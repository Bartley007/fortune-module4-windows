from fastapi.testclient import TestClient

from tests.conftest import headers


def create_session(client: TestClient, user_id: str = "user-a") -> str:
    response = client.post(
        "/api/v1/sessions",
        headers=headers(user_id),
        json={"system": "divination", "title": "integration session"},
    )
    assert response.status_code == 200
    return response.json()["result"]["session"]["session_id"]


def event_payload(session_id: str, sequence_no: int) -> dict[str, object]:
    return {
        "event_id": f"00000000-0000-0000-0000-{sequence_no:012d}",
        "session_id": session_id,
        "source_module": "module2a",
        "event_type": "module2a.divination.completed",
        "sequence_no": sequence_no,
        "occurred_at": f"2026-09-18T10:3{sequence_no}:00+08:00",
        "system": "divination",
        "payload": {
            "divination_id": f"div-{sequence_no}",
            "method": "meihua",
            "primary_hexagram": {"number": 1, "name": "qian"},
            "moving_lines": [2],
            "rule_version": "rules-1.0",
            "deterministic_hash": f"sha256:div-{sequence_no}",
        },
        "source_refs": ["source:zhouyi"],
        "schema_version": "1.0",
    }


def test_event_ingestion_is_idempotent_and_ordered(client: TestClient) -> None:
    session_id = create_session(client)
    first = event_payload(session_id, 1)
    second = event_payload(session_id, 2)

    response = client.post(
        "/api/v1/events/ingest",
        headers={**headers(), "X-Idempotency-Key": "event-key-1"},
        json=first,
    )
    assert response.status_code == 200
    assert response.json()["result"]["duplicate"] is False

    response = client.post(
        "/api/v1/events/ingest",
        headers={**headers(), "X-Idempotency-Key": "event-key-2"},
        json=second,
    )
    assert response.status_code == 200

    duplicate = client.post(
        "/api/v1/events/ingest",
        headers={**headers(), "X-Idempotency-Key": "event-key-1"},
        json=first,
    )
    assert duplicate.status_code == 200
    assert duplicate.json()["result"]["duplicate"] is True

    events = client.get(f"/api/v1/sessions/{session_id}/events", headers=headers())
    assert events.status_code == 200
    sequence_numbers = [item["sequence_no"] for item in events.json()["result"]]
    assert sequence_numbers == [1, 2]


def test_session_events_are_isolated_by_user(client: TestClient) -> None:
    session_id = create_session(client, "user-a")
    response = client.get(
        f"/api/v1/sessions/{session_id}/events",
        headers=headers("user-b"),
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
