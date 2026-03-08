#!/usr/bin/env python3
"""
CrisisInbox Demo Display

Runs a full episode with color-coded urgency levels, drift event
notifications, and agent action visualization. Designed for the
3-minute hackathon demo.

Usage:
    python demo.py                    # Run against local server
    python demo.py --remote           # Run against HF Spaces
    python demo.py --strategy smart   # Use smart triage (default)
    python demo.py --strategy naive   # Use naive arrival-order strategy
"""

import argparse
import json
import sys
import time

from server.crisis_inbox_environment import CrisisInboxEnvironment, CrisisInboxAction


# ---------------------------------------------------------------------------
# ANSI colors
# ---------------------------------------------------------------------------
class C:
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"
    BG_RED = "\033[41m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"


URGENCY_COLORS = {
    "critical": C.BG_RED + C.WHITE + C.BOLD,
    "high": C.RED + C.BOLD,
    "medium": C.YELLOW,
    "low": C.GREEN,
}

URGENCY_LABELS = {
    "critical": " CRITICAL ",
    "high": "   HIGH   ",
    "medium": "  MEDIUM  ",
    "low": "   LOW    ",
}

CHANNEL_ICONS = {
    "sms": "SMS",
    "email": "EMAIL",
    "phone": "PHONE",
    "government_alert": "ALERT",
    "app_notification": "APP",
    "social_media": "SOCIAL",
}


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------
def header(text: str):
    width = 72
    print(f"\n{C.BOLD}{C.CYAN}{'=' * width}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}  {text}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}{'=' * width}{C.RESET}")


def subheader(text: str):
    print(f"\n{C.BOLD}{C.WHITE}--- {text} ---{C.RESET}")


def show_time(hour: float):
    h = int(hour)
    m = int((hour - h) * 60)
    day = "Day 1" if hour < 24 else "Day 2"
    display_h = h % 24
    ampm = "AM" if display_h < 12 else "PM"
    display_h = display_h % 12 or 12
    return f"{day} {display_h}:{m:02d} {ampm} (hour {hour:.1f}/48)"


def show_message_line(msg: dict, prefix: str = ""):
    urg = msg["urgency"]
    color = URGENCY_COLORS.get(urg, "")
    label = URGENCY_LABELS.get(urg, urg.upper())
    channel = CHANNEL_ICONS.get(msg["channel"], msg["channel"])
    handled = f"{C.GRAY}[DONE]{C.RESET} " if msg.get("handled") else ""
    superseded = f"{C.GRAY}[STALE]{C.RESET} " if msg.get("superseded") else ""
    drift = f"{C.BG_MAGENTA}{C.WHITE} DRIFT {C.RESET} " if msg.get("drift_flag") else ""
    deadline_str = ""
    if msg.get("deadline_hours") is not None:
        deadline_str = f" {C.DIM}(due h{msg['deadline_hours']:.0f}){C.RESET}"

    print(
        f"  {prefix}{color}[{label}]{C.RESET} "
        f"{C.DIM}{channel:>5}{C.RESET} "
        f"{drift}{superseded}{handled}"
        f"{C.BOLD}{msg['sender']}{C.RESET}: {msg['subject']}"
        f"{deadline_str}"
    )


def show_action(action_text: str):
    print(f"\n  {C.BG_BLUE}{C.WHITE}{C.BOLD} AGENT ACTION {C.RESET} {C.CYAN}{action_text}{C.RESET}")


def show_reward(reward: float, total: float):
    color = C.GREEN if reward > 0 else C.RED
    print(f"  {color}+{reward:.1f} pts{C.RESET} {C.DIM}(total: {total:.1f}){C.RESET}")


def show_drift_alert(msg: dict):
    print(f"\n  {C.BG_MAGENTA}{C.WHITE}{C.BOLD} SCHEMA DRIFT {C.RESET} "
          f"{C.MAGENTA}{C.BOLD}{msg['sender']}: {msg['subject']}{C.RESET}")
    print(f"  {C.MAGENTA}Rules have changed! Previous information may be outdated.{C.RESET}")


