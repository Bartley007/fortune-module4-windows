import os

from app.core.database import SessionLocal, init_database
from app.schemas.event import EventIngestRequest
from app.schemas.personal import PrivacyUpdate
from app.services.events import ingest_event
from app.services.privacy import update_privacy

DEMO_USER = os.getenv("DEMO_USER_ID", "demo-user")
PEER_USER = os.getenv("DEMO_PEER_ID", "demo-peer")
SESSION_ID = "demo-session-001"
PEER_SESSION_ID = "demo-peer-session-001"


def main() -> None:
    init_database()
    with SessionLocal() as db:
        update_privacy(
            db,
            DEMO_USER,
            PrivacyUpdate(
                consent_scopes=["session_storage"],
                retention_policy="standard",
                allow_anonymous_cases=False,
                allow_shared_training=False,
            ),
        )
        update_privacy(
            db,
            PEER_USER,
            PrivacyUpdate(
                consent_scopes=["session_storage", "anonymous_case_matching"],
                retention_policy="standard",
                allow_anonymous_cases=True,
                allow_shared_training=False,
            ),
        )

        ingest_event(
            db,
            PEER_USER,
            EventIngestRequest(
                event_id="10000000-0000-0000-0000-000000000001",
                session_id=PEER_SESSION_ID,
                source_module="module1",
                event_type="module1.chart.completed",
                sequence_no=1,
                system="bazi",
                payload={
                    "chart_id": "demo-chart-001",
                    "chart_features": {
                        "day_master": "wood",
                        "five_elements": {"wood": 0.4, "fire": 0.3, "earth": 0.3},
                        "strength": "balanced",
                        "pattern": "balanced_qi",
                    },
                },
                source_refs=["source:demo-bazi-reference"],
            ),
            "demo-chart-event-001",
        )
        ingest_event(
            db,
            DEMO_USER,
            EventIngestRequest(
                event_id="10000000-0000-0000-0000-000000000002",
                session_id=SESSION_ID,
                source_module="module2a",
                event_type="module2a.divination.completed",
                sequence_no=1,
                system="divination",
                payload={
                    "divination_id": "demo-divination-001",
                    "method": "meihua",
                    "primary_hexagram": {"number": 1, "name": "qian"},
                    "moving_lines": [2],
                    "rule_version": "rules-1.0",
                    "deterministic_hash": "sha256:demo-divination-001",
                },
                source_refs=["source:demo-zhouyi-reference"],
            ),
            "demo-divination-event-001",
        )

    print("Demo data is ready.")
    print(f"Session: {SESSION_ID}")
    print(f"User header: X-User-Id: {DEMO_USER}")
    print()
    print("Recommendation request:")
    print(
        "curl -sS http://127.0.0.1:8000/api/v1/recommendations/next "
        f"-H 'Content-Type: application/json' -H 'X-User-Id: {DEMO_USER}' "
        f'-d \'{{"session_id":"{SESSION_ID}","top_k":2,"candidates":['
        '{"candidate_id":"a","item_id":"knowledge-a","title":"Qian evidence",'
        '"features":{"semantic_similarity":0.9,"knowledge_graph_relation":0.8,'
        '"sequence_transition":0.7,"historical_feedback":0.5,"content_freshness":0.5},'
        '"source_refs":["source:demo-zhouyi-reference"]}]}\''
    )
    print()
    print("Similar-case request:")
    print(
        "curl -sS http://127.0.0.1:8000/api/v1/cases/similar "
        f"-H 'Content-Type: application/json' -H 'X-User-Id: {DEMO_USER}' "
        '-d \'{"threshold":0.6,"features":{"chart_structure":{"day_master":"wood",'
        '"five_elements":{"wood":0.4,"fire":0.3,"earth":0.3},'
        '"strength":"balanced","pattern":"balanced_qi"}}}\''
    )


if __name__ == "__main__":
    main()
