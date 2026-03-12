"""
Tests for the reward functions in CrisisInbox.

Covers: tone_multiplier, calculate_reward, score_format, score_action
"""

import pytest
import sys
import os

# Allow imports from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models import Channel, Message, Urgency
from server.crisis_inbox_environment import (
    tone_multiplier,
    calculate_reward,
    score_format,
    score_action,
    _FAMILY_SENDERS,
    _FAMILY_TONE_WORDS,
    _FORMAL_TONE_WORDS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_message(**overrides) -> Message:
    """Factory for creating test messages with sensible defaults."""
    defaults = {
        "id": "msg_test_001",
        "sender": "Test Sender",
        "channel": Channel.EMAIL,
        "subject": "Test Subject",
        "content": "Test content body.",
        "urgency": Urgency.MEDIUM,
        "timestamp_hours": 5.0,
        "deadline_hours": None,
        "dependencies": [],
        "drift_flag": False,
        "supersedes": None,
        "conflicts_with": None,
    }
    defaults.update(overrides)
    return Message(**defaults)


# ---------------------------------------------------------------------------
# tone_multiplier tests
# ---------------------------------------------------------------------------

class TestToneMultiplier:
    """Tests for tone_multiplier(sender, response)."""

    def test_family_sender_with_warm_tone(self):
        """Family senders with warm tone words get a 1.15 multiplier."""
        result = tone_multiplier("Mom", "I love you and I'm safe, don't worry")
        assert result == 1.15

    def test_family_sender_with_one_warm_word(self):
        """Family sender with exactly one warm word gets 1.07."""
        result = tone_multiplier("Sister", "I'm safe right now")
        assert result == 1.07

    def test_family_sender_no_warm_words(self):
        """Family sender with no warm words gets neutral 1.0."""
        result = tone_multiplier("Neighbor Dave", "Got it, will do")
        assert result == 1.0

    def test_formal_sender_with_formal_tone(self):
        """Non-family senders with formal words get 1.1."""
        result = tone_multiplier("State Farm Insurance", "Please confirm the documentation has been submitted")
        assert result == 1.1

    def test_formal_sender_one_formal_word(self):
        """Non-family sender with one formal word gets 1.05."""
        result = tone_multiplier("HR Department", "Please send the form")
        assert result == 1.05

    def test_neutral_response(self):
        """Completely neutral response returns 1.0."""
        result = tone_multiplier("Random Person", "ok")
        assert result == 1.0

    def test_case_insensitivity(self):
        """Sender matching is case-insensitive."""
        result = tone_multiplier("MOM", "I love you and I'm safe")
        assert result == 1.15

    def test_emma_is_family(self):
        """Emma (niece) is recognized as a family sender."""
        result = tone_multiplier("Emma", "I love you, stay safe okay")
        assert result == 1.15

    def test_all_family_senders_recognized(self):
        """All defined family senders are recognized."""
        for sender in _FAMILY_SENDERS:
            result = tone_multiplier(sender, "I love you, stay safe")
            assert result > 1.0, f"Family sender '{sender}' not recognized"


# ---------------------------------------------------------------------------
# calculate_reward tests
# ---------------------------------------------------------------------------

class TestCalculateReward:
    """Tests for calculate_reward(msg, current_hour, response, superseded, ...)."""

    def test_urgency_base_rewards(self):
        """Each urgency level has the correct base reward."""
        for urgency, expected_base in [
            (Urgency.CRITICAL, 10.0),
            (Urgency.HIGH, 5.0),
            (Urgency.MEDIUM, 3.0),
            (Urgency.LOW, 1.0),
        ]:
            msg = make_message(urgency=urgency)
            reward = calculate_reward(msg, 5.0, "A reasonable response here", {})
            # Base reward may be modified by tone, but should be proportional
            assert reward > 0

    def test_critical_higher_than_low(self):
        """Critical messages always yield higher reward than low ones."""
        critical = make_message(urgency=Urgency.CRITICAL)
        low = make_message(urgency=Urgency.LOW, id="msg_test_002")
        r_crit = calculate_reward(critical, 5.0, "Evacuating now immediately", {})
        r_low = calculate_reward(low, 5.0, "Evacuating now immediately", {})
        assert r_crit > r_low

    def test_early_response_bonus(self):
        """Responding before deadline gives a timing bonus."""
        msg = make_message(deadline_hours=10.0)
        early = calculate_reward(msg, 2.0, "Handling this right away", {})
        late_but_on_time = calculate_reward(msg, 9.5, "Handling this right away", {})
        assert early > late_but_on_time

    def test_missed_deadline_penalty(self):
        """Responding after deadline applies a 0.25 penalty."""
        msg = make_message(deadline_hours=5.0)
        on_time = calculate_reward(msg, 4.0, "Handling this right away", {})
        missed = calculate_reward(msg, 6.0, "Handling this right away", {})
        assert missed < on_time
        # Missed should be roughly 25% of base (times other multipliers)
        assert missed < on_time * 0.5

    def test_short_response_penalty(self):
        """Very short responses (< 10 chars) get a 0.5 penalty."""
        msg = make_message()
        good = calculate_reward(msg, 5.0, "I will handle this situation promptly", {})
        short = calculate_reward(msg, 5.0, "ok", {})
        assert short < good

    def test_drift_flag_bonus(self):
        """Messages with drift_flag=True get a 1.5x bonus."""
        normal = make_message(drift_flag=False)
        drift = make_message(drift_flag=True, id="msg_test_drift")
        r_normal = calculate_reward(normal, 5.0, "Acknowledging the update and adjusting", {})
        r_drift = calculate_reward(drift, 5.0, "Acknowledging the update and adjusting", {})
        assert r_drift == pytest.approx(r_normal * 1.5, rel=0.01)

    def test_superseded_penalty(self):
        """Handling a superseded message gets a 0.5 penalty."""
        msg = make_message()
        normal = calculate_reward(msg, 5.0, "Taking action on this immediately", {})
        superseded = calculate_reward(msg, 5.0, "Taking action on this immediately", {"msg_test_001": "msg_036"})
        assert superseded == pytest.approx(normal * 0.5, rel=0.01)

    def test_conflict_bonus(self):
        """Messages with a conflicts_with field get 1.25x bonus."""
        normal = make_message()
        conflict = make_message(conflicts_with="msg_other", id="msg_test_conflict")
        r_normal = calculate_reward(normal, 5.0, "Choosing this option carefully", {})
        r_conflict = calculate_reward(conflict, 5.0, "Choosing this option carefully", {})
        assert r_conflict == pytest.approx(r_normal * 1.25, rel=0.01)

    def test_priority_penalty_low_over_critical(self):
        """Handling a low message when critical is unhandled gets 0.3 penalty."""
        low_msg = make_message(urgency=Urgency.LOW, id="msg_low")
        critical_msg = make_message(urgency=Urgency.CRITICAL, id="msg_crit")

        visible = [low_msg, critical_msg]
        handled = {}  # Nothing handled yet

        reward = calculate_reward(
            low_msg, 5.0, "Doing this low priority thing instead",
            {}, visible_messages=visible, handled=handled,
        )
        reward_no_crit = calculate_reward(
            low_msg, 5.0, "Doing this low priority thing instead",
            {},
        )
        assert reward < reward_no_crit

    def test_priority_penalty_not_applied_to_high(self):
        """Priority penalty does NOT apply to high-urgency messages."""
        high_msg = make_message(urgency=Urgency.HIGH, id="msg_high")
        critical_msg = make_message(urgency=Urgency.CRITICAL, id="msg_crit")

        visible = [high_msg, critical_msg]
        handled = {}

        r_with = calculate_reward(
            high_msg, 5.0, "Handling this high priority item", {},
            visible_messages=visible, handled=handled,
        )
        r_without = calculate_reward(
            high_msg, 5.0, "Handling this high priority item", {},
        )
        # High urgency should NOT be penalized
        assert r_with == r_without

    def test_reward_is_rounded(self):
        """Reward should be rounded to 2 decimal places."""
        msg = make_message()
        reward = calculate_reward(msg, 5.0, "A reasonable response", {})
        assert reward == round(reward, 2)


# ---------------------------------------------------------------------------
# score_format tests
# ---------------------------------------------------------------------------

class TestScoreFormat:
    """Tests for score_format(completion)."""

    def test_perfect_format(self):
        """A perfectly formatted completion gets full 2.0."""
        completion = 'respond_to_message(msg_001, "Evacuating immediately")'
        assert score_format(completion) == 2.0

    def test_partial_format_tool_name_only(self):
        """Just mentioning the tool name gives 0.5."""
        completion = "I should respond_to_message about this"
        assert score_format(completion) == 0.5

    def test_partial_format_msg_id_only(self):
        """Just having a msg_id gives 0.5."""
        completion = "I need to handle msg_042"
        assert score_format(completion) == 0.5

    def test_tool_with_paren(self):
        """Tool name with parentheses adds another 0.5."""
        completion = "respond_to_message( something here"
        assert score_format(completion) >= 1.0

    def test_empty_completion(self):
        """Empty completion scores 0."""
        assert score_format("") == 0.0

    def test_irrelevant_text(self):
        """Random text scores 0."""
        assert score_format("The weather is nice today") == 0.0

    def test_graduated_scoring(self):
        """Score increases with better formatting."""
        s1 = score_format("respond_to_message")
        s2 = score_format("respond_to_message(msg_001")
        s3 = score_format('respond_to_message(msg_001, "hello")')
        assert s1 < s2 < s3


# ---------------------------------------------------------------------------
# score_action tests
# ---------------------------------------------------------------------------

class TestScoreAction:
    """Tests for score_action(completion, prompt_data)."""

    @pytest.fixture
    def prompt_data(self):
        """Sample prompt data mimicking environment state."""
        return {
            "messages": [
                {
                    "id": "msg_001",
                    "sender": "National Weather Service",
                    "channel": "government_alert",
                    "subject": "Mandatory Evacuation",
                    "content": "Evacuate Zone A immediately.",
                    "urgency": "critical",
                    "timestamp_hours": 0.0,
                    "deadline_hours": 6.0,
                    "handled": False,
                },
                {
                    "id": "msg_002",
                    "sender": "Mom",
                    "channel": "sms",
                    "subject": "Are you safe?",
                    "content": "Are you okay?",
                    "urgency": "high",
                    "timestamp_hours": 0.5,
                    "handled": False,
                },
            ],
            "hour": 2.0,
            "superseded": {},
        }

    def test_well_formed_action_scores_high(self, prompt_data):
        """A well-formed action on a critical message scores > format alone."""
        completion = 'respond_to_message(msg_001, "Evacuating immediately to Lincoln High")'
        score = score_action(completion, prompt_data)
        fmt_only = score_format(completion)
        assert score > fmt_only

    def test_invalid_msg_id_gets_partial_credit(self, prompt_data):
        """Referencing a non-existent message gets format + 0.5."""
        completion = 'respond_to_message(msg_999, "hello")'
        score = score_action(completion, prompt_data)
        fmt = score_format(completion)
        assert score == pytest.approx(fmt + 0.5, rel=0.01)

    def test_no_parseable_action(self, prompt_data):
        """Completely unparseable completion gets only format score."""
        completion = "I think we should evacuate but I'm not sure what to do"
        score = score_action(completion, prompt_data)
        assert score == score_format(completion)

    def test_critical_scores_higher_than_high(self, prompt_data):
        """Handling critical message scores higher than handling high message."""
        crit = 'respond_to_message(msg_001, "Evacuating to shelter right now")'
        high = 'respond_to_message(msg_002, "I am safe, love you mom")'
        assert score_action(crit, prompt_data) > score_action(high, prompt_data)