def show_expired(expired: list):
    if expired:
        print(f"\n  {C.RED}{C.BOLD}EXPIRED DEADLINES:{C.RESET}")
        for e in expired:
            print(f"    {C.RED}x {e['subject']}{C.RESET}")


def show_upcoming(upcoming: list):
    if upcoming:
        print(f"\n  {C.YELLOW}UPCOMING DEADLINES:{C.RESET}")
        for u in upcoming:
            print(f"    {C.YELLOW}! {u['subject']} ({u['hours_remaining']:.1f}h left){C.RESET}")


def pause(seconds: float = 0.5):
    time.sleep(seconds)


# ---------------------------------------------------------------------------
# Agent strategies
# ---------------------------------------------------------------------------
def smart_priority(messages: list[dict]) -> list[dict]:
    """Triage: safety first, then deadlines, then drift, then urgency."""
    urgency_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    unhandled = [m for m in messages if not m.get("handled") and not m.get("superseded")]

    def score(m):
        urg = urgency_order.get(m["urgency"], 4)
        deadline = m.get("deadline_hours") or 999
        drift = 0 if m.get("drift_flag") else 1
        return (urg, drift, deadline)

    return sorted(unhandled, key=score)


def naive_order(messages: list[dict]) -> list[dict]:
    """Respond in arrival order (bad strategy for comparison)."""
    return [m for m in messages if not m.get("handled") and not m.get("superseded")]


