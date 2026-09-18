# Cross-Module Input Contract

Module 4 consumes already-computed structured results. It does not recalculate Module 1 or
Module 2 facts and it does not mutate Module 3 public knowledge.

Every event must provide:

```json
{
  "event_id": "uuid",
  "session_id": "uuid",
  "user_id": "pseudonymous-id",
  "source_module": "module1 | module2a | module2b | module3 | frontend",
  "event_type": "module2a.divination.completed",
  "sequence_no": 1,
  "occurred_at": "2026-09-18T10:30:00+08:00",
  "system": "bazi | divination | sign",
  "payload": {},
  "source_refs": ["source-id"],
  "schema_version": "1.0"
}
```

## Module 1

Required payload: `chart_id`, structured chart features, day master, five elements, strength,
pattern, useful god, luck cycle, annual cycle, `rule_version`, and `source_refs`.

## Module 2A

Required payload: `divination_id`, method, input numbers or time data, primary hexagram, changed
hexagram, mutual hexagram, moving lines, `sign_collection`, `sign_no`, `sign_poem`, fortune level,
traditional explanation, `rule_version`, `deterministic_hash`, and `source_refs`.

## Module 2B

Required payload: intent, missing fields, display blocks separated into `original`, `commentary`,
`translation`, and `ai_explanation`, visualization events, model name/version, prompt version,
warnings, and per-block `source_refs`.

## Module 3

Use `source_id` as the only public reference key. Module 4 also accepts `content_checksum` so a
private collection or note can retain its source version and show a version-change warning.

## Frontend

Recommended event types: `session.started`, `knowledge.item.opened`, `recommendation.impression`,
`recommendation.click`, `collection.created`, `note.created`, `tag.assigned`, and
`feedback.submitted`.

Do not send raw identity data. The authentication service provides the pseudonymous `user_id` used
in `X-User-Id` or the event body.
