from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class Envelope(BaseModel, Generic[T]):
    model_config = ConfigDict(extra="forbid")

    result: T | None = None
    source_refs: list[str] = Field(default_factory=list)
    system: str = "unknown"
    session_id: str | None = None
    warnings: list[str] = Field(default_factory=list)
    error: ErrorDetail | None = None


def success_envelope(
    result: T,
    *,
    system: str,
    session_id: str | None = None,
    source_refs: list[str] | None = None,
    warnings: list[str] | None = None,
) -> Envelope[T]:
    return Envelope[T](
        result=result,
        source_refs=source_refs or [],
        system=system,
        session_id=session_id,
        warnings=warnings or [],
    )
