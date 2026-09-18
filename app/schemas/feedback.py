from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class FeedbackCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str | None = Field(default=None, max_length=36)
    event_id: str | None = Field(default=None, max_length=36)
    item_id: str | None = Field(default=None, max_length=255)
    source_id: str | None = Field(default=None, max_length=255)
    feedback_type: str = Field(min_length=1, max_length=64)
    rating: float | None = Field(default=None, ge=0, le=5)
    text: str | None = Field(default=None, max_length=10_000)
    payload: dict[str, Any] = Field(default_factory=dict)
    source_refs: list[str] = Field(default_factory=list)


class FeedbackOut(BaseModel):
    feedback_id: str
    user_id: str
    session_id: str | None
    event_id: str | None
    item_id: str | None
    source_id: str | None
    feedback_type: str
    rating: float | None
    text: str | None
    payload: dict[str, Any]
    source_refs: list[str]
    created_at: datetime
