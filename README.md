---
title: CrisisInbox
emoji: 📱
colorFrom: red
colorTo: yellow
sdk: docker
app_port: 8000
pinned: false
---

# CrisisInbox

A reinforcement learning environment built on [OpenEnv 0.2.1](https://github.com/OpenEnvs/OpenEnv) for training language models to manage personal task overload during natural disasters.

**Problem Statement 3.2** (Personalized Tasks) + **Patronus AI Sub-Theme** (Schema Drift)

**HF Space:** [eptan-crisis-inbox.hf.space](https://eptan-crisis-inbox.hf.space)

## The Problem

When disaster strikes, your phone explodes. Evacuation orders, panicked family texts, insurance deadlines, your boss demanding slides, your sister begging you to pick up her kids from school, your dad's heart medication left behind. Everything is urgent. Policies change mid-crisis. There are no clean answers — only tradeoffs.

CrisisInbox trains an agent to make those tradeoffs well.

## How It Works

The agent manages a **48-hour post-disaster inbox** as a working parent in Sacramento during a hurricane. 116 messages arrive in real time from 30+ senders across 6 channels. The agent must triage, respond, and adapt — while the rules keep changing underneath.

### Three Layers of Difficulty

**1. Cognitive Overload** — 116 messages arrive over 48 hours. Reading costs time (6 min). Responding costs more (15 min). The agent can't handle everything — it must prioritize and let some things slide.

**2. Conflicting Obligations** — Your boss says come in. HR says take emergency leave. Your sister needs you to watch her kids. Mom wants you to drive to Tahoe. The evacuation shelter is full. A wheelchair-bound neighbor is trapped. A baby down the street needs your generator. There's no right answer, only better tradeoffs.

**3. Scams & Misinformation** — Fake FEMA texts ask for your SSN. A contractor demands cash upfront. Social media says the dam is failing. The agent must recognize and deprioritize traps while acting on real emergencies.

**4. Schema Drift** — Mid-episode, the rules change:
- Insurance deadline shortened from 72h to 48h
- Evacuation zone expands to include your workplace
- Employer switches from "use PTO" to "5 days paid emergency leave"
- Airline extends free rebooking from 48h to 7 days
- FEMA adds new documentation requirements
- Shelter closes due to structural damage — relocate immediately
- County implements fuel rationing (odd/even plates)
- Multiple pharmacies close — prescription transfers needed
- Curfew extended from 9PM-6AM to 6PM-8AM due to looting

Each episode randomly fires 3 of 9 drift events. The agent receives no explicit flag — it must detect changes from message content alone and reprioritize.

### Sender Profiles

| Sender | Messages | Tone | Stakes |
|--------|----------|------|--------|
| Mom | 10 | Panicked, crying voicemails | Dad's heart medication, family safety |
| Sister | 9 | Desperate, grateful | Kids stranded at school, childcare |
| Emma (niece, 7) | 3 | Kid texting style | Scared in the dark, rainbow drawings |
| Boss (Greg) | 8 | Passive-aggressive, then softens | Career pressure vs. emergency |
| Neighbor Dave | 15 | Casual bro, community | Cat rescue, looting, generator, cleanup |
| Mrs. Chen (neighbor) | 3 | Frail, frightened | Wheelchair-bound, trapped by floodwater |
| FEMA / NWS / County | 19 | Formal, information-dense | Evacuation, shelters, curfew, mold |
| State Farm / GEICO | 9 | Corporate | Claim deadlines, vehicle damage |
| Scam / Misinfo senders | 3 | Urgent, suspicious | Fake FEMA, phishing, price gouging |
| Delta Airlines | 3 | Automated | Flight rebooking |
| Oakwood Elementary | 5 | School admin | Closures, virtual learning, devices |
| HR / EAP | 4 | Policy updates | Leave policies, crisis counseling |
| + 14 others | 25 | Various | Pharmacy, landlord, mutual aid, church, legal aid, etc. |

### Tools (Agent Actions)

| Tool | Time Cost | Description |
|------|-----------|-------------|
| `get_inbox` | 0h | View all arrived messages with metadata |
| `read_message` | 0.1h | Read full content of a specific message |
| `respond_to_message` | 0.25h | Take action on a message (earns reward) |
| `get_status` | 0h | View time, score, deadlines, drift events |
| `advance_time` | 0.5-4h | Skip forward (new messages may arrive) |
| `get_prompt` | 0h | Get formatted prompt for LLM training |

### Reward Function

| Signal | Weight | Mechanic |
|--------|--------|----------|
| **Format compliance** | 0-2 | Graduated credit for parseable output structure |
| **Urgency base** | 1-10 | Critical=10, High=5, Medium=3, Low=1 |
| **Deadline timing** | x0.25 to x1.5 | Earlier response = bigger bonus; late = 75% penalty |
| **Drift adaptation** | x1.5 | Bonus for handling drift messages (detected from content) |
| **Stale info penalty** | x0.5 | Penalty for acting on superseded information |
| **Response quality** | x0.5 | Penalty for very short/empty responses |
| **Prioritization** | x0.3 | Penalty for choosing low when critical exists |

### Episode Variation

Each episode has:
- 3 of 9 drift events randomly selected (seed-controlled)
- +/-15% jitter on message arrival times
- +/-10% jitter on deadlines
- Dependency chains that gate actions (e.g., must handle sister's request before school pickup confirmation)

## Quick Start (Hosted)

```python
from openenv import GenericEnvClient, GenericAction

with GenericEnvClient("https://eptan-crisis-inbox.hf.space", message_timeout_s=60.0).sync() as env:
    env.reset(seed=42)
    result = env.step(GenericAction(tool_name="get_inbox", arguments={}))
    print(result.observation)
```

## Training

Training uses **online GRPO** — the reward function calls `env.step()` on the live OpenEnv environment for each generated action, so rewards come directly from the environment's full game state (deadlines, drift events, superseded messages).

**Notebook:** [`notebooks/crisisinbox_grpo_northflank.ipynb`](notebooks/crisisinbox_grpo_northflank.ipynb) — Unsloth + HF TRL GRPO with LoRA (2x speedup)

**Training loop:**
1. Collect prompts from live environment episodes (varied seeds)
2. Model generates `respond_to_message(msg_id, response)` completions
3. For each completion, reset environment to the episode state and call `env.step()` to get the reward
4. Format compliance scored locally (graduated credit for parseable output)
5. GRPO updates the policy using relative reward rankings within each batch

Trains Qwen2.5-0.5B-Instruct with 200 steps, 16 generations per step, learning rate 1e-6.

## Deployment

```bash
# 1. Create and activate a virtual environment
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .

# 2. Deploy to HF Spaces via OpenEnv CLI
openenv push -r eptan/crisis-inbox
```

Or run locally:

```bash
source .venv/bin/activate
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

## Local Development

```bash
git clone https://github.com/eptan/crisis-inbox.git
cd crisis-inbox

python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .

# Run server
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

Test with the client:

```python
import json
from openenv import GenericEnvClient, GenericAction

with GenericEnvClient("http://localhost:8000", message_timeout_s=60.0).sync() as env:
    env.reset(seed=42)

    # View the inbox
    result = env.step(GenericAction(tool_name="get_inbox", arguments={}))
    inbox = result.observation.get("result", result.observation)
    print(json.dumps(inbox, indent=2))

    # Respond to a message
    result = env.step(GenericAction(
        tool_name="respond_to_message",
        arguments={
            "message_id": "msg_001",
            "response": "Evacuating to Lincoln High School immediately with documents and medication."
        }
    ))
    print(f"Reward: {result.reward}, Done: {result.done}")

    # Advance time and check status
    env.step(GenericAction(tool_name="advance_time", arguments={"hours": 4.0}))
    status = env.step(GenericAction(tool_name="get_status", arguments={}))
    print(status.observation)
```

## Repository Structure

```
crisis-inbox/
├── models.py                           # Message data model (Channel, Urgency, Message)
├── messages.py                         # 116 pre-written messages across 48h timeline
├── drift_events.py                     # 9 schema drift events (3 fire per episode)
├── client.py                           # GenericEnvClient helper
├── __init__.py                         # Package exports
├── server/
│   ├── crisis_inbox_environment.py     # OpenEnv Environment with timeline engine & rewards
│   ├── app.py                          # FastAPI app entry point
│   ├── demo_ui.py                      # HTML scenario overview at /demo
│   └── Dockerfile                      # HF Spaces deployment
├── notebooks/
│   └── crisisinbox_grpo_northflank.ipynb  # GRPO training (Unsloth LoRA)
├── pyproject.toml                      # Package config
├── openenv.yaml                        # OpenEnv environment spec
├── requirements.txt                    # Docker build dependencies
└── demo.py                            # Interactive demo script
```

## Stack

- **Environment:** OpenEnv 0.2.1 (Environment base class + GenericEnvClient)
- **Deployment:** HF Spaces (Docker)
- **Training:** Unsloth + HF TRL GRPO (LoRA, 2x speedup)
- **Model:** Qwen2.5-0.5B-Instruct

## Team

Built at the OpenEnv Hackathon @ Shack15, SF — March 7-8, 2026
