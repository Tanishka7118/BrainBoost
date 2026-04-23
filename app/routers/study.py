from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.models import StudySession, User
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

router = APIRouter(tags=["study"])


@router.post("/sessions/", response_model=StudySessionOut)
@router.post("/sessions", response_model=StudySessionOut)
@router.post("/api/study/sessions", response_model=StudySessionOut)
def create_session(
    payload: StudySessionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = StudySession(
        user_id=user.id,
        subject=payload.subject.strip(),
        topic=payload.topic.strip(),
        duration_minutes=payload.duration_minutes,
        notes=payload.notes,
        session_date=payload.session_date,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/sessions/", response_model=list[StudySessionOut])
@router.get("/sessions", response_model=list[StudySessionOut])
@router.get("/api/study/sessions", response_model=list[StudySessionOut])
def get_sessions(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
):
    return (
        db.query(StudySession)
        .filter(StudySession.user_id == user.id)
        .order_by(StudySession.session_date.desc(), StudySession.id.desc())
        .limit(min(max(limit, 1), 300))
        .all()
    )


@router.get("/analytics/overview", response_model=AnalyticsOverview)
@router.get("/api/study/analytics/overview", response_model=AnalyticsOverview)
def get_overview(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    total_sessions = (
        db.query(func.count(StudySession.id)).filter(StudySession.user_id == user.id).scalar() or 0
    )
    total_minutes = (
        db.query(func.sum(StudySession.duration_minutes))
        .filter(StudySession.user_id == user.id)
        .scalar()
        or 0
    )
    return AnalyticsOverview(
        total_sessions=total_sessions,
        total_minutes=total_minutes,
        current_streak_days=compute_streak_days(db, user.id),
        due_revisions=due_revisions_count(db, user.id),
    )


@router.get("/analytics/daily", response_model=list[AnalyticsBucket])
@router.get("/api/study/analytics/daily", response_model=list[AnalyticsBucket])
def daily_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = 14,
):
    rows = aggregate_daily(db, user.id, min(max(days, 1), 120))
    return [
        AnalyticsBucket(bucket=bucket.isoformat(), total_minutes=minutes, sessions_count=count)
        for bucket, minutes, count in rows
    ]


@router.get("/analytics/weekly", response_model=list[AnalyticsBucket])
@router.get("/api/study/analytics/weekly", response_model=list[AnalyticsBucket])
def weekly_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    weeks: int = 10,
):
    rows = aggregate_weekly(db, user.id, min(max(weeks, 1), 60))
    return [
        AnalyticsBucket(bucket=bucket, total_minutes=minutes, sessions_count=count)
        for bucket, minutes, count in rows
    ]


@router.get("/analytics/monthly", response_model=list[AnalyticsBucket])
@router.get("/api/study/analytics/monthly", response_model=list[AnalyticsBucket])
def monthly_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    months: int = 6,
):
    rows = aggregate_monthly(db, user.id, min(max(months, 1), 24))
    return [
        AnalyticsBucket(bucket=bucket, total_minutes=minutes, sessions_count=count)
        for bucket, minutes, count in rows
    ]
