"""
Gradio demo UI for the CrisisInbox environment.

Provides an interactive inbox viewer that lets judges/visitors step through
the 48-hour crisis scenario, see messages arrive, and watch an agent
(or human) make triage decisions.

Mounted alongside the FastAPI app at /demo.
"""

import json
import gradio as gr

try:
    from .crisis_inbox_environment import CrisisInboxEnvironment
except ImportError:
    from server.crisis_inbox_environment import CrisisInboxEnvironment


def _urgency_color(urgency: str) -> str:
    return {
        "critical": "#dc2626",
        "high": "#ea580c",
        "medium": "#ca8a04",
        "low": "#65a30d",
    }.get(urgency, "#6b7280")


def _format_inbox_html(env: CrisisInboxEnvironment) -> str:
    """Render the current inbox as styled HTML."""
    msgs = env._visible_messages
    hour = env._current_hour
    score = env._score
    handled_count = len(env._handled)
    superseded = env._superseded

    lines = [
        f'<div style="font-family: monospace; padding: 8px;">',
        f'<div style="display:flex; justify-content:space-between; margin-bottom:12px;">',
        f'<span><b>Hour {hour:.1f}</b> / 48</span>',
        f'<span>Score: <b>{score:.1f}</b></span>',
        f'<span>Handled: <b>{handled_count}</b> / {len(msgs)}</span>',
        f'</div>',
    ]

    # Separate unhandled and handled
    unhandled = [m for m in msgs if m.id not in env._handled]
    handled = [m for m in msgs if m.id in env._handled]

    if unhandled:
        lines.append('<div style="margin-bottom:8px;"><b>Unhandled:</b></div>')
        for msg in unhandled:
            color = _urgency_color(msg.urgency.value)
            is_superseded = msg.id in superseded
            is_drift = msg.drift_flag
            opacity = "0.5" if is_superseded else "1.0"
            badges = ""
            if is_drift:
                badges += ' <span style="background:#7c3aed;color:white;padding:1px 6px;border-radius:4px;font-size:11px;">POLICY UPDATE</span>'
            if is_superseded:
                badges += ' <span style="background:#6b7280;color:white;padding:1px 6px;border-radius:4px;font-size:11px;">SUPERSEDED</span>'
            deadline = f' | Due: hr {msg.deadline_hours:.0f}' if msg.deadline_hours else ""
            overdue = ""
            if msg.deadline_hours and hour > msg.deadline_hours:
                overdue = ' <span style="color:#dc2626;font-weight:bold;">OVERDUE</span>'
            lines.append(
                f'<div style="border-left:4px solid {color}; padding:4px 8px; margin:4px 0; opacity:{opacity}; background:#fafafa;">'
                f'<span style="color:{color};font-weight:bold;">{msg.urgency.value.upper()}</span> '
                f'<b>{msg.id}</b> | {msg.sender} via {msg.channel.value}{deadline}{overdue}{badges}<br/>'
                f'<span style="color:#374151;">{msg.subject}</span>'
                f'</div>'
            )

    if handled:
        lines.append(f'<details style="margin-top:12px;"><summary style="cursor:pointer;"><b>Handled ({len(handled)})</b></summary>')
        for msg in handled:
            color = _urgency_color(msg.urgency.value)
            lines.append(
                f'<div style="border-left:4px solid #d1d5db; padding:4px 8px; margin:4px 0; opacity:0.6;">'
                f'<span style="color:{color};">{msg.urgency.value.upper()}</span> '
                f'<b>{msg.id}</b> | {msg.sender} — {msg.subject}'
                f'</div>'
            )
        lines.append('</details>')

    lines.append('</div>')
    return "\n".join(lines)


def _format_message_detail(env: CrisisInboxEnvironment, msg_id: str) -> str:
    """Render full message content."""
    for msg in env._visible_messages:
        if msg.id == msg_id:
            color = _urgency_color(msg.urgency.value)
            warning = ""
            if msg.id in env._superseded:
                warning = f'<div style="background:#fef2f2;border:1px solid #dc2626;padding:8px;margin-bottom:8px;border-radius:4px;">This message has been superseded by {env._superseded[msg.id]}. Information may be outdated.</div>'
            return (
                f'<div style="font-family: monospace; padding: 8px;">'
                f'{warning}'
                f'<div style="border-left:4px solid {color}; padding:8px;">'
                f'<b>{msg.id}</b> — <span style="color:{color};font-weight:bold;">{msg.urgency.value.upper()}</span><br/>'
                f'<b>From:</b> {msg.sender} via {msg.channel.value}<br/>'
                f'<b>Subject:</b> {msg.subject}<br/>'
                f'<b>Arrived:</b> hour {msg.timestamp_hours:.1f}'
                f'{f" | <b>Deadline:</b> hour {msg.deadline_hours:.1f}" if msg.deadline_hours else ""}<br/>'
                f'<hr style="margin:8px 0;"/>'
                f'<div style="white-space:pre-wrap;">{msg.content}</div>'
                f'</div></div>'
            )
    return f'<div style="color:#6b7280;">Message {msg_id} not found or not yet arrived.</div>'


