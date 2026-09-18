from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models.entities import CollectionRecord, NoteRecord, TagRecord
from app.schemas.personal import (
    CollectionCreate,
    CollectionOut,
    NoteCreate,
    NoteOut,
    TagCreate,
    TagOut,
)


def list_collections(db: Session, user_id: str) -> list[CollectionRecord]:
    return list(
        db.scalars(
            select(CollectionRecord)
            .where(CollectionRecord.user_id == user_id)
            .order_by(CollectionRecord.created_at.desc())
        ).all()
    )


def create_collection(
    db: Session,
    user_id: str,
    payload: CollectionCreate,
) -> CollectionRecord:
    if payload.source_id:
        existing = db.scalar(
            select(CollectionRecord).where(
                CollectionRecord.user_id == user_id,
                CollectionRecord.item_type == payload.item_type,
                CollectionRecord.source_id == payload.source_id,
            )
        )
        if existing is not None:
            return existing

    record = CollectionRecord(
        id=str(uuid4()),
        user_id=user_id,
        item_type=payload.item_type,
        source_id=payload.source_id,
        snapshot_id=payload.snapshot_id,
        title=payload.title,
        source_metadata=payload.source_metadata,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def delete_collection(db: Session, user_id: str, collection_id: str) -> None:
    record = db.scalar(
        select(CollectionRecord).where(
            CollectionRecord.id == collection_id,
            CollectionRecord.user_id == user_id,
        )
    )
    if record is None:
        raise NotFoundError("Collection not found", {"collection_id": collection_id})
    db.delete(record)
    db.commit()


def list_notes(db: Session, user_id: str) -> list[NoteRecord]:
    return list(
        db.scalars(
            select(NoteRecord)
            .where(NoteRecord.user_id == user_id)
            .order_by(NoteRecord.updated_at.desc())
        ).all()
    )


def upsert_note(db: Session, user_id: str, payload: NoteCreate) -> NoteRecord:
    if payload.collection_id:
        collection = db.scalar(
            select(CollectionRecord).where(
                CollectionRecord.id == payload.collection_id,
                CollectionRecord.user_id == user_id,
            )
        )
        if collection is None:
            raise NotFoundError("Collection not found", {"collection_id": payload.collection_id})

    if payload.note_id:
        record = db.scalar(
            select(NoteRecord).where(
                NoteRecord.id == payload.note_id,
                NoteRecord.user_id == user_id,
            )
        )
        if record is None:
            other_user_note = db.get(NoteRecord, payload.note_id)
            if other_user_note is not None:
                raise NotFoundError("Note not found", {"note_id": payload.note_id})
            record = NoteRecord(id=payload.note_id, user_id=user_id, body=payload.body)
            db.add(record)
    else:
        record = NoteRecord(id=str(uuid4()), user_id=user_id, body=payload.body)
        db.add(record)

    record.source_id = payload.source_id
    record.collection_id = payload.collection_id
    record.title = payload.title
    record.body = payload.body
    record.tags = _normalize_tags(payload.tags)
    record.source_refs = list(dict.fromkeys(payload.source_refs))
    _ensure_tags(db, user_id, record.tags)
    db.commit()
    db.refresh(record)
    return record


def delete_note(db: Session, user_id: str, note_id: str) -> None:
    record = db.scalar(
        select(NoteRecord).where(NoteRecord.id == note_id, NoteRecord.user_id == user_id)
    )
    if record is None:
        raise NotFoundError("Note not found", {"note_id": note_id})
    db.delete(record)
    db.commit()


def list_tags(db: Session, user_id: str) -> list[TagRecord]:
    return list(
        db.scalars(
            select(TagRecord).where(TagRecord.user_id == user_id).order_by(TagRecord.name.asc())
        ).all()
    )


def create_tag(db: Session, user_id: str, payload: TagCreate) -> TagRecord:
    name = payload.name.strip()
    existing = db.scalar(
        select(TagRecord).where(TagRecord.user_id == user_id, TagRecord.name == name)
    )
    if existing is not None:
        return existing
    record = TagRecord(id=str(uuid4()), user_id=user_id, name=name)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def delete_tag(db: Session, user_id: str, tag_id: str) -> None:
    record = db.scalar(
        select(TagRecord).where(TagRecord.id == tag_id, TagRecord.user_id == user_id)
    )
    if record is None:
        raise NotFoundError("Tag not found", {"tag_id": tag_id})
    db.delete(record)
    db.commit()


def collection_to_schema(record: CollectionRecord) -> CollectionOut:
    return CollectionOut(
        collection_id=record.id,
        user_id=record.user_id,
        item_type=record.item_type,
        source_id=record.source_id,
        snapshot_id=record.snapshot_id,
        title=record.title,
        source_metadata=record.source_metadata,
        created_at=record.created_at,
    )


def note_to_schema(record: NoteRecord) -> NoteOut:
    return NoteOut(
        note_id=record.id,
        user_id=record.user_id,
        source_id=record.source_id,
        collection_id=record.collection_id,
        title=record.title,
        body=record.body,
        tags=record.tags,
        source_refs=record.source_refs,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def tag_to_schema(record: TagRecord) -> TagOut:
    return TagOut(tag_id=record.id, name=record.name, created_at=record.created_at)


def _normalize_tags(tags: list[str]) -> list[str]:
    normalized = [tag.strip() for tag in tags if tag.strip()]
    return list(dict.fromkeys(normalized))


def _ensure_tags(db: Session, user_id: str, tags: list[str]) -> None:
    if not tags:
        return
    existing = set(
        db.scalars(
            select(TagRecord.name).where(TagRecord.user_id == user_id, TagRecord.name.in_(tags))
        ).all()
    )
    for tag in tags:
        if tag not in existing:
            db.add(TagRecord(id=str(uuid4()), user_id=user_id, name=tag))
