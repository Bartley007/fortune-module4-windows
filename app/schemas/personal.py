from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CollectionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_type: str = Field(default="knowledge_item", min_length=1, max_length=64)
    source_id: str | None = Field(default=None, max_length=255)
    snapshot_id: str | None = Field(default=None, max_length=255)
    title: str | None = Field(default=None, max_length=512)
    source_metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def require_reference(self) -> "CollectionCreate":
        if not self.source_id and not self.snapshot_id:
            raise ValueError("source_id or snapshot_id is required")
        return self


class CollectionOut(BaseModel):
    collection_id: str
    user_id: str
    item_type: str
    source_id: str | None
    snapshot_id: str | None
    title: str | None
    source_metadata: dict[str, Any]
    created_at: datetime


class NoteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    note_id: str | None = Field(default=None, max_length=36)
    source_id: str | None = Field(default=None, max_length=255)
    collection_id: str | None = Field(default=None, max_length=36)
    title: str | None = Field(default=None, max_length=255)
    body: str = Field(min_length=1, max_length=100_000)
    tags: list[str] = Field(default_factory=list, max_length=50)
    source_refs: list[str] = Field(default_factory=list)


class NoteOut(BaseModel):
    note_id: str
    user_id: str
    source_id: str | None
    collection_id: str | None
    title: str | None
    body: str
    tags: list[str]
    source_refs: list[str]
    created_at: datetime
    updated_at: datetime


class TagCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=128)


class TagOut(BaseModel):
    tag_id: str
    name: str
    created_at: datetime


class ExportJobOut(BaseModel):
    export_id: str
    user_id: str
    status: str
    created_at: datetime
    completed_at: datetime | None
    source_manifest: list[str]
    data: dict[str, Any]


class DeleteDataResult(BaseModel):
    user_id: str
    status: str
    deleted_at: datetime
    deleted_counts: dict[str, int]


class PrivacyOut(BaseModel):
    user_id: str
    consent_scopes: list[str]
    retention_policy: str
    allow_anonymous_cases: bool
    allow_shared_training: bool
    updated_at: datetime


class PrivacyUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    consent_scopes: list[str] = Field(default_factory=list)
    retention_policy: str = Field(default="standard", min_length=1, max_length=64)
    allow_anonymous_cases: bool = False
    allow_shared_training: bool = False