# ---------------------------------------------------------------------------
# Main demo loop
# ---------------------------------------------------------------------------
def run_demo(strategy: str = "smart", seed: int = 42, speed: float = 0.3):
    env = CrisisInboxEnvironment()
    obs = env.reset(seed=seed)

    def call(tool, **kwargs):
        o = env.step(CrisisInboxAction(tool_name=tool, arguments=kwargs))
        result = o.result
        if isinstance(result, str):
            return json.loads(result)
        return result

    prioritize = smart_priority if strategy == "smart" else naive_order
    strategy_name = "SMART TRIAGE" if strategy == "smart" else "NAIVE (arrival order)"

    header(f"CrisisInbox Demo  |  Strategy: {strategy_name}")
    print(f"\n  {C.DIM}Scenario: Post-hurricane evacuation in Sacramento")
    print(f"  You are a working parent. Your phone is about to explode.{C.RESET}")
    print(f"  {C.DIM}Messages: {obs.metadata['messages_total']} total | "
          f"Drift events: {obs.metadata['drift_events_scheduled']} scheduled{C.RESET}")
    pause(speed * 2)

    last_drift_count = 0
    actions_taken = 0
    max_actions = 25  # Cap for demo length

    # Advance through the timeline in chunks
    time_chunks = [0, 2, 6, 12, 20, 25, 34, 44, 48]

    for i in range(len(time_chunks) - 1):
        target_hour = time_chunks[i + 1]
        current = time_chunks[i]

        # Advance time to target
        while current < target_hour:
            advance = min(4.0, target_hour - current)
            result = call("advance_time", hours=advance)
            current = result["current_hour"]
            if result.get("new_messages", 0) > 0:
                pass  # Messages delivered silently

        # Get current state
        status = call("get_status")
        inbox = call("get_inbox")

        subheader(f"HOUR {status['current_hour']:.1f}  |  {show_time(status['current_hour'])}")
        print(f"  {C.DIM}Messages arrived: {status['messages_total_arrived']} | "
              f"Handled: {status['messages_handled']} | "
              f"Score: {status['total_score']:.1f}{C.RESET}")

        # Check for new drift events
        if status["drift_events_fired"] > last_drift_count:
            drift_msgs = [m for m in inbox if m.get("drift_flag") and not m.get("handled")]
            for dm in drift_msgs:
                show_drift_alert(dm)
                pause(speed)
            last_drift_count = status["drift_events_fired"]

        # Show deadlines
        show_expired(status.get("expired_deadlines", []))
        show_upcoming(status.get("upcoming_deadlines", []))

        # Show current inbox
        print(f"\n  {C.BOLD}INBOX ({len(inbox)} messages):{C.RESET}")
        # Show only recent unhandled, plus any drift
        visible = [m for m in inbox if not m.get("handled")]
        for msg in visible[:8]:  # Show max 8 at a time
            show_message_line(msg)
        if len(visible) > 8:
            print(f"  {C.DIM}  ... and {len(visible) - 8} more unread{C.RESET}")
        pause(speed)

        # Agent takes actions on available messages
        prioritized = prioritize(inbox)
        actions_this_chunk = 0
        max_per_chunk = 4  # Don't monopolize one time period

        for msg in prioritized:
            if actions_taken >= max_actions or actions_this_chunk >= max_per_chunk:
                break

            msg_id = msg["id"]

            # Read the message first
            full_msg = call("read_message", message_id=msg_id)
            if "error" in full_msg:
                continue

            # Generate a contextual response based on sender/urgency
            response = _generate_response(full_msg)

            # Try to respond
            result = call("respond_to_message", message_id=msg_id, response=response)
            if "error" in result:
                if "dependencies" in result.get("error", ""):
                    show_action(f"Cannot handle {msg_id} yet - dependencies unmet")
                    pause(speed * 0.5)
                continue

            show_action(f"Respond to {msg['sender']} - \"{msg['subject']}\"")
            print(f"  {C.DIM}\"{response[:80]}{'...' if len(response) > 80 else ''}\"{C.RESET}")
            show_reward(result["reward"], result["total_score"])
            pause(speed)

            actions_taken += 1
            actions_this_chunk += 1

        if status.get("done"):
            break

    # Final summary
    final_status = call("get_status")
    final_inbox = call("get_inbox")

    header("EPISODE COMPLETE")
    handled_count = final_status["messages_handled"]
    total_arrived = final_status["messages_total_arrived"]
    missed = len(final_status.get("expired_deadlines", []))

    print(f"\n  Strategy: {C.BOLD}{strategy_name}{C.RESET}")
    print(f"  Final Score: {C.BOLD}{C.GREEN}{final_status['total_score']:.1f} pts{C.RESET}")
    print(f"  Messages Handled: {handled_count}/{total_arrived}")
    print(f"  Deadlines Missed: {C.RED}{missed}{C.RESET}")
    print(f"  Drift Events Encountered: {final_status['drift_events_fired']}")

    # Show what was handled vs missed by urgency
    handled_ids = {m["id"] for m in final_inbox if m.get("handled")}
    by_urgency = {"critical": [0, 0], "high": [0, 0], "medium": [0, 0], "low": [0, 0]}
    for m in final_inbox:
        urg = m["urgency"]
        if urg in by_urgency:
            by_urgency[urg][1] += 1
            if m["id"] in handled_ids:
                by_urgency[urg][0] += 1

    print(f"\n  {C.BOLD}Coverage by Urgency:{C.RESET}")
    for urg, (handled, total) in by_urgency.items():
        color = URGENCY_COLORS.get(urg, "")
        pct = (handled / total * 100) if total > 0 else 0
        bar = "#" * int(pct / 5) + "." * (20 - int(pct / 5))
        print(f"    {color}{urg:>8}{C.RESET}: {handled}/{total} [{bar}] {pct:.0f}%")

    print()
    return final_status["total_score"]


