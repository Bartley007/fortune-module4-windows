from __future__ import annotations

import hashlib
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def canonicalize_url(url: str) -> str:
    value = url.strip()
    if not value:
        return ""
    parts = urlsplit(value)
    if not parts.scheme or not parts.netloc:
        return value
    query = urlencode(sorted(parse_qsl(parts.query, keep_blank_values=True)))
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, query, parts.fragment))


def stable_source_id_from_url(url: str) -> str:
    canonical = canonicalize_url(url)
    if not canonical:
        raise ValueError("A non-empty URL is required")
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:32]
    return f"source:{digest}"


def stable_source_id_from_record(record: dict[str, Any]) -> str:
    url = record.get("url")
    if isinstance(url, str) and url.strip():
        return stable_source_id_from_url(url)

    source = str(record.get("source") or "")
    title = str(record.get("title") or "")
    catalog = str(record.get("catalog") or "")
    content = str(record.get("content") or "")
    material = "\0".join((source, title, catalog, content))
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]
    return f"source:{digest}"


def content_checksum(content: str) -> str:
    return f"sha256:{hashlib.sha256(content.encode('utf-8')).hexdigest()}"