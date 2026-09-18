from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class CaseFeatures(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chart_structure: dict[str, Any] = Field(default_factory=dict)
    hexagram_path: dict[str, Any] = Field(default_factory=dict)
    topic_symbol: dict[str, Any] = Field(default_factory=dict)
    session_sequence: list[Any] = Field(default_factory=list)


class SimilarCaseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str | None = Field(default=None, max_length=36)
    features: CaseFeatures = Field(validation_alias=AliasChoices("features", "current_features"))
    top_k: int = Field(default=3, ge=1, le=10)
    threshold: float | None = Field(default=None, ge=0, le=1)


class SimilarCaseItem(BaseModel):
    case_key: str
    score: float
    feature_scores: dict[str, float]
    effective_weights: dict[str, float]
    similarities: list[str]
    key_differences: list[str]
    anonymized_features: dict[str, Any]


class SimilarCaseResult(BaseModel):
    items: list[SimilarCaseItem]
    threshold: float
    algorithm_version: str