def _generate_response(msg: dict) -> str:
    """Generate a contextual response based on sender and content."""
    sender = msg.get("sender", "")
    urgency = msg.get("urgency", "")
    subject = msg.get("subject", "").lower()

    if "national weather" in sender.lower() or "fema" in sender.lower():
        return "Acknowledged. Following evacuation orders immediately. Heading to designated shelter with essential documents and medication."
    if sender == "Mom":
        return "I'm safe, Mom. Don't worry. I'm following the evacuation orders and heading to the shelter. I'll call you as soon as I can. Love you."
    if sender == "Sister":
        if "kids" in subject or "take" in subject:
            return "I'll get them, don't worry. Heading to Oakwood now. I'll text you the second I have them safe."
        return "Kids are safe with me. Emma is being brave. Don't worry about anything, just stay safe yourself."
    if "emma" in sender.lower():
        return "Hey sweetie! Mac and cheese sounds perfect. Mommy is coming soon. Let's build a blanket fort while we wait!"
    if sender == "Boss" or sender == "HR Department":
        if "drift" in str(msg.get("drift_flag", "")):
            return "Thanks for the update on the emergency leave policy. I've submitted my status form on the HR portal. Will be taking the emergency leave days."
        return "I'm in the evacuation zone and following mandatory orders. Will work remotely when I can access wifi. Updating my status on the portal now."
    if "insurance" in sender.lower() or "state farm" in sender.lower():
        return "Filing claim now with policy number and damage photos. Have documented all damage with timestamps before any cleanup."
    if sender == "Neighbor Dave":
        return "Thanks for the heads up Dave. Stay safe at the shelter. I'll keep an eye on things here. We'll get through this."
    if "delta" in sender.lower() or "airline" in sender.lower():
        return "Selecting Option A for rebooking to the earliest available flight. Thank you for the flexibility during this emergency."
    if "school" in sender.lower() or "oakwood" in sender.lower():
        return "Acknowledged. Will arrange pickup before the deadline. Thank you for the early notification."
    if "pharmacy" in sender.lower() or "cvs" in sender.lower():
        return "Will pick up the prescription today. If the usual location is closed, I'll transfer to the nearest open CVS."
    if "sacramento" in sender.lower():
        return "Acknowledged. Following all advisories and avoiding affected areas."
    if urgency == "critical":
        return "Taking immediate action on this critical matter. Will follow up with details shortly."
    if urgency == "high":
        return "Understood, this is a priority. Handling this now and will confirm when complete."
    return "Thank you for the information. I've noted this and will address it as soon as possible given the current situation."


# ---------------------------------------------------------------------------
# Comparison mode
# ---------------------------------------------------------------------------
def run_comparison(seed: int = 42, speed: float = 0.2):
    """Run both strategies side by side for the demo."""
    header("CRISISINBOX: STRATEGY COMPARISON")
    print(f"\n  {C.DIM}Same episode, two different approaches.{C.RESET}")
    print(f"  {C.DIM}Which agent handles a disaster better?{C.RESET}\n")
    pause(1)

    print(f"{C.RED}{C.BOLD}{'=' * 72}")
    print(f"  ROUND 1: NAIVE AGENT (responds in arrival order)")
    print(f"{'=' * 72}{C.RESET}")
    pause(0.5)
    naive_score = run_demo(strategy="naive", seed=seed, speed=speed)

    pause(1)
    print(f"\n{C.GREEN}{C.BOLD}{'=' * 72}")
    print(f"  ROUND 2: TRAINED AGENT (smart triage)")
    print(f"{'=' * 72}{C.RESET}")
    pause(0.5)
    smart_score = run_demo(strategy="smart", seed=seed, speed=speed)

    header("FINAL COMPARISON")
    improvement = smart_score - naive_score
    pct = (improvement / max(naive_score, 1)) * 100
    print(f"\n  Naive Agent:   {C.RED}{naive_score:.1f} pts{C.RESET}")
    print(f"  Trained Agent: {C.GREEN}{smart_score:.1f} pts{C.RESET}")
    print(f"  Improvement:   {C.BOLD}{C.CYAN}+{improvement:.1f} pts ({pct:.0f}%){C.RESET}\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CrisisInbox Demo")
    parser.add_argument("--strategy", choices=["smart", "naive", "compare"],
                        default="compare", help="Agent strategy (default: compare)")
    parser.add_argument("--seed", type=int, default=42, help="Episode seed")
    parser.add_argument("--speed", type=float, default=0.3,
                        help="Pause between actions in seconds (default: 0.3)")
    args = parser.parse_args()

    if args.strategy == "compare":
        run_comparison(seed=args.seed, speed=args.speed)
    else:
        run_demo(strategy=args.strategy, seed=args.seed, speed=args.speed)
