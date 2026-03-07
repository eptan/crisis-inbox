"""
Episode Generator for CrisisInbox
Connects to deployed HF Spaces environment and generates training episodes.
"""

import json
import sys
sys.path.insert(0, r'C:\Users\smrit\CascadeProjects\crisis-inbox-test')

from crisis_inbox import CrisisInboxEnv

def generate_episodes(num_episodes=50):
    """Generate episodes from the deployed environment."""
    episodes = []
    
    print(f"Connecting to HF Spaces environment...")
    
    # Connect to deployed environment
    with CrisisInboxEnv(base_url="https://eptan-crisis-inbox.hf.space") as env:
        print(f"✓ Connected to environment")
        
        for i in range(num_episodes):
            print(f"Generating episode {i+1}/{num_episodes}...", end=" ")
            
            # Reset environment to get new episode
            env.reset()
            
            # Get inbox
            inbox = env.call_tool("get_inbox")
            
            # Convert to training format
            episode = convert_to_training_format(inbox, episode_id=f"ep_{i:03d}")
            episodes.append(episode)
            
            print(f"✓ ({len(episode['messages'])} messages)")
    
    return episodes

def convert_to_training_format(inbox_json, episode_id):
    """Convert environment inbox JSON to training episode format."""
    
    # Parse JSON string
    inbox_data = json.loads(inbox_json)
    
    messages = []
    critical_ids = []
    deadlines = {}
    tasks = {}
    schema_events = []
    
    for msg_data in inbox_data:
        msg_id = msg_data.get('id')
        
        message = {
            "id": msg_id,
            "sender": msg_data.get('sender', 'Unknown'),
            "channel": msg_data.get('channel', 'email'),
            "content": msg_data.get('subject', ''),
            "time": msg_data.get('timestamp_hours', 0),
            "type": map_urgency_to_type(msg_data.get('urgency', 'medium')),
        }
        
        # Add deadline if exists
        if msg_data.get('deadline_hours'):
            message["deadline"] = msg_data['deadline_hours']
            task_id = f"task_{msg_id}"
            deadlines[task_id] = msg_data['deadline_hours']
            tasks[task_id] = {
                "category": message["type"],
                "sender": message["sender"]
            }
        
        # Mark critical messages
        if msg_data.get('urgency') in ['critical', 'high']:
            critical_ids.append(msg_id)
        
        # Check for schema drift
        if msg_data.get('drift_flag'):
            schema_events.append({
                "time": message["time"],
                "kind": "policy_change",
                "new_value": "updated"
            })
        
        messages.append(message)
    
    episode = {
        "messages": messages,
        "critical_ids": critical_ids,
        "deadlines": deadlines,
        "tasks": tasks,
        "schema_events": schema_events,
        "ideal_tone_map": infer_tone_map(messages),
        "episode_id": episode_id
    }
    
    return episode

def map_urgency_to_type(urgency):
    """Map environment urgency to training type."""
    mapping = {
        'critical': 'safety',
        'high': 'admin',
        'medium': 'work',
        'low': 'social'
    }
    return mapping.get(urgency, 'work')

def infer_tone_map(messages):
    """Infer ideal tone for each sender."""
    tone_map = {}
    
    for msg in messages:
        sender = msg['sender']
        if sender not in tone_map:
            # Simple heuristics
            if sender in ['FEMA', 'Insurance', 'School']:
                tone_map[sender] = 'factual'
            elif sender in ['Mom', 'Dad', 'Sister', 'Spouse']:
                tone_map[sender] = 'warm'
            elif sender in ['Boss', 'Employer']:
                tone_map[sender] = 'professional'
            else:
                tone_map[sender] = 'casual'
    
    return tone_map

def save_episodes(episodes, filename='episodes.json'):
    """Save episodes to JSON file."""
    with open(filename, 'w') as f:
        json.dump(episodes, f, indent=2)
    print(f"\n✓ Saved {len(episodes)} episodes to {filename}")

if __name__ == "__main__":
    # Generate 50 episodes for training
    episodes = generate_episodes(num_episodes=50)
    save_episodes(episodes)
    
    # Also save a sample for testing
    save_episodes(episodes[:5], 'sample_episodes.json')
    print(f"✓ Saved 5 sample episodes to sample_episodes.json")
