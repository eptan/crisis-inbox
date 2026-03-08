"""
Schema drift events for the CrisisInbox environment.

Each drift event represents a mid-episode policy/rule change that invalidates
previous information. The agent must detect these changes and adapt.

There are 9 drift events defined. Each episode randomly selects 3 to fire.
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


DRIFT_SHELTER_RELOCATION = DriftEvent(
    id="drift_shelter",
    name="Shelter relocation",
    description="Lincoln High shelter closes due to structural damage; evacuees must relocate",
    trigger_hour=16.0,
    messages=[
        Message(
            id="msg_drift_shelter_01",
            sender="Sacramento County",
            channel=Channel.GOVERNMENT_ALERT,
            subject="URGENT: Lincoln High shelter closing - relocate immediately",
            content=(
                "URGENT: Lincoln High School shelter is being closed effective 8 PM tonight "
                "due to structural concerns identified during inspection. All evacuees must "
                "relocate to Sacramento Convention Center (1400 J St) or Natomas Community "
                "Center (2921 Truxel Rd). Transportation will be provided starting at 5 PM. "
                "If you have your own vehicle, proceed directly. Pet-friendly option: Natomas only."
            ),
            urgency=Urgency.CRITICAL,
            timestamp_hours=16.0,
            deadline_hours=20.0,
            drift_flag=True,
            supersedes="msg_010",
        ),
        Message(
            id="msg_drift_shelter_02",
            sender="Neighbor Dave",
            channel=Channel.SMS,
            subject="Shelter is closing!",
            content=(
                "They're kicking us out of Lincoln High!! Something about the roof structure. "
                "Everyone's scrambling. The buses aren't here yet and people are freaking out. "
                "Convention Center is already packed. If you have ANY room at your place or "
                "know anyone who does, please let me know. There's a family here with a "
                "newborn and nowhere to go."
            ),
            urgency=Urgency.HIGH,
            timestamp_hours=16.5,
        ),
    ],
    superseded_msg_ids=["msg_010"],
)

DRIFT_GAS_RATIONING = DriftEvent(
    id="drift_gas",
    name="Gas rationing implemented",
    description="County implements fuel rationing — odd/even license plate days",
    trigger_hour=18.0,
    messages=[
        Message(
            id="msg_drift_gas_01",
            sender="Sacramento County",
            channel=Channel.GOVERNMENT_ALERT,
            subject="MANDATORY fuel rationing in effect",
            content=(
                "Due to critical fuel shortages, Sacramento County has implemented mandatory "
                "fuel rationing effective immediately. Odd-numbered license plates may purchase "
                "fuel on odd calendar days; even-numbered plates on even days. Maximum 10 gallons "
                "per fill-up. Violators will be fined $500. Rationing is expected to remain in "
                "effect for 5-7 days. Plan travel accordingly."
            ),
            urgency=Urgency.HIGH,
            timestamp_hours=18.0,
            drift_flag=True,
            supersedes="msg_087",
        ),
    ],
    superseded_msg_ids=["msg_087"],
)

DRIFT_PHARMACY_CLOSURE = DriftEvent(
    id="drift_pharmacy",
    name="Pharmacy closures expand",
    description="Multiple pharmacies close; prescription transfer process changes",
    trigger_hour=26.0,
    messages=[
        Message(
            id="msg_drift_pharmacy_01",
            sender="Pharmacy - CVS",
            channel=Channel.SMS,
            subject="UPDATED: Multiple CVS locations closed",
            content=(
                "CVS Health Alert: Due to flood damage and power outages, the following "
                "CVS locations are temporarily closed: #4521 (Florin Rd), #3892 (Arden Way), "
                "#2201 (Freeport Blvd). Your prescription can be transferred to CVS #5580 "
                "(Roseville) or any Walgreens location. To transfer, call 1-800-746-7287. "
                "Emergency 72-hour supplies available at shelters with valid prescription."
            ),
            urgency=Urgency.HIGH,
            timestamp_hours=26.0,
            deadline_hours=40.0,
            drift_flag=True,
            supersedes="msg_028",
        ),
    ],
    superseded_msg_ids=["msg_028"],
)

DRIFT_CURFEW_EXTENDED = DriftEvent(
    id="drift_curfew",
    name="Curfew hours extended",
    description="Curfew expanded from 9PM-6AM to 6PM-8AM due to looting",
    trigger_hour=28.0,
    messages=[
        Message(
            id="msg_drift_curfew_01",
            sender="Sacramento County Sheriff",
            channel=Channel.GOVERNMENT_ALERT,
            subject="UPDATED: Curfew hours extended due to looting",
            content=(
                "Due to increased looting and safety concerns, the curfew in evacuation zones "
                "A and B has been EXTENDED to 6 PM through 8 AM (previously 9 PM to 6 AM). "
                "This takes effect TONIGHT. All non-emergency movement in these zones is "
                "prohibited during curfew hours. Violators will be arrested. If you need to "
                "travel during curfew for medical or emergency reasons, call the non-emergency "
                "line at 555-0199 for a travel authorization."
            ),
            urgency=Urgency.CRITICAL,
            timestamp_hours=28.0,
            drift_flag=True,
            supersedes="msg_034",
        ),
        Message(
            id="msg_drift_curfew_02",
            sender="Sister",
            channel=Channel.SMS,
            subject="Curfew extended - can't get kids tonight",
            content=(
                "Did you see the curfew got moved to 6 PM?? I was going to come get the kids "
                "tonight but there's no way I can make it before 6. I don't want to get "
                "arrested with two car seats in the back. Can you keep them one more night? "
                "I'm so sorry. I'll come first thing in the morning at 8."
            ),
            urgency=Urgency.MEDIUM,
            timestamp_hours=28.5,
            dependencies=["msg_003"],
        ),
    ],
    superseded_msg_ids=["msg_034"],
)

ALL_DRIFT_EVENTS: list[DriftEvent] = [
    DRIFT_INSURANCE_DEADLINE,
    DRIFT_EVACUATION_EXPANSION,
    DRIFT_EMPLOYER_POLICY,
    DRIFT_AIRLINE_TERMS,
    DRIFT_FEMA_DOCUMENTATION,
    DRIFT_SHELTER_RELOCATION,
    DRIFT_GAS_RATIONING,
    DRIFT_PHARMACY_CLOSURE,
    DRIFT_CURFEW_EXTENDED,
]


def select_drift_events(
    count: int = 3,
    rng: random.Random | None = None,
) -> list[DriftEvent]:
    """Randomly select `count` drift events for an episode."""
    r = rng or random.Random()
    return r.sample(ALL_DRIFT_EVENTS, min(count, len(ALL_DRIFT_EVENTS)))
