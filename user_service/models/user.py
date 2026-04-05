"""
Main User model that combines all user-related data.
"""

from datetime import date, datetime
from typing import List, Set
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator

from .enums import CategoryName, Weekday
from .interests import Interest, NotInterested
from .manual_config import ManualConfig


class ScheduledContent(BaseModel):
    """Content scheduled for a specific rule."""

    allowed_categories: Set[CategoryName] = Field(default_factory=set)
    youtube_channels: Set[str] = Field(default_factory=set)
    # Easy to add more dimensions here later (podcasts, topics, etc.)


class ScheduleRule(BaseModel):
    """A rule that defines when specific content is scheduled."""

    rule_type: str  # "WEEKDAY". Future: "MONTHDAY", "DATE", "ALWAYS"
    rule_value: str  # "MONDAY", "1", "2024-04-05", etc.
    content: ScheduledContent

    def matches(self, target_date: date) -> bool:
        """Check if the rule matches the given date."""
        if self.rule_type == "WEEKDAY":
            return target_date.strftime("%A").upper() == self.rule_value.upper()
        # Future rules:
        # if self.rule_type == "MONTHDAY":
        #    return str(target_date.day) == self.rule_value
        # if self.rule_type == "DATE":
        #    return target_date.isoformat() == self.rule_value
        # if self.rule_type == "ALWAYS":
        #    return True
        return False

    @validator("rule_value")
    def validate_rule_value(cls, v, values):
        """Validate rule_value based on rule_type."""
        rule_type = values.get("rule_type")
        if rule_type == "WEEKDAY":
            if v.upper() not in [wd.value for wd in Weekday]:
                raise ValueError(f"Invalid weekday: {v}")
        return v


class UserSchedule(BaseModel):
    """User's schedule consisting of multiple rules."""

    rules: List[ScheduleRule] = Field(default_factory=list)

    def get_scheduled_content_list_for_date(
        self, target_date: date
    ) -> List[ScheduledContent]:
        """Get the list of scheduled content for a specific date."""
        return [rule.content for rule in self.rules if rule.matches(target_date)]


class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    name: str = Field(..., min_length=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    max_reading_time_per_day_mins: int = Field(..., gt=0)
    interested: List[Interest] = Field(default_factory=list)
    not_interested: List[NotInterested] = Field(default_factory=list)
    manual_configs: ManualConfig = Field(default_factory=ManualConfig)
    schedule: UserSchedule = Field(default_factory=UserSchedule)

    @validator("created_at")
    def validate_created_at(cls, v):
        if not isinstance(v, datetime):
            raise ValueError("created_at must be a datetime object")
        return v

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() + "Z", UUID: str}
