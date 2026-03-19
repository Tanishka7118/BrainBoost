from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_student
from app.db.database import get_db
from app.models.models import RevisionItem, Student, StudySession
from app.schemas.schemas import RevisionItemCreate, RevisionItemOut, RevisionReviewRequest

router = APIRouter(prefix="/api/revision", tags=["revision"])


@router.post("/items", response_model=RevisionItemOut)
def create_revision_item(
    payload: RevisionItemCreate,
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    if payload.source_session_id:
        source = (
            db.query(StudySession)
            .filter(StudySession.id == payload.source_session_id, StudySession.student_id == student.id)
            .first()
        )
        if not source:
            raise HTTPException(status_code=404, detail="Source session not found")

    item = RevisionItem(
        student_id=student.id,
        source_session_id=payload.source_session_id,
        topic=payload.topic,
        notes=payload.notes,
        confidence_level=payload.confidence_level,
        next_review_date=payload.next_review_date,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post("/from-session/{session_id}", response_model=RevisionItemOut)
def create_from_session(
    session_id: int,
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    source = (
        db.query(StudySession)
        .filter(StudySession.id == session_id, StudySession.student_id == student.id)
        .first()
    )
    if not source:
        raise HTTPException(status_code=404, detail="Study session not found")

    item = RevisionItem(
        student_id=student.id,
        source_session_id=source.id,
        topic=source.topic,
        notes=source.notes,
        confidence_level=3,
        next_review_date=date.today() + timedelta(days=2),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/items", response_model=list[RevisionItemOut])
def list_revision_items(
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
    due_only: bool = False,
):
    query = db.query(RevisionItem).filter(RevisionItem.student_id == student.id)
    if due_only:
        query = query.filter(RevisionItem.next_review_date <= date.today())
    return query.order_by(RevisionItem.next_review_date.asc(), RevisionItem.id.desc()).all()


@router.post("/items/{item_id}/review", response_model=RevisionItemOut)
def mark_reviewed(
    item_id: int,
    payload: RevisionReviewRequest,
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    item = (
        db.query(RevisionItem)
        .filter(RevisionItem.id == item_id, RevisionItem.student_id == student.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Revision item not found")

    item.confidence_level = payload.confidence_level
    item.notes = payload.notes or item.notes
    item.last_reviewed_at = datetime.utcnow()

    # Basic spaced repetition scaling based on confidence.
    multiplier = {1: 1, 2: 1, 3: 2, 4: 3, 5: 4}[payload.confidence_level]
    item.next_review_date = date.today() + timedelta(days=payload.interval_days * multiplier)

    db.commit()
    db.refresh(item)
    return item
