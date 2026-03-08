"""
Episode Generator for CrisisInbox GRPO Training.

Generates training episodes locally (no server needed) by simulating the
environment and capturing inbox snapshots at key decision points.

Each episode produces multiple training prompts — one per decision point —
where the model must choose which message to handle next.

Output format (per episode):
{
  "episode_id": "ep_000",
  "seed": 42,
  "total_messages": 73,
  "drift_events": ["drift_insurance", "drift_evacuation", "drift_fema"],
  "decision_points": [
    {
      "hour": 0.0,
      "prompt": "...",           # full text prompt for the LLM
      "visible_messages": [...], # inbox snapshot
      "handled_ids": [],
      "pending_deadlines": [...],
      "drift_events_fired": []
    },
    ...
  ]
}
"""

import json
import random
from typing import Any

from models import Channel, Message, Urgency
from messages import ALL_MESSAGES
from drift_events import ALL_DRIFT_EVENTS, DriftEvent, select_drift_events


SYSTEM_PROMPT = """You are managing a personal crisis inbox during a post-hurricane evacuation in Sacramento. You are a working parent with 48 hours to triage incoming messages from family, employer, government, insurance, and service providers.

Rules:
- Reading a message costs 0.1 hours (6 minutes)
- Responding to a message costs 0.25 hours (15 minutes)
- You cannot handle everything — prioritize wisely
- Safety-critical messages (evacuations, medical) should come first
- Watch for policy changes that supersede earlier information
- Some messages have dependencies that must be handled first
- Deadlines are real — missing them reduces your score

Available actions:
- respond_to_message(message_id, response) — handle a message
- advance_time(hours) — skip forward to see new messages
- get_status() — check time, score, deadlines"""


def build_episode(seed: int) -> dict[str, Any]:
    """Build a single training episode with decision-point snapshots."""
    rng = random.Random(seed)

    # Select drift events
    drift_events = select_drift_events(count=3, rng=rng)
    drift_event_ids = [d.id for d in drift_events]

    # Collect drift message IDs
    selected_drift_msg_ids = set()
    for drift in drift_events:
        for msg in drift.messages:
            selected_drift_msg_ids.add(msg.id)

    all_drift_msg_ids = set()
    for drift in ALL_DRIFT_EVENTS:
        for msg in drift.messages:
            all_drift_msg_ids.add(msg.id)

    # Build message pool with jitter
    all_messages = []
    for msg in ALL_MESSAGES:
        if msg.id in all_drift_msg_ids and msg.id not in selected_drift_msg_ids:
            continue
        m = msg.model_copy()
        if m.timestamp_hours > 0:
            jitter = rng.uniform(-0.15, 0.15) * m.timestamp_hours
            m.timestamp_hours = round(max(0.1, min(47.5, m.timestamp_hours + jitter)), 2)
        if m.deadline_hours is not None and m.deadline_hours > 0:
            d_jitter = rng.uniform(-0.1, 0.1) * m.deadline_hours
            m.deadline_hours = round(max(m.timestamp_hours + 0.5, min(72.0, m.deadline_hours + d_jitter)), 2)
        all_messages.append(m)

    # Also add drift event messages
    for drift in drift_events:
        for msg in drift.messages:
            if not any(m.id == msg.id for m in all_messages):
                all_messages.append(msg)

    # Sort all messages by arrival time
    all_messages.sort(key=lambda m: m.timestamp_hours)

    # Track superseded messages
    superseded = {}
    for drift in drift_events:
        for old_id in drift.superseded_msg_ids:
            for dmsg in drift.messages:
                if dmsg.supersedes == old_id:
                    superseded[old_id] = dmsg.id

    # Simulate the episode at key time points to capture decision snapshots
    decision_hours = [0.0, 2.0, 6.0, 10.0, 14.0, 18.0]
    # Add drift trigger hours
    for drift in drift_events:
        decision_hours.append(drift.trigger_hour)
        decision_hours.append(drift.trigger_hour + 1.0)
    # Add late-game hours
    decision_hours.extend([28.0, 34.0, 40.0, 44.0, 47.0])
    decision_hours = sorted(set(decision_hours))

    decision_points = []
    fired_drifts = set()

    for hour in decision_hours:
        if hour > 48.0:
            continue

        # Deliver messages visible at this hour
        visible = [m for m in all_messages if m.timestamp_hours <= hour]

        # Fire drift events
        newly_fired = []
        for drift in drift_events:
            if drift.id not in fired_drifts and hour >= drift.trigger_hour:
                fired_drifts.add(drift.id)
                newly_fired.append(drift.id)

        # Build inbox summary
        visible_summaries = []
        for msg in visible:
            is_superseded = msg.id in superseded
            summary = {
                "id": msg.id,
                "sender": msg.sender,
                "subject": msg.subject,
                "content": msg.content,
                "urgency": msg.urgency.value,
                "channel": msg.channel.value,
                "timestamp_hours": msg.timestamp_hours,
                "deadline_hours": msg.deadline_hours,
                "dependencies": msg.dependencies,
                "drift_flag": msg.drift_flag,
                "superseded": is_superseded,
            }
            visible_summaries.append(summary)

        # Identify pending deadlines
        pending_deadlines = []
        for msg in visible:
            if msg.deadline_hours is not None:
                remaining = msg.deadline_hours - hour
                if remaining > 0:
                    pending_deadlines.append({
                        "id": msg.id,
                        "subject": msg.subject,
                        "urgency": msg.urgency.value,
                        "hours_remaining": round(remaining, 1),
                    })
                elif remaining > -2:  # recently expired
                    pending_deadlines.append({
                        "id": msg.id,
                        "subject": msg.subject,
                        "urgency": msg.urgency.value,
                        "hours_remaining": round(remaining, 1),
                        "expired": True,
                    })

        # Build the text prompt
        prompt = format_prompt(hour, visible_summaries, pending_deadlines, list(fired_drifts))

        decision_points.append({
            "hour": hour,
            "prompt": prompt,
            "visible_count": len(visible),
            "visible_messages": visible_summaries,
            "pending_deadlines": pending_deadlines,
            "drift_events_fired": list(fired_drifts),
            "newly_fired_drifts": newly_fired,
        })

    return {
        "episode_id": f"ep_{seed:03d}",
        "seed": seed,
        "total_messages": len(all_messages),
        "drift_events": drift_event_ids,
        "superseded_messages": superseded,
        "decision_points": decision_points,
    }


