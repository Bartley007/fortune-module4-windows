import pytest

from app.services.source_ids import (
    canonicalize_url,
    content_checksum,
    stable_source_id_from_record,
    stable_source_id_from_url,
)


def test_url_canonicalization_is_stable() -> None:
    first = stable_source_id_from_url("HTTPS://Example.com/path/?b=2&a=1#section")
    second = stable_source_id_from_url("https://example.com/path?a=1&b=2#section")
    without_fragment = stable_source_id_from_url("https://example.com/path?a=1&b=2")
    assert first == second
    assert first != without_fragment
    assert canonicalize_url("https://example.com/path/#x") == "https://example.com/path#x"


def test_record_fallback_uses_content_when_url_is_absent() -> None:
    first = stable_source_id_from_record(
        {"source": "ctext", "title": "Example", "catalog": "A", "content": "text"}
    )
    second = stable_source_id_from_record(
        {"source": "ctext", "title": "Example", "catalog": "A", "content": "text"}
    )
    assert first == second
    assert first.startswith("source:")


def test_source_id_rejects_empty_url() -> None:
    with pytest.raises(ValueError):
        stable_source_id_from_url("")


def test_content_checksum_is_sha256() -> None:
    assert content_checksum("hello").startswith("sha256:")