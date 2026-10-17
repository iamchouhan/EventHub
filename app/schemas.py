from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EventCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str = Field(default="", max_length=2000)
    location: str = Field(min_length=2, max_length=200)
    starts_at: datetime
    ends_at: datetime
    is_published: bool = False

    @model_validator(mode="after")
    def validate_schedule(self):
        if self.starts_at.tzinfo is None or self.ends_at.tzinfo is None:
            raise ValueError("Event dates must include a timezone")

        if self.ends_at <= self.starts_at:
            raise ValueError("Event end must be after its start")

        return self


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=150)
    description: str | None = Field(default=None, max_length=2000)
    location: str | None = Field(default=None, min_length=2, max_length=200)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    is_published: bool | None = None


class EventResponse(EventCreate):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)