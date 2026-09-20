from __future__ import annotations

import os
from datetime import UTC, datetime
from uuid import uuid4

import httpx

BASE_URL = os.getenv("MODULE4_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
TIMEOUT_SECONDS = float(os.getenv("MODULE4_VERIFY_TIMEOUT", "600"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    user_id = f"e2e-{uuid4().hex[:12]}"
    other_user_id = f"e2e-other-{uuid4().hex[:12]}"
    headers = {"X-User-Id": user_id}
    other_headers = {"X-User-Id": other_user_id}
    session_id = f"e2e-session-{uuid4().hex[:12]}"
    event_id = str(uuid4())
    idempotency_key = f"e2e-key-{uuid4().hex}"

    with httpx.Client(base_url=BASE_URL, timeout=TIMEOUT_SECONDS) as client:
        health = client.get("/health")
        health.raise_for_status()
        require(health.json().get("status") == "ok", "health check failed")
        print("[OK] health")

        privacy = client.put(
            "/api/v1/me/privacy",
            headers=headers,
            json={
                "consent_scopes": ["session_storage", "anonymous_case_matching"],
                "retention_policy": "standard",
                "allow_anonymous_cases": True,
                "allow_shared_training": False,
            },
        )
        privacy.raise_for_status()
        require(privacy.json()["result"]["allow_anonymous_cases"] is True, "privacy update failed")
        print("[OK] privacy")

        compat_session_id = f"compat-{uuid4().hex[:12]}"
        compat_event_id = str(uuid4())
        compat_event = {
            "session_id": compat_session_id,
            "event_id": compat_event_id,
            "event_type": "question",
            "module": "bazi",
            "user_id": user_id,
            "payload": {
                "question": "E2E compatibility event",
                "source_ref": "source:e2e-compat",
            },
        }
        first_compat_event = client.post("/api/session/event", json=compat_event)
        first_compat_event.raise_for_status()
        require(first_compat_event.json()["meta"]["mock"] is False, "compat event envelope failed")
        duplicate_compat_event = client.post("/api/session/event", json=compat_event)
        duplicate_compat_event.raise_for_status()
        require(
            duplicate_compat_event.json()["result"]["duplicate"] is True,
            "compat event idempotency failed",
        )

        compat_note = client.post(
            "/api/user/notes",
            json={
                "user_id": user_id,
                "title": "E2E compatibility note",
                "content": "Created through the frontend compatibility route.",
                "tags": ["compat"],
                "source_ref": "source:e2e-compat",
                "action": "create",
            },
        )
        compat_note.raise_for_status()
        compat_note_id = compat_note.json()["result"]["note_id"]
        deleted_compat_note = client.post(
            "/api/user/notes",
            json={"user_id": user_id, "note_id": compat_note_id, "action": "delete"},
        )
        deleted_compat_note.raise_for_status()
        require(
            deleted_compat_note.json()["result"]["deleted"] is True,
            "compat note deletion failed",
        )
        print("[OK] frontend compatibility routes")

        created_session = client.post(
            "/api/v1/sessions",
            headers=headers,
            json={"session_id": session_id, "system": "bazi", "title": "E2E verification"},
        )
        created_session.raise_for_status()
        session_result = created_session.json()["result"]
        require(session_result["session"]["session_id"] == session_id, "session creation failed")
        print("[OK] session")

        event = {
            "event_id": event_id,
            "session_id": session_id,
            "source_module": "module1",
            "event_type": "module1.chart.completed",
            "sequence_no": 1,
            "occurred_at": datetime.now(UTC).isoformat(),
            "system": "bazi",
            "payload": {
                "chart_id": f"chart-{uuid4().hex[:8]}",
                "chart_features": {
                    "day_master": "wood",
                    "five_elements": {"wood": 0.4, "fire": 0.3, "earth": 0.3},
                    "strength": "balanced",
                    "pattern": "balanced_qi",
                },
                "rule_version": "e2e-rules-v1",
            },
            "source_refs": ["source:e2e-chart"],
            "schema_version": "1.0",
        }
        ingest_headers = {**headers, "X-Idempotency-Key": idempotency_key}
        first_event = client.post("/api/v1/events/ingest", headers=ingest_headers, json=event)
        first_event.raise_for_status()
        require(first_event.json()["result"]["duplicate"] is False, "first event marked duplicate")
        second_event = client.post("/api/v1/events/ingest", headers=ingest_headers, json=event)
        second_event.raise_for_status()
        require(second_event.json()["result"]["duplicate"] is True, "event idempotency failed")
        events = client.get(f"/api/v1/sessions/{session_id}/events", headers=headers)
        events.raise_for_status()
        require(len(events.json()["result"]) == 1, "event count mismatch")
        print("[OK] event ingestion and idempotency")

        recommendation = client.post(
            "/api/v1/recommendations/next",
            headers=headers,
            json={
                "session_id": session_id,
                "top_k": 1,
                "candidates": [
                    {
                        "candidate_id": "e2e-candidate",
                        "item_id": "e2e-knowledge",
                        "source_id": "source:e2e-chart",
                        "title": "E2E knowledge",
                        "features": {
                            "semantic_similarity": 1.0,
                            "knowledge_graph_relation": 1.0,
                            "sequence_transition": 1.0,
                            "historical_feedback": 1.0,
                            "content_freshness": 1.0,
                        },
                        "source_refs": ["source:e2e-chart"],
                    }
                ],
            },
        )
        recommendation.raise_for_status()
        recommendation_result = recommendation.json()["result"]
        require(recommendation_result["items"][0]["score"] == 1.0, "ranking score failed")
        require(
            "qwen3.8:27b-q8_0" in recommendation_result["model_version"],
            "remote Qwen model was not used for recommendation explanation",
        )
        require(
            bool(recommendation_result["items"][0]["reason"]),
            "recommendation explanation missing",
        )
        print("[OK] recommendation and remote Qwen explanation")

        feedback = client.post(
            "/api/v1/feedback",
            headers=headers,
            json={
                "session_id": session_id,
                "item_id": "e2e-knowledge",
                "source_id": "source:e2e-chart",
                "feedback_type": "helpful",
                "rating": 5,
            },
        )
        feedback.raise_for_status()
        require(feedback.json()["result"]["feedback_type"] == "helpful", "feedback failed")
        print("[OK] feedback")

        collection = client.post(
            "/api/v1/me/collections",
            headers=headers,
            json={
                "item_type": "knowledge_item",
                "source_id": "source:e2e-chart",
                "title": "E2E collection",
            },
        )
        collection.raise_for_status()
        collection_id = collection.json()["result"]["collection_id"]

        note = client.post(
            "/api/v1/me/notes",
            headers=headers,
            json={
                "source_id": "source:e2e-chart",
                "collection_id": collection_id,
                "title": "E2E note",
                "body": "Private note created by end-to-end verification.",
                "tags": ["e2e", "verification"],
                "source_refs": ["source:e2e-chart"],
            },
        )
        note.raise_for_status()
        note_id = note.json()["result"]["note_id"]

        collections = client.get("/api/v1/me/collections", headers=headers)
        collections.raise_for_status()
        require(len(collections.json()["result"]) == 1, "collection list failed")

        notes = client.get("/api/v1/me/notes", headers=headers)
        notes.raise_for_status()
        require(notes.json()["result"][0]["note_id"] == note_id, "note list failed")

        tags = client.get("/api/v1/me/tags", headers=headers)
        tags.raise_for_status()
        tag_names = {item["name"] for item in tags.json()["result"]}
        require({"e2e", "verification"} <= tag_names, "tag list failed")
        print("[OK] collections, notes, and tags")

        other_collections = client.get("/api/v1/me/collections", headers=other_headers)
        other_collections.raise_for_status()
        other_notes = client.get("/api/v1/me/notes", headers=other_headers)
        other_notes.raise_for_status()
        require(other_collections.json()["result"] == [], "collection isolation failed")
        require(other_notes.json()["result"] == [], "note isolation failed")
        print("[OK] user isolation")

        exported = client.post("/api/v1/me/exports", headers=headers)
        exported.raise_for_status()
        export_data = exported.json()["result"]["data"]
        require(len(export_data["notes"]) == 1, "export notes failed")
        require(len(export_data["collections"]) == 1, "export collections failed")
        print("[OK] export")

        similar = client.post(
            "/api/v1/cases/similar",
            headers=headers,
            json={
                "threshold": 0.6,
                "features": {
                    "chart_structure": {
                        "day_master": "wood",
                        "five_elements": {"wood": 0.4, "fire": 0.3, "earth": 0.3},
                        "strength": "balanced",
                        "pattern": "balanced_qi",
                    }
                },
            },
        )
        similar.raise_for_status()
        similar_items = similar.json()["result"]["items"]
        require(bool(similar_items), "similar case result missing")
        require(similar_items[0]["score"] == 1.0, "similar case score failed")
        require(bool(similar_items[0]["explanation"]), "similar case explanation missing")
        print("[OK] similar case and remote Qwen explanation")

        deleted = client.delete("/api/v1/me/data", headers=headers, params={"confirm": "true"})
        deleted.raise_for_status()
        require(deleted.json()["result"]["status"] == "deleted", "delete data failed")

        collections_after = client.get("/api/v1/me/collections", headers=headers)
        collections_after.raise_for_status()
        notes_after = client.get("/api/v1/me/notes", headers=headers)
        notes_after.raise_for_status()
        privacy_after = client.get("/api/v1/me/privacy", headers=headers)
        privacy_after.raise_for_status()
        require(collections_after.json()["result"] == [], "collections remained after deletion")
        require(notes_after.json()["result"] == [], "notes remained after deletion")
        require(
            privacy_after.json()["result"]["allow_anonymous_cases"] is False,
            "privacy reset failed",
        )
        print("[OK] export and deletion already verified; deletion cleanup complete")

    print(f"END-TO-END VERIFICATION PASSED for user_id={user_id}")


if __name__ == "__main__":
    main()