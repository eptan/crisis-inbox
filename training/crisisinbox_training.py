"""
CrisisInbox GRPO Training Script
Person B: ML Pipeline

Run this in Google Colab:
1. Upload this file
2. Upload episodes.json from repo
3. Run: python crisisinbox_training.py
"""

import torch
import re
import json
import numpy as np
from datasets import Dataset
from unsloth import FastLanguageModel
from trl import GRPOConfig, GRPOTrainer

# Download episodes from GitHub repo
print("Loading episodes...")
import urllib.request
urllib.request.urlretrieve(
    "https://raw.githubusercontent.com/eptan/crisis-inbox/main/episodes.json",
    "episodes.json"
)

with open("episodes.json", "r") as f:
    EPISODES = json.load(f)

print(f"✓ Loaded {len(EPISODES)} episodes")

# =============================================================================
# PROMPT BUILDING
# =============================================================================

CRISIS_SYSTEM_PROMPT = """
You are an assistant helping a working parent during a wildfire.
You must triage messages, act on safety-critical items first,
respect deadlines, adapt to policy changes, and write appropriate
tones to different people.

Respond ONLY in this format:
<plan>
1. [time=min X] ACTION_DESCRIPTION
2. [time=min Y] ACTION_DESCRIPTION
...
</plan>
"""

