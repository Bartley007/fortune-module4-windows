from typing import Any

from app.services.knowledge_dataset import build_source_mapping, validate_records
from app.services.source_ids import stable_source_id_from_url


def record(url: str = "https://example.com/a") -> dict[str, Any]:
    return {
        "url": url,
        "title": "Example",
        "source": "example",
        "source_name": "Example Source",
        "source_type": "website",
        "catalog": "A -> B",
        "category": ["original"],
        "content": "Example content",
        "content_blocks": [{"type": "original", "text": "Example content"}],
    }


def test_valid_dataset_without_source_id_uses_derived_ids() -> None:
    result = validate_records([record()], expected_count=1)
    assert result.valid
    assert result.source_id_count == 0
    assert result.derived_ids == [stable_source_id_from_url("https://example.com/a")]
    assert result.warnings


def test_require_source_id_reports_contract_gap() -> None:
    result = validate_records([record()], expected_count=1, require_source_id=True)
    assert not result.valid
    assert any("source_id is required" in error for error in result.errors)


def test_duplicate_url_and_invalid_structure_are_errors() -> None:
    result = validate_records([record(), record()], expected_count=2)
    assert not result.valid
    assert any("duplicate URLs" in error for error in result.errors)


def test_source_mapping_contains_stable_ids_and_checksums() -> None:
    mapping = build_source_mapping([record()])
    assert mapping[0]["source_id"].startswith("source:")
    assert mapping[0]["content_checksum"].startswith("sha256:")