def _get_msg_choices(env: CrisisInboxEnvironment) -> list[str]:
    """Get list of unhandled message IDs for the dropdown."""
    return [
        f"{m.id} — [{m.urgency.value.upper()}] {m.sender}: {m.subject}"
        for m in env._visible_messages
        if m.id not in env._handled
    ]


# ── Gradio app state: one env instance per session ──────────────────

def reset_env(seed: int):
    env = CrisisInboxEnvironment()
    env.reset(seed=int(seed))
    inbox_html = _format_inbox_html(env)
    choices = _get_msg_choices(env)
    return env, inbox_html, gr.update(choices=choices, value=choices[0] if choices else None), "", f"Episode reset (seed={int(seed)}). Hour 0.0 — {len(env._visible_messages)} messages visible."


def advance_time(env, hours: float):
    if env is None:
        return None, "Reset the environment first.", gr.update(), "", ""
    env._advance_clock(float(hours))
    inbox_html = _format_inbox_html(env)
    choices = _get_msg_choices(env)
    done = " **EPISODE COMPLETE**" if env._current_hour >= 48.0 else ""
    return env, inbox_html, gr.update(choices=choices, value=choices[0] if choices else None), "", f"Advanced {hours}h → hour {env._current_hour:.1f}. {len(env._visible_messages)} messages visible.{done}"


def read_message(env, msg_choice: str):
    if env is None or not msg_choice:
        return None, "", ""
    msg_id = msg_choice.split(" — ")[0]
    detail = _format_message_detail(env, msg_id)
    return env, detail, ""


def _call_tool(env, tool_name: str, arguments: dict) -> dict:
    """Call an MCP tool on the environment and return parsed JSON result."""
    from openenv.core.env_server.mcp_types import CallToolAction
    action = CallToolAction(tool_name=tool_name, arguments=arguments)
    obs = env._handle_call_tool(action)
    raw = getattr(obs, "result", None)
    if hasattr(raw, "content"):
        raw = raw.content[0].text
    if isinstance(raw, str):
        return json.loads(raw)
    return raw if isinstance(raw, dict) else {}


def respond_to_message(env, msg_choice: str, response: str):
    if env is None:
        return None, "Reset the environment first.", gr.update(), "", ""
    if not msg_choice:
        return env, _format_inbox_html(env), gr.update(), "", "Select a message first."
    if not response.strip():
        return env, _format_inbox_html(env), gr.update(), "", "Write a response first."

    msg_id = msg_choice.split(" — ")[0]
    result = _call_tool(env, "respond_to_message", {"message_id": msg_id, "response": response})

    if "error" in result:
        return env, _format_inbox_html(env), gr.update(), "", f"Error: {result['error']}"

    reward = result.get("reward", 0)
    inbox_html = _format_inbox_html(env)
    choices = _get_msg_choices(env)
    status = f"Responded to {msg_id} → reward: **{reward:+.1f}** (total: {env._score:.1f})"
    return env, inbox_html, gr.update(choices=choices, value=choices[0] if choices else None), "", status


def build_demo() -> gr.Blocks:
    """Build the Gradio Blocks demo."""
    with gr.Blocks(
        title="CrisisInbox Demo",
        theme=gr.themes.Soft(),
        css=".gradio-container { max-width: 1100px !important; }",
    ) as demo:
        gr.Markdown("# CrisisInbox — Interactive Demo\nStep through a 48-hour post-disaster inbox. Triage messages, respond to emergencies, and watch policies change mid-crisis.")

        env_state = gr.State(None)

        with gr.Row():
            seed_input = gr.Number(value=42, label="Episode Seed", precision=0)
            reset_btn = gr.Button("Reset Episode", variant="primary")
            advance_btn = gr.Button("Advance +2h")
            advance_4_btn = gr.Button("Advance +4h")

        status_text = gr.Markdown("Click **Reset Episode** to start.")
        inbox_html = gr.HTML(label="Inbox")

        with gr.Row():
            with gr.Column(scale=2):
                msg_dropdown = gr.Dropdown(label="Select message", choices=[], interactive=True)
                read_btn = gr.Button("Read Message")
                msg_detail = gr.HTML(label="Message Detail")
            with gr.Column(scale=1):
                response_input = gr.Textbox(label="Your response", lines=3, placeholder="Type your response here...")
                respond_btn = gr.Button("Respond", variant="primary")

        # Wire up events
        reset_btn.click(
            reset_env, inputs=[seed_input],
            outputs=[env_state, inbox_html, msg_dropdown, msg_detail, status_text],
        )
        advance_btn.click(
            advance_time, inputs=[env_state, gr.Number(value=2, visible=False)],
            outputs=[env_state, inbox_html, msg_dropdown, msg_detail, status_text],
        )
        advance_4_btn.click(
            advance_time, inputs=[env_state, gr.Number(value=4, visible=False)],
            outputs=[env_state, inbox_html, msg_dropdown, msg_detail, status_text],
        )
        read_btn.click(
            read_message, inputs=[env_state, msg_dropdown],
            outputs=[env_state, msg_detail, status_text],
        )
        respond_btn.click(
            respond_to_message, inputs=[env_state, msg_dropdown, response_input],
            outputs=[env_state, inbox_html, msg_dropdown, msg_detail, status_text],
        )

    return demo
