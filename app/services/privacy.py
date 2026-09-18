from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import PrivacySettingsRecord
from app.schemas.personal import PrivacyOut, PrivacyUpdate


def get_or_create_privacy(db: Session, user_id: str) -> PrivacySettingsRecord:
    record = db.get(PrivacySettingsRecord, user_id)
    if record is not None:
        return record

    record = PrivacySettingsRecord(
        user_id=user_id,
        consent_scopes=["session_storage"],
        retention_policy="standard",
        allow_anonymous_cases=False,
        allow_shared_training=False,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_privacy(db: Session, user_id: str, payload: PrivacyUpdate) -> PrivacySettingsRecord:
    record = get_or_create_privacy(db, user_id)
    record.consent_scopes = list(dict.fromkeys(payload.consent_scopes))
    record.retention_policy = payload.retention_policy
    record.allow_anonymous_cases = payload.allow_anonymous_cases
    record.allow_shared_training = payload.allow_shared_training
    record.updated_at = datetime.now(UTC)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def select_privacy(db: Session, user_id: str) -> PrivacySettingsRecord:
    record = db.scalar(
        select(PrivacySettingsRecord).where(PrivacySettingsRecord.user_id == user_id)
    )
    return record or get_or_create_privacy(db, user_id)


def privacy_to_schema(record: PrivacySettingsRecord) -> PrivacyOut:
    return PrivacyOut(
        user_id=record.user_id,
        consent_scopes=record.consent_scopes,
        retention_policy=record.retention_policy,
        allow_anonymous_cases=record.allow_anonymous_cases,
        allow_shared_training=record.allow_shared_training,
        updated_at=record.updated_at,
    )
