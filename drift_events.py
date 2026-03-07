"""
Schema drift events for the CrisisInbox environment.

Each drift event represents a mid-episode policy/rule change that invalidates
previous information. The agent must detect these changes and adapt.

There are 5 drift events defined. Each episode randomly selects 3 to fire.
Drift events inject new messages and may modify existing deadlines/rules.
"""

import random
from dataclasses import dataclass
from typing import Callable

from models import Channel, Message, Urgency


@dataclass
class DriftEvent:
    """A schema drift event that fires at a specific time in the episode."""
    id: str
    name: str
    description: str
    trigger_hour: float
    messages: list[Message]
    superseded_msg_ids: list[str]


# ---------------------------------------------------------------------------
# The 5 drift events
# ---------------------------------------------------------------------------

DRIFT_INSURANCE_DEADLINE = DriftEvent(
    id="drift_insurance",
    name="Insurance deadline shortened",
    description="State Farm shortens claim filing deadline from 72h to 48h",
    trigger_hour=20.0,
    messages=[
        Message(
            id="msg_036",
            sender="State Farm Insurance",
            channel=Channel.EMAIL,
            subject="UPDATED: Claim deadline changed to 48 hours",
            content=(
                "IMPORTANT UPDATE: Due to the volume of claims, State Farm has shortened "
                "the initial claim filing deadline from 72 hours to 48 hours for expedited "
                "processing. Claims filed after 48 hours will still be accepted but may "
                "experience significant processing delays of 30-60 days. Please file ASAP."
            ),
            urgency=Urgency.CRITICAL,
            timestamp_hours=20.0,
            deadline_hours=48.0,
            drift_flag=True,
            supersedes="msg_004",
        ),
    ],
    superseded_msg_ids=["msg_004"],
)

DRIFT_EVACUATION_EXPANSION = DriftEvent(
    id="drift_evacuation",
    name="Evacuation zone expanded",
    description="Mandatory evacuation expanded from Zone A to include Zone B",
    trigger_hour=21.0,
    messages=[
        Message(
            id="msg_037",
            sender="National Weather Service",
            channel=Channel.GOVERNMENT_ALERT,
            subject="EXPANDED: Evacuation zones now include Zone B",
            content=(
                "URGENT UPDATE: The mandatory evacuation order has been expanded to include "
                "Zone B. All Zone B residents must evacuate within 4 hours. This includes "
                "the downtown corridor, Midtown, and East Sacramento. All previously listed "
                "shelters remain active."
            ),
            urgency=Urgency.CRITICAL,
            timestamp_hours=21.0,
            deadline_hours=25.0,
            drift_flag=True,
            supersedes="msg_001",
        ),
        Message(
            id="msg_038",
            sender="Boss",
            channel=Channel.SMS,
            subject="Office is in Zone B - disregard earlier email",
            content=(
                "Well, our office is in Zone B. So obviously disregard the 'come in tomorrow' "
                "thing. But I STILL need those slides. Can you work on them from wherever "
                "you are? Sarah said she can pick up some of the slack but I need to know "
                "what you can deliver. This client won't wait for a hurricane."
            ),
            urgency=Urgency.MEDIUM,
            timestamp_hours=21.5,
            dependencies=["msg_005", "msg_025"],
        ),
    ],
    superseded_msg_ids=["msg_001"],
)

DRIFT_EMPLOYER_POLICY = DriftEvent(
    id="drift_employer",
    name="Employer emergency leave expanded",
    description="HR expands emergency leave from PTO-required to 5 days paid leave",
    trigger_hour=22.5,
    messages=[
        Message(
            id="msg_040",
            sender="HR Department",
            channel=Channel.EMAIL,
            subject="UPDATED: Emergency leave policy expanded",
            content=(
                "UPDATE: Due to the expanded evacuation zones, the emergency leave policy "
                "has been extended. Employees in Zones A and B are granted 5 days of paid "
                "emergency leave effective immediately. You do NOT need to use PTO. "
                "Please still submit the emergency status form on the HR portal."
            ),
            urgency=Urgency.MEDIUM,
            timestamp_hours=22.5,
            drift_flag=True,
            supersedes="msg_006",
        ),
    ],
    superseded_msg_ids=["msg_006"],
)

DRIFT_AIRLINE_TERMS = DriftEvent(
    id="drift_airline",
    name="Airline rebooking window extended",
    description="Delta extends free rebooking from 48h to 7 days",
    trigger_hour=24.5,
    messages=[
        Message(
            id="msg_043",
            sender="Delta Airlines",
            channel=Channel.APP_NOTIFICATION,
            subject="UPDATED: Free rebooking window extended to 7 days",
            content=(
                "Good news: Delta has extended the free rebooking window for all cancelled "
                "flights to 7 days (previously 48 hours). You now have until March 17 to "
                "rebook at no additional charge. Refund option remains available."
            ),
            urgency=Urgency.LOW,
            timestamp_hours=24.5,
            drift_flag=True,
            supersedes="msg_008",
        ),
    ],
    superseded_msg_ids=["msg_008"],
)

DRIFT_FEMA_DOCUMENTATION = DriftEvent(
    id="drift_fema",
    name="FEMA documentation requirements updated",
    description="FEMA adds new documentation requirements for disaster assistance",
    trigger_hour=34.0,
    messages=[
        Message(
            id="msg_055",
            sender="FEMA",
            channel=Channel.GOVERNMENT_ALERT,
            subject="FEMA documentation requirements updated",
            content=(
                "IMPORTANT UPDATE: FEMA disaster assistance applications now require "
                "additional documentation. In addition to standard requirements, applicants "
                "must provide: utility bills from the last 3 months, a signed letter from "
                "landlord confirming tenancy (for renters), and photos of damage with "
                "timestamps. Updated forms available at DisasterAssistance.gov."
            ),
            urgency=Urgency.HIGH,
            timestamp_hours=34.0,
            deadline_hours=48.0,
            drift_flag=True,
            supersedes="msg_024",
        ),
    ],
    superseded_msg_ids=["msg_024"],
)


ALL_DRIFT_EVENTS: list[DriftEvent] = [
    DRIFT_INSURANCE_DEADLINE,
    DRIFT_EVACUATION_EXPANSION,
    DRIFT_EMPLOYER_POLICY,
    DRIFT_AIRLINE_TERMS,
    DRIFT_FEMA_DOCUMENTATION,
]


def select_drift_events(
    count: int = 3,
    rng: random.Random | None = None,
) -> list[DriftEvent]:
    """Randomly select `count` drift events for an episode."""
    r = rng or random.Random()
    return r.sample(ALL_DRIFT_EVENTS, min(count, len(ALL_DRIFT_EVENTS)))
