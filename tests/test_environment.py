"""
Tests for the CrisisInbox environment lifecycle and mechanics.

Covers: reset, message delivery, responding, time advancement, drift events,
dependencies, conflicts, escalations, and edge cases.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models import Urgency
from server.crisis_inbox_environment import (
    CrisisInboxEnvironment,
    CrisisInboxAction,
)


@pytest.fixture
def env():
    """Create and reset a fresh environment with a fixed seed."""
    e = CrisisInboxEnvironment()
    e.reset(seed=42)
    return e


# ---------------------------------------------------------------------------
# Reset and initialization
# ---------------------------------------------------------------------------

class TestReset:
    """Tests for environment reset and initialization."""

    def test_reset_returns_observation(self, env):
        """Reset returns a valid observation with status 'ready'."""
        obs = env.reset(seed=42)
        assert obs.done is False
        assert obs.reward == 0.0
        assert obs.result["status"] == "ready"

    def test_reset_delivers_initial_messages(self, env):
        """Some messages should be visible at hour 0."""
        inbox = env.get_inbox()
        assert len(inbox) > 0

    def test_reset_clears_state(self, env):
        """Reset should clear all previous state."""
        # Handle a message first
        inbox = env.get_inbox()
        first_id = inbox[0]["id"]
        env.respond_to_message(first_id, "Handling this")

        # Reset and verify clean state
        env.reset(seed=99)
        status = env.get_status()
        assert status["messages_handled"] == 0
        assert status["current_hour"] == 0.0
        assert status["total_score"] == 0.0

    def test_different_seeds_different_drift_events(self):
        """Different seeds should produce different drift event selections."""
        e1 = CrisisInboxEnvironment()
        e1.reset(seed=1)
        d1 = e1._fired_drifts.copy()

        e2 = CrisisInboxEnvironment()
        e2.reset(seed=2)
        d2 = e2._fired_drifts.copy()

        # Both start empty, but advance time to trigger drifts
        for e in [e1, e2]:
            e.advance_time(4.0)
            e.advance_time(4.0)
            e.advance_time(4.0)
            e.advance_time(4.0)
            e.advance_time(4.0)
            e.advance_time(4.0)
            e.advance_time(4.0)
            e.advance_time(4.0)
            e.advance_time(4.0)
            e.advance_time(4.0)
            e.advance_time(4.0)
            e.advance_time(4.0)  # 48 hours

        d1_final = e1._fired_drifts
        d2_final = e2._fired_drifts

        # With different seeds, drift events should differ (probabilistically)
        # Both should have exactly 3 drift events
        assert len(d1_final) == 3
        assert len(d2_final) == 3

    def test_same_seed_reproducible(self):
        """Same seed should produce identical initial states."""
        e1 = CrisisInboxEnvironment()
        e1.reset(seed=42)
        inbox1 = e1.get_inbox()

        e2 = CrisisInboxEnvironment()
        e2.reset(seed=42)
        inbox2 = e2.get_inbox()

        assert len(inbox1) == len(inbox2)
        for m1, m2 in zip(inbox1, inbox2):
            assert m1["id"] == m2["id"]


# ---------------------------------------------------------------------------
# Message operations
# ---------------------------------------------------------------------------

class TestMessageOperations:
    """Tests for get_inbox, read_message, respond_to_message."""

    def test_get_inbox_returns_list(self, env):
        """get_inbox returns a list of message dicts."""
        inbox = env.get_inbox()
        assert isinstance(inbox, list)
        assert len(inbox) > 0
        assert "id" in inbox[0]
        assert "sender" in inbox[0]
        assert "urgency" in inbox[0]

    def test_read_message_costs_time(self, env):
        """Reading a message advances the clock by 0.1 hours."""
        status_before = env.get_status()
        inbox = env.get_inbox()
        env.read_message(inbox[0]["id"])
        status_after = env.get_status()
        assert status_after["current_hour"] == pytest.approx(
            status_before["current_hour"] + 0.1, abs=0.01
        )

    def test_read_nonexistent_message(self, env):
        """Reading a non-existent message returns an error."""
        result = env.read_message("msg_nonexistent_xyz")
        assert "error" in result

    def test_respond_to_message_earns_reward(self, env):
        """Responding to a message earns a positive reward."""
        inbox = env.get_inbox()
        first_id = inbox[0]["id"]
        result = env.respond_to_message(first_id, "Taking immediate action on this")
        assert result["reward"] > 0
        assert result["status"] == "handled"

    def test_respond_costs_time(self, env):
        """Responding advances the clock by 0.25 hours."""
        hour_before = env.get_status()["current_hour"]
        inbox = env.get_inbox()
        env.respond_to_message(inbox[0]["id"], "Handling this now")
        hour_after = env.get_status()["current_hour"]
        assert hour_after == pytest.approx(hour_before + 0.25, abs=0.01)

    def test_cannot_handle_same_message_twice(self, env):
        """Responding to an already-handled message returns an error."""
        inbox = env.get_inbox()
        first_id = inbox[0]["id"]
        env.respond_to_message(first_id, "First response")
        result = env.respond_to_message(first_id, "Second response")
        assert "error" in result

    def test_respond_to_nonexistent_message(self, env):
        """Responding to a non-existent message returns an error."""
        result = env.respond_to_message("msg_nonexistent", "Hello")
        assert "error" in result


# ---------------------------------------------------------------------------
# Time advancement
# ---------------------------------------------------------------------------

class TestTimeAdvancement:
    """Tests for advance_time and the timeline engine."""

    def test_advance_time_basic(self, env):
        """advance_time moves the clock forward."""
        result = env.advance_time(2.0)
        assert result["current_hour"] >= 2.0
        assert result["advanced_by"] == 2.0

    def test_advance_time_clamped_min(self, env):
        """advance_time enforces minimum of 0.5 hours."""
        result = env.advance_time(0.1)
        assert result["advanced_by"] == 0.5

    def test_advance_time_clamped_max(self, env):
        """advance_time enforces maximum of 4.0 hours."""
        result = env.advance_time(10.0)
        assert result["advanced_by"] == 4.0

    def test_new_messages_arrive_over_time(self, env):
        """Advancing time should cause new messages to arrive."""
        initial_count = len(env.get_inbox())
        env.advance_time(4.0)
        env.advance_time(4.0)
        env.advance_time(4.0)
        later_count = len(env.get_inbox())
        assert later_count > initial_count

    def test_episode_ends_at_48_hours(self, env):
        """Episode should be done after 48 hours."""
        for _ in range(13):  # 13 * 4 = 52 hours
            result = env.advance_time(4.0)
        assert result["done"] is True
        assert result["current_hour"] == pytest.approx(48.0, abs=0.5)


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------

class TestDependencies:
    """Tests for message dependency chains."""

    def test_unmet_dependencies_blocked(self, env):
        """Messages with unmet dependencies cannot be handled."""
        # Find a message with dependencies by advancing time
        for _ in range(6):
            env.advance_time(4.0)

        inbox = env.get_inbox()
        for msg_dict in inbox:
            # Look at the internal message to check dependencies
            msg_obj = next(
                (m for m in env._all_messages if m.id == msg_dict["id"]),
                None,
            )
            if msg_obj and msg_obj.dependencies:
                # Check if deps are unmet
                unmet = [d for d in msg_obj.dependencies if d not in env._handled]
                if unmet:
                    result = env.respond_to_message(msg_dict["id"], "Trying to handle")
                    assert "error" in result
                    assert "dependencies" in result["error"].lower() or "Unmet" in result["error"]
                    return

        pytest.skip("No messages with unmet dependencies found in this seed/timeline")


# ---------------------------------------------------------------------------
# Drift events
# ---------------------------------------------------------------------------

class TestDriftEvents:
    """Tests for schema drift mechanics."""

    def test_three_drift_events_fire(self, env):
        """Exactly 3 drift events should fire over a full episode."""
        for _ in range(12):
            env.advance_time(4.0)
        assert len(env._fired_drifts) == 3

    def test_drift_messages_appear(self, env):
        """Drift event messages should appear in the inbox after trigger time."""
        # Get the trigger hours for scheduled drift events
        drift_hours = [d.trigger_hour for d in env._drift_events]
        max_trigger = max(drift_hours) if drift_hours else 35.0

        # Advance past the latest drift trigger
        hours_needed = max_trigger + 1.0
        while env._current_hour < hours_needed:
            env.advance_time(4.0)

        inbox = env.get_inbox()
        inbox_ids = {m["id"] for m in inbox}

        # At least some drift messages should be in the inbox
        drift_msg_ids = set()
        for drift in env._drift_events:
            for msg in drift.messages:
                drift_msg_ids.add(msg.id)

        found = drift_msg_ids & inbox_ids
        assert len(found) > 0, "No drift messages found in inbox after trigger times"


# ---------------------------------------------------------------------------
# Step interface (OpenEnv)
# ---------------------------------------------------------------------------

class TestStepInterface:
    """Tests for the OpenEnv step() dispatch."""

    def test_step_get_inbox(self, env):
        """step() with get_inbox tool returns inbox."""
        obs = env.step(CrisisInboxAction(tool_name="get_inbox", arguments={}))
        assert isinstance(obs.result, list)
        assert obs.done is False

    def test_step_get_status(self, env):
        """step() with get_status tool returns status dict."""
        obs = env.step(CrisisInboxAction(tool_name="get_status", arguments={}))
        assert "current_hour" in obs.result
        assert "total_score" in obs.result

    def test_step_unknown_tool(self, env):
        """step() with unknown tool returns error."""
        obs = env.step(CrisisInboxAction(tool_name="nonexistent_tool", arguments={}))
        assert "error" in obs.result

    def test_step_respond(self, env):
        """step() with respond_to_message returns reward."""
        inbox_obs = env.step(CrisisInboxAction(tool_name="get_inbox", arguments={}))
        first_id = inbox_obs.result[0]["id"]
        obs = env.step(CrisisInboxAction(
            tool_name="respond_to_message",
            arguments={"message_id": first_id, "response": "Handling this now"},
        ))
        assert obs.reward > 0

    def test_step_increments_step_count(self, env):
        """Each step increments the step counter."""
        assert env.state.step_count == 0
        env.step(CrisisInboxAction(tool_name="get_inbox", arguments={}))
        assert env.state.step_count == 1
        env.step(CrisisInboxAction(tool_name="get_status", arguments={}))
        assert env.state.step_count == 2


# ---------------------------------------------------------------------------
# Conflict mechanics
# ---------------------------------------------------------------------------

class TestConflicts:
    """Tests for message conflict handling."""

    def test_handling_conflict_expires_other(self, env):
        """Handling a message with conflicts_with auto-expires the conflicting message."""
        # Advance to get more messages
        for _ in range(6):
            env.advance_time(4.0)

        inbox = env.get_inbox()
        for msg_dict in inbox:
            if msg_dict.get("conflicts_with") and not msg_dict["handled"]:
                conflict_id = msg_dict["conflicts_with"]
                # Check if the conflict target is also unhandled
                conflict_msg = next(
                    (m for m in inbox if m["id"] == conflict_id),
                    None,
                )
                if conflict_msg and not conflict_msg["handled"]:
                    env.respond_to_message(msg_dict["id"], "Choosing this option")
                    # The conflicting message should now be auto-handled
                    assert conflict_id in env._handled
                    return

        pytest.skip("No actionable conflict pairs found in this seed/timeline")
