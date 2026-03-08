"""
Static HTML demo for the CrisisInbox environment.

Generates a scenario overview page showing message timeline, urgency
distribution, and drift events. Served at /demo as a FastAPI endpoint.
"""

from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse

try:
    from .crisis_inbox_environment import CrisisInboxEnvironment
except ImportError:
    from server.crisis_inbox_environment import CrisisInboxEnvironment

try:
    from ..drift_events import ALL_DRIFT_EVENTS
except ImportError:
    from drift_events import ALL_DRIFT_EVENTS

router = APIRouter()

URGENCY_COLORS = {
    "critical": "#dc2626",
    "high": "#ea580c",
    "medium": "#ca8a04",
    "low": "#65a30d",
}


def _generate_demo_html(seed: int = 42) -> str:
    """Run one episode and render an HTML overview."""
    env = CrisisInboxEnvironment()
    env.reset(seed=seed)

    # Advance through full timeline collecting messages
    arrivals = []
    prev_count = 0
    h = 0.0
    while h <= 48.0:
        if env._current_hour < h:
            env._advance_clock(h - env._current_hour)
        msgs = env._visible_messages
        if len(msgs) > prev_count:
            for m in msgs[prev_count:]:
                arrivals.append({
                    "id": m.id,
                    "hour": m.timestamp_hours,
                    "urgency": m.urgency.value,
                    "sender": m.sender,
                    "subject": m.subject,
                    "content": m.content[:200],
                    "channel": m.channel.value,
                    "deadline": m.deadline_hours,
                    "drift": m.drift_flag,
                    "supersedes": m.supersedes,
                })
            prev_count = len(msgs)
        h += 0.5

    # Count by urgency
    urgency_counts = {}
    for a in arrivals:
        urgency_counts[a["urgency"]] = urgency_counts.get(a["urgency"], 0) + 1

    drift_msgs = [a for a in arrivals if a["drift"]]

    # Build HTML
    msg_rows = ""
    for a in arrivals:
        color = URGENCY_COLORS.get(a["urgency"], "#6b7280")
        drift_badge = '<span style="background:#7c3aed;color:white;padding:1px 6px;border-radius:4px;font-size:11px;margin-left:6px;">DRIFT</span>' if a["drift"] else ""
        supersedes_badge = f'<span style="background:#6b7280;color:white;padding:1px 6px;border-radius:4px;font-size:11px;margin-left:6px;">supersedes {a["supersedes"]}</span>' if a.get("supersedes") else ""
        deadline_text = f'<span style="color:#6b7280;"> | deadline: hr {a["deadline"]:.0f}</span>' if a["deadline"] else ""
        msg_rows += f"""<div style="border-left:4px solid {color};padding:6px 10px;margin:4px 0;background:#fafafa;border-radius:0 4px 4px 0;">
            <span style="color:{color};font-weight:bold;font-size:12px;">{a["urgency"].upper()}</span>
            <b>{a["id"]}</b> | {a["sender"]} via {a["channel"]}{deadline_text}{drift_badge}{supersedes_badge}
            <br/><span style="color:#374151;">{a["subject"]}</span>
            <br/><span style="color:#6b7280;font-size:12px;">Hour {a["hour"]:.1f}</span>
        </div>"""

    # Urgency summary bars
    total = len(arrivals)
    urgency_bars = ""
    for u in ["critical", "high", "medium", "low"]:
        count = urgency_counts.get(u, 0)
        pct = (count / total * 100) if total else 0
        color = URGENCY_COLORS[u]
        urgency_bars += f"""<div style="margin:4px 0;">
            <span style="display:inline-block;width:70px;font-size:13px;font-weight:bold;color:{color};">{u.upper()}</span>
            <span style="display:inline-block;width:40px;text-align:right;font-size:13px;">{count}</span>
            <div style="display:inline-block;width:60%;height:18px;background:#f3f4f6;border-radius:4px;vertical-align:middle;margin-left:8px;">
                <div style="width:{pct}%;height:100%;background:{color};border-radius:4px;opacity:0.8;"></div>
            </div>
            <span style="font-size:12px;color:#6b7280;margin-left:4px;">{pct:.0f}%</span>
        </div>"""

    # Drift events list
    drift_list = ""
    if drift_msgs:
        for d in sorted(drift_msgs, key=lambda x: x["hour"]):
            sup = f" (supersedes {d['supersedes']})" if d.get("supersedes") else ""
            drift_list += f'<div style="margin:4px 0;padding:4px 8px;background:#f5f3ff;border-left:3px solid #7c3aed;border-radius:0 4px 4px 0;"><b>Hour {d["hour"]:.1f}</b> — {d["subject"]}{sup}</div>'
    else:
        drift_list = '<div style="color:#6b7280;">No drift events in this episode.</div>'

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>CrisisInbox — Scenario Overview</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #fff; color: #1f2937; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ font-size: 24px; margin-bottom: 4px; }}
        h2 {{ font-size: 16px; margin-top: 24px; margin-bottom: 8px; color: #374151; border-bottom: 1px solid #e5e7eb; padding-bottom: 4px; }}
        .stats {{ display: flex; gap: 16px; margin: 16px 0; }}
        .stat {{ flex: 1; padding: 12px; background: #f9fafb; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 28px; font-weight: bold; }}
        .stat-label {{ font-size: 12px; color: #6b7280; }}
        .seed-nav {{ margin: 8px 0; font-size: 13px; color: #6b7280; }}
        .seed-nav a {{ color: #2563eb; text-decoration: none; margin: 0 4px; }}
        .seed-nav a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
<div class="container">
    <h1>CrisisInbox — Scenario Overview</h1>
    <div class="seed-nav">
        Seed: <b>{seed}</b> |
        Try: <a href="?seed=0">0</a> <a href="?seed=7">7</a> <a href="?seed=42">42</a> <a href="?seed=99">99</a> <a href="?seed=123">123</a>
    </div>

    <div class="stats">
        <div class="stat"><div class="stat-value">{total}</div><div class="stat-label">Total Messages</div></div>
        <div class="stat"><div class="stat-value" style="color:#dc2626;">{urgency_counts.get("critical", 0)}</div><div class="stat-label">Critical</div></div>
        <div class="stat"><div class="stat-value" style="color:#7c3aed;">{len(drift_msgs)}</div><div class="stat-label">Drift Events</div></div>
        <div class="stat"><div class="stat-value">48h</div><div class="stat-label">Timeline</div></div>
    </div>

    <h2>Urgency Distribution</h2>
    {urgency_bars}

    <h2>Drift Events (Policy Changes)</h2>
    {drift_list}

    <h2>All Messages ({total})</h2>
    {msg_rows}
</div>
</body>
</html>"""
    return html


@router.get("/demo", response_class=HTMLResponse)
def demo_page(seed: Optional[int] = Query(default=42, description="Episode seed")):
    """Serve a static scenario overview page."""
    return _generate_demo_html(seed=seed)