def format_prompt(hour: float, messages: list, deadlines: list, fired_drifts: list,
                  max_messages: int = 20) -> str:
    """Format an inbox state into a text prompt for the LLM.

    Only the top `max_messages` unhandled messages are shown (by urgency then
    deadline), keeping prompts within ~1500 tokens for small-model training.
    """
    lines = [SYSTEM_PROMPT, ""]
    lines.append(f"CURRENT TIME: Hour {hour:.1f} of 48 ({48 - hour:.1f} hours remaining)")
    lines.append(f"MESSAGES IN INBOX: {len(messages)}")
    lines.append("")

    # Show urgent deadlines first
    urgent = [d for d in deadlines if not d.get("expired") and d["hours_remaining"] < 4]
    expired = [d for d in deadlines if d.get("expired")]
    if urgent:
        lines.append("URGENT DEADLINES:")
        for d in sorted(urgent, key=lambda x: x["hours_remaining"]):
            lines.append(f"  ! {d['subject']} — {d['hours_remaining']}h left [{d['urgency']}]")
        lines.append("")
    if expired:
        lines.append("EXPIRED DEADLINES:")
        for d in expired:
            lines.append(f"  x {d['subject']} — expired {abs(d['hours_remaining']):.1f}h ago")
        lines.append("")

    if fired_drifts:
        lines.append(f"POLICY CHANGES DETECTED: {len(fired_drifts)}")
        lines.append("")

    # Prioritize unhandled messages by urgency then deadline
    urgency_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    ranked = sorted(messages, key=lambda m: (
        urgency_order.get(m["urgency"], 4),
        0 if m.get("drift_flag") else 1,
        m.get("deadline_hours") or 999,
    ))
    shown = ranked[:max_messages]
    omitted = len(messages) - len(shown)

    # Group shown messages by urgency
    by_urgency = {"critical": [], "high": [], "medium": [], "low": []}
    for msg in shown:
        by_urgency.get(msg["urgency"], by_urgency["low"]).append(msg)

    for level in ["critical", "high", "medium", "low"]:
        msgs = by_urgency[level]
        if msgs:
            lines.append(f"--- {level.upper()} ({len(msgs)}) ---")
            for msg in msgs:
                stale = " [STALE]" if msg.get("superseded") else ""
                drift = " [POLICY CHANGE]" if msg.get("drift_flag") else ""
                deadline = f" (due h{msg['deadline_hours']})" if msg.get("deadline_hours") else ""
                deps = f" [requires: {', '.join(msg['dependencies'])}]" if msg.get("dependencies") else ""
                lines.append(f"  [{msg['id']}] {msg['sender']}: {msg['subject']}{deadline}{stale}{drift}{deps}")
                # Show content preview (first 120 chars)
                preview = msg["content"][:120].replace("\n", " ")
                if len(msg["content"]) > 120:
                    preview += "..."
                lines.append(f"    > {preview}")
            lines.append("")

    if omitted > 0:
        lines.append(f"  ({omitted} lower-priority messages not shown)")
        lines.append("")

    lines.append("Which message should you handle next? Respond with respond_to_message(message_id, response).")
    return "\n".join(lines)


def generate_episodes(num_episodes: int = 50, start_seed: int = 1000) -> list:
    """Generate multiple training episodes with different seeds."""
    episodes = []
    for i in range(num_episodes):
        seed = start_seed + i
        print(f"  Episode {i + 1}/{num_episodes} (seed={seed})...", end=" ")
        episode = build_episode(seed)
        # Some episodes may not have decision points; skip them.
        decision_points = episode.get("decision_points")
        if not decision_points:
            print("skipped (no decision_points)")
            continue
        n_dp = len(decision_points)
        n_msg = episode["total_messages"]
        drifts = ", ".join(episode["drift_events"])
        print(f"{n_msg} messages, {n_dp} decision points, drifts: [{drifts}]")
        episodes.append(episode)
    return episodes


def save_episodes(episodes: list, filename: str = "episodes.json"):
    """Save episodes to JSON file."""
    with open(filename, "w") as f:
        json.dump(episodes, f, indent=2)
    total_prompts = sum(len(ep.get("decision_points", [])) for ep in episodes)
    print(f"\nSaved {len(episodes)} episodes ({total_prompts} training prompts) to {filename}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate CrisisInbox training episodes")
    parser.add_argument("-n", "--num-episodes", type=int, default=50, help="Number of episodes")
    parser.add_argument("-s", "--start-seed", type=int, default=1000, help="Starting seed")
    parser.add_argument("-o", "--output", type=str, default="episodes.json", help="Output file")
    parser.add_argument("--sample", type=int, default=5, help="Also save N sample episodes")
    args = parser.parse_args()

    print(f"Generating {args.num_episodes} episodes (seeds {args.start_seed}-{args.start_seed + args.num_episodes - 1})...")
    episodes = generate_episodes(args.num_episodes, args.start_seed)
    save_episodes(episodes, args.output)

    if args.sample > 0:
        sample_file = "sample_episodes.json"
        save_episodes(episodes[:args.sample], sample_file)
