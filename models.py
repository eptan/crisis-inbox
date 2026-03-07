"""
CrisisInbox Data Models.

Core data model for the crisis inbox environment: messages arriving across
multiple channels during a 48-hour post-disaster scenario.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Channel(str, Enum):
    """Communication channel a message arrives on."""
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    GOVERNMENT_ALERT = "government_alert"
    APP_NOTIFICATION = "app_notification"
    SOCIAL_MEDIA = "social_media"


class Urgency(str, Enum):
    """Urgency level of a message."""
    CRITICAL = "critical"      # Life-safety, immediate action required
    HIGH = "high"              # Time-sensitive deadline (hours)
    MEDIUM = "medium"          # Important but can wait (days)
    LOW = "low"                # Informational, no deadline


class Message(BaseModel):
    """
    A message arriving in the crisis inbox.

    Represents a single communication from any sender across any channel
    during a post-disaster scenario. Messages may have deadlines, depend
    on other messages/actions, and may be affected by schema drift (changing
    rules mid-episode).
    """
    id: str = Field(description="Unique message identifier")
    sender: str = Field(description="Who sent the message (e.g. 'FEMA', 'Mom', 'State Farm')")
    channel: Channel = Field(description="Communication channel")
    subject: str = Field(description="Brief subject line")
    content: str = Field(description="Full message body")
    urgency: Urgency = Field(description="Urgency level")
    timestamp_hours: float = Field(
        description="Hours since disaster onset (0-48)",
        ge=0.0,
        le=48.0,
    )
    deadline_hours: Optional[float] = Field(
        default=None,
        description="Hours since disaster onset by which action must be taken",
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="IDs of messages that must be handled before this one can be resolved",
    )
    drift_flag: bool = Field(
        default=False,
        description="Whether this message represents a schema drift event "
        "(policy change, deadline shift, rule update)",
    )
    supersedes: Optional[str] = Field(
        default=None,
        description="ID of a previous message this one replaces (due to drift)",
    )
