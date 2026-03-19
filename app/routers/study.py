
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_current_student
from app.db.database import get_db
from app.models.models import Student, StudySession
from app.schemas.schemas import (
    AnalyticsBucket,
    AnalyticsOverview,
    StudySessionCreate,
    StudySessionOut,
)
from app.services.analytics_service import (
    aggregate_daily,
    aggregate_monthly,
    aggregate_weekly,
    compute_streak_days,
    due_revisions_count,
)

router = APIRouter(prefix="/api/study", tags=["study"])


@router.post("/sessions", response_model=StudySessionOut)
def create_session(
    payload: StudySessionCreate,
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    item = StudySession(
        student_id=student.id,
        subject=payload.subject,
        topic=payload.topic,
        duration_minutes=payload.duration_minutes,
        notes=payload.notes,
        session_date=payload.session_date,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/sessions", response_model=list[StudySessionOut])
def get_sessions(
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
    limit: int = 50,
):
    return (
        db.query(StudySession)
        .filter(StudySession.student_id == student.id)
        .order_by(StudySession.session_date.desc(), StudySession.id.desc())
        .limit(min(max(limit, 1), 300))
        .all()
    )


@router.get("/analytics/overview", response_model=AnalyticsOverview)
def get_overview(student: Student = Depends(get_current_student), db: Session = Depends(get_db)):
    total_sessions = (
        db.query(func.count(StudySession.id)).filter(StudySession.student_id == student.id).scalar() or 0
    )
    total_minutes = (
        db.query(func.sum(StudySession.duration_minutes))
        .filter(StudySession.student_id == student.id)
        .scalar()
        or 0
    )
    return AnalyticsOverview(
        total_sessions=total_sessions,
        total_minutes=total_minutes,
        current_streak_days=compute_streak_days(db, student.id),
        due_revisions=due_revisions_count(db, student.id),
    )


@router.get("/analytics/daily", response_model=list[AnalyticsBucket])
def daily_stats(
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
    days: int = 14,
):
    rows = aggregate_daily(db, student.id, min(max(days, 1), 120))
    return [
        AnalyticsBucket(bucket=d.isoformat(), total_minutes=minutes, sessions_count=count)
        for d, minutes, count in rows
    ]


@router.get("/analytics/weekly", response_model=list[AnalyticsBucket])
def weekly_stats(
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
    weeks: int = 10,
):
    rows = aggregate_weekly(db, student.id, min(max(weeks, 1), 60))
    return [
        AnalyticsBucket(bucket=week, total_minutes=minutes, sessions_count=count)
        for week, minutes, count in rows
    ]


@router.get("/analytics/monthly", response_model=list[AnalyticsBucket])
def monthly_stats(
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
    months: int = 6,
):
    rows = aggregate_monthly(db, student.id, min(max(months, 1), 24))
    return [
        AnalyticsBucket(bucket=month, total_minutes=minutes, sessions_count=count)
        for month, minutes, count in rows
    ]
