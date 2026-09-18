from fastapi.testclient import TestClient

from tests.conftest import headers


def test_collections_notes_tags_export_and_delete(client: TestClient) -> None:
    collection = client.post(
        "/api/v1/me/collections",
        headers=headers(),
        json={
            "item_type": "knowledge_item",
            "source_id": "source:yijing",
            "title": "Yijing passage",
            "source_metadata": {"content_checksum": "sha256:abc"},
        },
    )
    assert collection.status_code == 201
    collection_id = collection.json()["result"]["collection_id"]

    note = client.post(
        "/api/v1/me/notes",
        headers=headers(),
        json={
            "source_id": "source:yijing",
            "collection_id": collection_id,
            "title": "My note",
            "body": "Private interpretation note",
            "tags": ["yijing", "private"],
            "source_refs": ["source:yijing"],
        },
    )
    assert note.status_code == 200
    assert note.json()["result"]["tags"] == ["yijing", "private"]

    tags = client.get("/api/v1/me/tags", headers=headers())
    assert tags.status_code == 200
    assert {tag["name"] for tag in tags.json()["result"]} == {"yijing", "private"}

    exported = client.post("/api/v1/me/exports", headers=headers())
    assert exported.status_code == 201
    exported_body = exported.json()["result"]
    assert "source:yijing" in exported_body["source_manifest"]
    assert len(exported_body["data"]["notes"]) == 1

    deleted = client.delete("/api/v1/me/data?confirm=true", headers=headers())
    assert deleted.status_code == 200
    assert deleted.json()["result"]["status"] == "deleted"

    collections = client.get("/api/v1/me/collections", headers=headers())
    assert collections.json()["result"] == []


def test_private_collections_are_isolated_by_user(client: TestClient) -> None:
    response = client.post(
        "/api/v1/me/collections",
        headers=headers("user-a"),
        json={"item_type": "knowledge_item", "source_id": "source:private"},
    )
    assert response.status_code == 201

    other_user = client.get("/api/v1/me/collections", headers=headers("user-b"))
    assert other_user.status_code == 200
    assert other_user.json()["result"] == []


def test_privacy_defaults_and_updates(client: TestClient) -> None:
    default = client.get("/api/v1/me/privacy", headers=headers("privacy-user"))
    assert default.status_code == 200
    assert default.json()["result"]["allow_anonymous_cases"] is False

    updated = client.put(
        "/api/v1/me/privacy",
        headers=headers("privacy-user"),
        json={
            "consent_scopes": ["session_storage", "anonymous_case_matching"],
            "retention_policy": "30d",
            "allow_anonymous_cases": True,
            "allow_shared_training": False,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["result"]["allow_anonymous_cases"] is True
    assert updated.json()["result"]["retention_policy"] == "30d"