def build_crisis_prompt(episode):
    """Build prompt from episode data."""
    msgs_str = []
    for m in episode.get("messages", []):
        deadline_info = f" (DEADLINE: {m['deadline']}h)" if m.get("deadline") else ""
        urgency = "🔴 URGENT" if m.get("type") == "safety" else ""
        msgs_str.append(
            f"[t={m['time']}h] {urgency} From {m['sender']} via {m['channel']}: {m['content']}{deadline_info}"
        )
    
    drift_str = []
    for d in episode.get("schema_events", []):
        drift_str.append(f"[t={d['time']}h] POLICY UPDATE: {d['kind']} -> {d.get('new_value', 'changed')}")
    
    user_content = (
        "Here is your 48-hour message history:\n\n"
        + "\n".join(msgs_str)
        + "\n\nPolicy changes observed:\n"
        + ("\n".join(drift_str) if drift_str else "None yet.")
        + "\n\nDecide what to do in order. Remember the required <plan> format."
    )
    
    return [
        {"role": "system", "content": CRISIS_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

# =============================================================================
# PLAN PARSER
# =============================================================================

def parse_plan(model_output):
    """Parse <plan> tag output into list of action dicts."""
    actions = []
    
    plan_match = re.search(r'<plan>(.*?)</plan>', model_output, re.DOTALL | re.IGNORECASE)
    if not plan_match:
        return []
    
    plan_content = plan_match.group(1).strip()
    
    lines = plan_content.split('\n')
    for line in lines:
        line = line.strip()
        if not line or not line[0].isdigit():
            continue
        
        # Extract time: [time=min X]
        time_match = re.search(r'time=min (\d+)', line)
        time_min = int(time_match.group(1)) if time_match else 0
        
        # Extract action description
        action_desc = line.split(']', 1)[1].strip() if ']' in line else line
        
        # Infer target
        target = "unknown"
        common_targets = ["spouse", "boss", "mom", "dad", "sister", "neighbor", "FEMA", "Insurance", "Airline", "School"]
        for t in common_targets:
            if t.lower() in action_desc.lower():
                target = t
                break
        
        actions.append({
            "time_min": time_min,
            "action": action_desc,
            "target": target,
            "task_id": None
        })
    
    return actions

# =============================================================================
# 5-COMPONENT REWARD FUNCTION
# =============================================================================

W_SAFETY   = 1.5
W_DEADLINE = 1.5
W_DRIFT    = 1.0
W_TONE     = 0.5
W_COVER    = 1.0

def score_safety_priority(episode, parsed_actions):
    """+10 if safety in first 3 actions, -10 if ignored."""
    safety_tasks = [t_id for t_id, t in episode.get("tasks", {}).items() 
                    if t.get("category") == "safety"]
    
    acted_tasks = set()
    for a in parsed_actions:
        for t_id, t_info in episode.get("tasks", {}).items():
            if a.get("target", "").lower() in t_info.get("sender", "").lower():
                a["task_id"] = t_id
                acted_tasks.add(t_id)
                break
    
    score = 0.0
    first_three_targets = [a.get("target", "").lower() for a in parsed_actions[:3]]
    safety_targets = [episode["tasks"][t]["sender"].lower() for t in safety_tasks]
    
    if any(t in first_three_targets for t in safety_targets):
        score += 10.0
    
    safety_acted = acted_tasks.intersection(set(safety_tasks))
    if not safety_acted and safety_tasks:
        score -= 10.0
    
    return score

def score_deadlines(episode, parsed_actions):
    """+5 before deadline, -5 after/missed."""
    score = 0.0
    completion_time = {}
    
    for a in parsed_actions:
        for t_id, t_info in episode.get("tasks", {}).items():
            if a.get("target", "").lower() in t_info.get("sender", "").lower():
                if t_id not in completion_time:
                    completion_time[t_id] = a["time_min"] / 60.0
                break
    
    for t_id, deadline in episode.get("deadlines", {}).items():
        if t_id in completion_time:
            if completion_time[t_id] <= deadline:
                score += 5.0
            else:
                score -= 5.0
        else:
            score -= 5.0
    
    return score

def score_schema_drift(episode, parsed_actions):
    """+10 for adapting to policy changes."""
    score = 0.0
    
    for event in episode.get("schema_events", []):
        event_time = event["time"]
        event_kind = event.get("kind", "")
        
        actions_after = [a for a in parsed_actions if a["time_min"] / 60.0 > event_time]
        
        if not actions_after:
            continue
        
        if "insurance_deadline_change" in event_kind:
            new_deadline = event.get("new_value", 72)
            old_deadline = event.get("old_value", 72)
            
            insurance_actions = [a for a in actions_after 
                               if "insurance" in a.get("action", "").lower()]
            
            for a in insurance_actions:
                action_hour = a["time_min"] / 60.0
                if action_hour <= new_deadline:
                    score += 10.0
                elif action_hour > old_deadline:
                    score -= 10.0
                else:
                    score -= 5.0
    
    return score

def score_tone(episode, model_raw_output):
    """Simple tone heuristics."""
    score = 0.0
    text = model_raw_output.lower()
    
    if "dear" in text or "sincerely" in text or "regards" in text:
        score += 1.0
    
    if "love you" in text or "i'm so sorry" in text or "worried" in text:
        score += 1.0
    
    if "confirm" in text or "verified" in text or "documentation" in text:
        score += 1.0
    
    return score

def score_coverage(episode, parsed_actions):
    """+2 per task touched, -1 per ignored."""
    described_tasks = set(episode.get("tasks", {}).keys())
    
    acted_tasks = set()
    for a in parsed_actions:
        for t_id, t_info in episode.get("tasks", {}).items():
            if a.get("target", "").lower() in t_info.get("sender", "").lower():
                acted_tasks.add(t_id)
                break
    
    score = 0.0
    for t_id in described_tasks:
        if t_id in acted_tasks:
            score += 2.0
        else:
            score -= 1.0
    
    return score

def total_reward(episode, model_raw_output):
    """Calculate total reward from 5 components."""
    parsed_actions = parse_plan(model_raw_output)
    
    if not parsed_actions:
        return -20.0
    
    r_safety   = score_safety_priority(episode, parsed_actions)
    r_deadline = score_deadlines(episode, parsed_actions)
    r_drift    = score_schema_drift(episode, parsed_actions)
    r_tone     = score_tone(episode, model_raw_output)
    r_cover    = score_coverage(episode, parsed_actions)
    
    total = (
        W_SAFETY   * r_safety +
        W_DEADLINE * r_deadline +
        W_DRIFT    * r_drift +
        W_TONE     * r_tone +
        W_COVER    * r_cover
    )
    
    return total

# =============================================================================
# GRPO TRAINING SETUP
# =============================================================================

def build_dataset(episodes):
    rows = []
    for idx, ep in enumerate(episodes):
        prompt = build_crisis_prompt(ep)
        rows.append({
            "id": idx,
            "prompt": prompt,
            "episode": ep,
        })
    return Dataset.from_list(rows)

print("Building dataset...")
crisis_dataset = build_dataset(EPISODES)
print(f"✓ Built dataset with {len(crisis_dataset)} episodes")

# Load model
print("Loading model...")
MODEL_NAME = "unsloth/Qwen2.5-0.5B-Instruct"

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
)

print(f"✓ Loaded model: {MODEL_NAME}")

# Reward function
EPISODES_LIST = [row["episode"] for row in crisis_dataset]

def crisis_reward_fn(prompts, completions, **kwargs):
    rewards = []
    
    for prompt, completion in zip(prompts, completions):
        episode = None
        for ep in EPISODES_LIST:
            test_prompt = build_crisis_prompt(ep)
            if test_prompt[1]["content"] == prompt[1]["content"]:
                episode = ep
                break
        
        if episode is None:
            idx = kwargs.get("episode_idx", 0)
            episode = EPISODES_LIST[idx % len(EPISODES_LIST)]
        
        reward = total_reward(episode, completion)
        rewards.append(float(reward))
    
    return rewards

# Training config
training_args = GRPOConfig(
    use_vllm=True,
    vllm_mode="colocate",
    num_train_epochs=3,
    max_steps=200,  # Start with 200 for test
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    num_generations=4,
    max_completion_length=512,
    temperature=0.7,
    learning_rate=1e-5,
    logging_steps=10,
    save_steps=50,
    output_dir="./crisisinbox_grpo",
    report_to="none",
)

trainer = GRPOTrainer(
    model=model,
    processing_class=tokenizer,
    reward_funcs=crisis_reward_fn,
    train_dataset=crisis_dataset,
    args=training_args,
)

print("✓ GRPO Trainer ready")

# =============================================================================
# TRAINING RUN
# =============================================================================

print("🚀 Starting CrisisInbox GRPO Training...")
print("This will take 1-4 hours depending on max_steps\n")

trainer.train()

print("\n✅ Training completed!")

# =============================================================================
# SAVE RESULTS
# =============================================================================

model.save_pretrained("./crisisinbox_model_final")
tokenizer.save_pretrained("./crisisinbox_model_final")
print("✓ Model saved")

# Generate demo examples
DEMO_EXAMPLES = []
for ep in EPISODES[:3]:
    prompt = build_crisis_prompt(ep)
    text = tokenizer.apply_chat_template(prompt, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=200, temperature=0.7)
    response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    
    reward = total_reward(ep, response)
    DEMO_EXAMPLES.append({
        "episode_id": ep["episode_id"],
        "response": response,
        "reward": reward,
        "parsed_actions": parse_plan(response)
    })

with open("demo_examples_trained.json", "w") as f:
    json.dump(DEMO_EXAMPLES, f, indent=2)

print(f"✓ Saved {len(DEMO_EXAMPLES)} demo examples")
