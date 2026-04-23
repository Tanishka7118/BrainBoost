from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.models import RevisionItem, StudySession, User
from app.schemas.schemas import RevisionItemCreate, RevisionItemOut, RevisionReviewRequest

router = APIRouter(tags=["revision"])

CONFIDENCE_INTERVAL_DAYS = {1: 1, 2: 3, 3: 7, 4: 14, 5: 30}


def next_review_date_for_confidence(confidence_level: int) -> date:
    return date.today() + timedelta(days=CONFIDENCE_INTERVAL_DAYS[confidence_level])


@router.post("/revisions/", response_model=RevisionItemOut)
@router.post("/revisions", response_model=RevisionItemOut)
@router.post("/api/revision/items", response_model=RevisionItemOut)
def create_revision_item(
    payload: RevisionItemCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.source_session_id:
        source = (
            db.query(StudySession)
            .filter(StudySession.id == payload.source_session_id, StudySession.user_id == user.id)
            .first()
        )
        if not source:
            raise HTTPException(status_code=404, detail="Source session not found")

    item = RevisionItem(
        user_id=user.id,
        source_session_id=payload.source_session_id,
        topic=payload.topic.strip(),
        notes=payload.notes,
        confidence_level=payload.confidence_level,
        next_review_date=payload.next_review_date
        or next_review_date_for_confidence(payload.confidence_level),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post("/revisions/from-session/{session_id}", response_model=RevisionItemOut)
@router.post("/api/revision/from-session/{session_id}", response_model=RevisionItemOut)
def create_from_session(
    session_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    source = (
        db.query(StudySession)
        .filter(StudySession.id == session_id, StudySession.user_id == user.id)
        .first()
    )
    if not source:
        raise HTTPException(status_code=404, detail="Study session not found")

    item = RevisionItem(
        user_id=user.id,
        source_session_id=source.id,
        topic=source.topic,
        notes=source.notes,
        confidence_level=3,
        next_review_date=next_review_date_for_confidence(3),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/revisions/", response_model=list[RevisionItemOut])
@router.get("/revisions", response_model=list[RevisionItemOut])
@router.get("/api/revision/items", response_model=list[RevisionItemOut])
def list_revision_items(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    due_only: bool = False,
):
    query = db.query(RevisionItem).filter(RevisionItem.user_id == user.id)
    if due_only:
        query = query.filter(RevisionItem.next_review_date <= date.today())
    return query.order_by(RevisionItem.next_review_date.asc(), RevisionItem.id.desc()).all()


@router.get("/revisions/due", response_model=list[RevisionItemOut])
@router.get("/api/revision/due", response_model=list[RevisionItemOut])
def due_revision_items(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(RevisionItem)
        .filter(RevisionItem.user_id == user.id, RevisionItem.next_review_date <= date.today())
        .order_by(RevisionItem.next_review_date.asc(), RevisionItem.id.desc())
        .all()
    )


@router.post("/revisions/{item_id}/review", response_model=RevisionItemOut)
@router.post("/api/revision/items/{item_id}/review", response_model=RevisionItemOut)
def mark_reviewed(
    item_id: int,
    payload: RevisionReviewRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = (
        db.query(RevisionItem)
        .filter(RevisionItem.id == item_id, RevisionItem.user_id == user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Revision item not found")

    item.confidence_level = payload.confidence_level
    item.notes = payload.notes or item.notes
    item.last_reviewed_at = datetime.utcnow()
    item.next_review_date = next_review_date_for_confidence(payload.confidence_level)

    db.commit()
    db.refresh(item)
    return item
