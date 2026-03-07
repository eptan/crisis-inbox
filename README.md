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