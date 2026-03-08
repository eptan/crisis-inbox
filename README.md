---
title: CrisisInbox
emoji: 📱
colorFrom: red
colorTo: yellow
sdk: docker
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

The agent manages a **48-hour post-disaster inbox** as a working parent in Sacramento during a hurricane. Messages arrive in real time from 19 senders across 6 channels. The agent must triage, respond, and adapt — while the rules keep changing underneath.

### Three Layers of Difficulty

**1. Cognitive Overload** — 76 messages arrive over 48 hours. Reading costs time (6 min). Responding costs more (15 min). The agent can't handle everything — it must prioritize and let some things slide.

**2. Conflicting Obligations** — Your boss says come in. HR says take emergency leave. Your sister needs you to watch her kids. Mom wants you to drive to Tahoe. The evacuation shelter is full. There's no right answer, only better tradeoffs.

**3. Schema Drift** — Mid-episode, the rules change:
- Insurance deadline shortened from 72h to 48h
- Evacuation zone expands to include your workplace
- Employer switches from "use PTO" to "5 days paid emergency leave"
- Airline extends free rebooking from 48h to 7 days
- FEMA adds new documentation requirements

Each episode randomly fires 3 of 5 drift events. The agent must detect changes and reprioritize.

### Sender Profiles

| Sender | Messages | Tone | Stakes |
|--------|----------|------|--------|
| Mom | 8 | Panicked, crying voicemails | Dad's heart medication, family safety |
| Sister | 7 | Desperate, grateful | Kids stranded at school, childcare |
| Emma (niece, 7) | 3 | Kid texting style | Scared in the dark, rainbow drawings |
| Boss (Greg) | 5 | Passive-aggressive, then softens | Career pressure vs. emergency |
| Neighbor Dave | 8 | Casual bro, community | Cat rescue, looting, cleanup |
| FEMA / NWS | 10 | Formal, information-dense | Evacuation orders, shelter locations |
| State Farm | 5 | Corporate | Claim deadlines, documentation |
| Delta Airlines | 3 | Automated | Flight rebooking |
| Oakwood Elementary | 3 | School admin | Closures, virtual learning |
| HR Department | 3 | Policy updates | Leave policies |
| + 9 others | 21 | Various | Pharmacy, landlord, utilities, etc. |

### MCP Tools (Agent Actions)

| Tool | Time Cost | Description |
|------|-----------|-------------|
| `get_inbox` | 0h | View all arrived messages with metadata |
| `read_message` | 0.1h | Read full content of a specific message |
| `respond_to_message` | 0.25h | Take action on a message (earns reward) |
| `get_status` | 0h | View time, score, deadlines, drift events |
| `advance_time` | 0.5-4h | Skip forward (new messages may arrive) |

### Reward Function

| Signal | Weight | Mechanic |
|--------|--------|----------|
| **Urgency base** | 1-10 | Critical=10, High=5, Medium=3, Low=1 |
| **Deadline timing** | x0.25 to x1.5 | Earlier response = bigger bonus; late = 75% penalty |
| **Drift adaptation** | x1.5 | Bonus for handling drift-flagged messages |
| **Stale info penalty** | x0.5 | Penalty for acting on superseded information |
| **Response quality** | x0.5 | Penalty for very short/empty responses |

An optimal agent responding to the critical evacuation alert at hour 0 earns 15 points. The same response at hour 10 (after the 6h deadline) earns only 2.5.

### Episode Variation

Each episode has:
- 3 of 5 drift events randomly selected (seed-controlled)
- +/-15% jitter on message arrival times
- +/-10% jitter on deadlines
- Dependency chains that gate actions (e.g., must handle sister's request before school pickup confirmation)

## Quick Start (Hosted)

```python
from crisis_inbox import CrisisInboxEnv

with CrisisInboxEnv(base_url="https://eptan-crisis-inbox.hf.space") as env:
    env.reset()
    inbox = env.call_tool("get_inbox")
    print(inbox)
```

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
from crisis_inbox import CrisisInboxEnv

with CrisisInboxEnv(base_url="http://localhost:8000") as env:
    env.reset()

    # View the inbox
    inbox = env.call_tool("get_inbox")
    print(inbox)

    # Read a message
    msg = env.call_tool("read_message", message_id="msg_001")
    print(msg)

    # Respond to it
    result = env.call_tool("respond_to_message",
        message_id="msg_001",
        response="Evacuating to Lincoln High School immediately with documents and medication.")
    print(result)

    # Advance time and check status
    env.call_tool("advance_time", hours=4.0)
    status = env.call_tool("get_status")
    print(status)
```

## Repository Structure

```
crisis-inbox/
├── models.py                           # Message data model (Channel, Urgency, Message)
├── messages.py                         # 76 pre-written messages across 48h timeline
├── drift_events.py                     # 5 schema drift events (3 fire per episode)
├── client.py                           # MCPToolClient subclass
├── __init__.py                         # Package exports
├── server/
│   ├── crisis_inbox_environment.py     # MCPEnvironment with timeline engine
│   ├── app.py                          # FastAPI app with MCPAction workaround
│   └── Dockerfile                      # HF Spaces deployment
├── notebooks/
│   └── crisisinbox_grpo_simple.ipynb   # GRPO training notebook (Colab)
├── .episodes.json                      # Pre-generated training episodes (gitignored)
├── generate_episodes.py                # Episode generator script
├── pyproject.toml                      # Package config
├── openenv.yaml                        # OpenEnv environment spec
├── requirements.txt                    # Docker build dependencies
└── ROADMAP.md                          # Hackathon timeline and progress
```

## Stack

- **Environment:** OpenEnv 0.2.1 (MCPEnvironment + FastMCP)
- **Deployment:** HF Spaces (Docker)
- **Training:** Unsloth GRPO via Google Colab
- **Model:** Qwen2.5-0.5B-Instruct

### GRPO training (Colab)

Open the notebook with the latest fixes (context length, reward signature, left-padding, batch size) in Google Colab (T4 GPU runtime):

**[Open in Colab](https://colab.research.google.com/github/eptan/crisis-inbox/blob/main/notebooks/crisisinbox_grpo_simple.ipynb)**

Push your local changes to the `main` branch so the link above serves the updated notebook.

## Team

Built at the OpenEnv Hackathon @ Shack15, SF — March 7-8, 2026
