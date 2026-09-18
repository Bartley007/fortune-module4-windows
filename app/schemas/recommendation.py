from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RecommendationFeatures(BaseModel):
    model_config = ConfigDict(extra="forbid")

    semantic_similarity: float | None = Field(default=None, ge=0, le=1)
    knowledge_graph_relation: float | None = Field(default=None, ge=0, le=1)
    sequence_transition: float | None = Field(default=None, ge=0, le=1)
    historical_feedback: float | None = Field(default=None, ge=0, le=1)
    content_freshness: float | None = Field(default=None, ge=0, le=1)


class RecommendationCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str = Field(min_length=1, max_length=255)
    item_type: str = Field(default="knowledge_item", min_length=1, max_length=64)
    item_id: str = Field(min_length=1, max_length=255)
    source_id: str | None = Field(default=None, max_length=255)
    title: str | None = Field(default=None, max_length=512)
    text: str | None = Field(default=None, max_length=10_000)
    features: RecommendationFeatures = Field(default_factory=RecommendationFeatures)
    source_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class NextActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(min_length=1, max_length=36)
    current_topic: str | None = Field(default=None, max_length=2_000)
    top_k: int = Field(default=3, ge=1, le=20)
    candidates: list[RecommendationCandidate] = Field(default_factory=list)


class RecommendationItem(BaseModel):
    recommendation_id: str
    candidate_id: str
    item_type: str
    item_id: str
    source_id: str | None
    title: str | None
    score: float
    features: dict[str, float]
    effective_weights: dict[str, float]
    reason: str
    source_refs: list[str]
    metadata: dict[str, Any]


class RecommendationResult(BaseModel):
    items: list[RecommendationItem]
    top_k: int
    cold_start: bool
    model_version: str
    scoring_weights: dict[str, float]
