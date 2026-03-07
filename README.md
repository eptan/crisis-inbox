# CrisisInbox

An reinforcement learning environment built on OpenEnv 0.2.1 for training language models to manage personal task overload during natural disasters.

## The Problem

When disaster strikes, people are overwhelmed with competing demands — evacuation alerts, insurance deadlines, employer communications, family coordination, travel rebooking — all arriving simultaneously with shifting rules and shrinking timelines. Most people make poor decisions under this cognitive load, missing critical deadlines and deprioritizing safety.

## The Environment

CrisisInbox simulates a 48-hour post-disaster scenario where an agent must triage and respond to a stream of messages across multiple channels. The environment features:

- **Realistic message streams** from family, employers, government agencies, insurance companies, and service providers
- **Conflicting obligations** with no clean solutions — forcing genuine prioritization
- **Schema drift** — policies, deadlines, and rules change mid-episode (evacuation zones expand, insurance requirements update, employer policies shift)
- **Dependency chains** — some actions require completing prerequisites first
- **Cognitive overload** — more tasks arrive than can be handled, requiring strategic triage

## Reward Function

Multi-signal reward based on: safety prioritization, deadline compliance, schema drift adaptation, tone appropriateness, and task coverage.

## Quick Start (Hosted)

Connect to the deployed environment on HF Spaces — no local setup needed:

```python
from crisis_inbox import CrisisInboxEnv

with CrisisInboxEnv(base_url="https://eptan-crisis-inbox.hf.space") as env:
    env.reset()
    inbox = env.call_tool("get_inbox")
    print(inbox)
```

## Local Development

### Prerequisites

- Python 3.10+

### Setup

```bash
git clone https://github.com/eptan/crisis-inbox.git
cd crisis-inbox

python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

### Run the server

```bash
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

The API docs will be available at http://localhost:8000/docs.

### Test with the client

```python
from crisis_inbox import CrisisInboxEnv

with CrisisInboxEnv(base_url="http://localhost:8000") as env:
    env.reset()

    # List available tools
    tools = env.list_tools()
    for t in tools:
        print(f"  {t.name}: {t.description[:60]}")

    # View the inbox
    inbox = env.call_tool("get_inbox")
    print(inbox)

    # Read a specific message
    msg = env.call_tool("read_message", message_id="msg_001")
    print(msg)

    # Respond to a message
    result = env.call_tool("respond_to_message",
        message_id="msg_001",
        response="Evacuating to Lincoln High School immediately.")
    print(result)

    # Check progress
    status = env.call_tool("get_status")
    print(status)
```

## Stack

- **Environment:** OpenEnv 0.2.1 deployed on HF Spaces
- **Training:** Unsloth GRPO via Google Colab
- **Problem Statement:** 3.2 (Personalized Tasks) + Patronus AI Sub-Theme (Schema Drift)

## Team

Built at the OpenEnv Hackathon, March 7-8, 2026

---

## Training the Model (Person B)

### Quick Start in Google Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eptan/crisis-inbox/blob/main/notebooks/crisisinbox_grpo.ipynb)

### Steps to Train

1. **Open the notebook in Colab**
   ```
   https://colab.research.google.com/github/eptan/crisis-inbox/blob/main/notebooks/crisisinbox_grpo.ipynb
   ```

2. **Set runtime to GPU**
   - Runtime → Change runtime type → Hardware accelerator: GPU (T4)

3. **Run all cells**
   - The notebook automatically downloads episodes.json from this repo
   - Loads Qwen2.5-0.5B-Instruct model
   - Starts GRPO training

4. **Monitor training**
   - Watch for upward reward curve
   - 200 steps = ~1 hour on T4 GPU
   - 500 steps = ~3 hours (recommended for full training)

5. **Save results**
   - Model saved to `./crisisinbox_model_final/`
   - Demo examples saved to `demo_examples_trained.json`
   - Upload model to Hugging Face Hub for demo

### Training Configuration

```python
# GRPO Settings
max_steps = 200-500
per_device_train_batch_size = 2
num_generations = 4  # GRPO group size
learning_rate = 1e-5

# 5-Component Reward Weights
W_SAFETY   = 1.5  # Safety priority (+10/-10)
W_DEADLINE = 1.5  # Deadline compliance (+5/-5)
W_DRIFT    = 1.0  # Schema drift adaptation (+10/-10)
W_TONE     = 0.5  # Tone appropriateness (+3)
W_COVER    = 1.0  # Task coverage (+2/-1)
```

### Episode Generation

To generate new training episodes from the environment:

```bash
pip install -e .
python generate_episodes.py
```

This connects to the HF Spaces deployment and generates `episodes.json`.

---

## Repository Structure

```
crisis-inbox/
├── README.md                    # This file
├── episodes.json               # 50 training episodes (auto-generated)
├── sample_episodes.json        # 5 sample episodes
├── generate_episodes.py        # Episode generator script
├── notebooks/
│   └── crisisinbox_grpo.ipynb # GRPO training notebook
├── crisis_inbox/               # Environment package
│   ├── __init__.py
│   ├── client.py               # Environment client
│   └── models.py               # Data models
├── server/                     # OpenEnv server
│   └── app.py
├── pyproject.toml             # Package config
└── openenv.yaml               # Environment spec
```