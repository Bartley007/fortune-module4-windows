# Knowledge Dataset Validation

Module 4 includes a validator for the upstream `knowledge_sources_pages.json` contract:

```bash
.venv/bin/python scripts/validate_knowledge_dataset.py \
  ../fortune/data/knowledge_sources_complete/knowledge_sources_pages.json \
  --expected-count 764
```

## Verified Upstream Dataset

Checked source commit: `d82f2a0`.

Results:

- 764 records.
- Required text fields complete.
- Valid source types: `website`, `pdf`, `bibliography`.
- Valid categories: `original`, `commentary`, `translation`, `modern_commentary`.
- 764 records contain structured `content_blocks`.
- No duplicate URLs.
- 343 PDF records use valid root-relative static paths such as
  `/data/sources/qiongtong-baojian.pdf#chapter-...`.
- 764 derived stable `source_id` values are unique.

## Strict Contract Gap

The upstream dataset does not currently contain:

- `source_id`
- `content_checksum`

Run strict validation with:

```bash
.venv/bin/python scripts/validate_knowledge_dataset.py \
  ../fortune/data/knowledge_sources_complete/knowledge_sources_pages.json \
  --expected-count 764 \
  --require-source-id
```

This reports 764 missing `source_id` errors, so the dataset is not strictly compliant with the
Module 4 public-reference contract yet.

Module 4 remains compatible by generating deterministic IDs from canonical URLs. URL fragments are
preserved because they identify distinct chapters. A reusable mapping can be generated with:

```bash
.venv/bin/python scripts/validate_knowledge_dataset.py \
  ../fortune/data/knowledge_sources_complete/knowledge_sources_pages.json \
  --expected-count 764 \
  --mapping-output knowledge_source_id_map.json
```

The mapping contains a stable `source_id` and `content_checksum` for every record. This does not
modify the upstream data file.