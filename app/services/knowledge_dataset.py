from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlsplit

from app.services.source_ids import content_checksum, stable_source_id_from_record

REQUIRED_TEXT_FIELDS = (
    "url",
    "title",
    "source",
    "source_name",
    "source_type",
    "catalog",
    "content",
)
ALLOWED_SOURCE_TYPES = {"website", "pdf", "bibliography"}


@dataclass
class DatasetValidationResult:
    record_count: int
    source_id_count: int
    content_checksum_count: int
    derived_ids: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors


def validate_records(
    records: list[dict[str, Any]],
    *,
    expected_count: int | None = None,
    require_source_id: bool = False,
) -> DatasetValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    source_id_count = 0
    content_checksum_count = 0
    stable_ids: list[str] = []
    urls: list[str] = []

    if expected_count is not None and len(records) != expected_count:
        errors.append(f"record count is {len(records)}, expected {expected_count}")

    for index, record in enumerate(records):
        location = f"record[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{location} is not an object")
            continue

        for field_name in REQUIRED_TEXT_FIELDS:
            value = record.get(field_name)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{location}.{field_name} is required")

        url = record.get("url")
        source_type = record.get("source_type")
        if isinstance(url, str) and url.strip():
            parsed = urlsplit(url)
            is_http = parsed.scheme in {"http", "https"} and bool(parsed.netloc)
            is_static_pdf = (
                source_type == "pdf"
                and url.startswith("/data/sources/")
                and bool(parsed.fragment)
            )
            if not is_http and not is_static_pdf:
                errors.append(f"{location}.url is not a valid HTTP(S) or static PDF URL")
            urls.append(url)

        if isinstance(source_type, str) and source_type not in ALLOWED_SOURCE_TYPES:
            errors.append(f"{location}.source_type is unsupported: {source_type}")

        categories = record.get("category")
        if not isinstance(categories, list) or not categories:
            errors.append(f"{location}.category must be a non-empty list")
        elif any(not isinstance(category, str) or not category.strip() for category in categories):
            errors.append(f"{location}.category contains an invalid value")

        blocks = record.get("content_blocks")
        if not isinstance(blocks, list):
            errors.append(f"{location}.content_blocks must be a list")
        else:
            for block_index, block in enumerate(blocks):
                block_location = f"{location}.content_blocks[{block_index}]"
                if not isinstance(block, dict):
                    errors.append(f"{block_location} is not an object")
                    continue
                for field_name in ("type", "text"):
                    value = block.get(field_name)
                    if not isinstance(value, str) or not value.strip():
                        errors.append(f"{block_location}.{field_name} is required")

        if record.get("source_id"):
            source_id_count += 1
        elif require_source_id:
            errors.append(f"{location}.source_id is required by the Module 4 contract")
        else:
            warnings.append(f"{location}.source_id missing; a derived public ID will be used")

        if record.get("content_checksum"):
            content_checksum_count += 1

        stable_ids.append(stable_source_id_from_record(record))

    duplicates = _duplicates(urls)
    if duplicates:
        errors.append(f"duplicate URLs: {', '.join(sorted(duplicates))}")

    duplicate_ids = _duplicates(stable_ids)
    if duplicate_ids:
        errors.append(f"derived source_id collisions: {', '.join(sorted(duplicate_ids))}")

    return DatasetValidationResult(
        record_count=len(records),
        source_id_count=source_id_count,
        content_checksum_count=content_checksum_count,
        derived_ids=stable_ids,
        errors=errors,
        warnings=warnings,
    )


def build_source_mapping(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    mapping: list[dict[str, str]] = []
    for record in records:
        mapping.append(
            {
                "url": str(record.get("url") or ""),
                "title": str(record.get("title") or ""),
                "source_id": stable_source_id_from_record(record),
                "content_checksum": content_checksum(str(record.get("content") or "")),
            }
        )
    return mapping


def _duplicates(values: list[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates