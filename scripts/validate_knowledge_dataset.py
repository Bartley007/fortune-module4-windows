from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.services.knowledge_dataset import build_source_mapping, validate_records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the upstream knowledge dataset contract."
    )
    parser.add_argument("dataset", type=Path, help="Path to knowledge_sources_pages.json")
    parser.add_argument("--expected-count", type=int, default=None)
    parser.add_argument(
        "--require-source-id",
        action="store_true",
        help="Fail when the dataset does not contain source_id fields.",
    )
    parser.add_argument("--mapping-output", type=Path, default=None)
    parser.add_argument("--report-output", type=Path, default=None)
    return parser.parse_args()


def load_records(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Dataset root must be a JSON array")
    return payload


def main() -> int:
    args = parse_args()
    records = load_records(args.dataset)
    result = validate_records(
        records,
        expected_count=args.expected_count,
        require_source_id=args.require_source_id,
    )

    report = {
        "dataset": str(args.dataset),
        "generated_at": datetime.now(UTC).isoformat(),
        "record_count": result.record_count,
        "source_id_count": result.source_id_count,
        "content_checksum_count": result.content_checksum_count,
        "valid": result.valid,
        "errors": result.errors,
        "warnings": result.warnings,
    }

    if args.report_output:
        args.report_output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    if args.mapping_output:
        mapping = build_source_mapping(records)
        args.mapping_output.write_text(
            json.dumps(
                {
                    "dataset": str(args.dataset),
                    "generated_at": report["generated_at"],
                    "mapping": mapping,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    print(f"records={result.record_count}")
    print(f"source_id_present={result.source_id_count}")
    print(f"content_checksum_present={result.content_checksum_count}")
    print(f"valid={str(result.valid).lower()}")
    print(f"errors={len(result.errors)}")
    print(f"warnings={len(result.warnings)}")
    for error in result.errors[:20]:
        print(f"ERROR: {error}")
    for warning in result.warnings[:5]:
        print(f"WARNING: {warning}")
    if len(result.warnings) > 5:
        print(f"WARNING: ... {len(result.warnings) - 5} more")
    return 0 if result.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())