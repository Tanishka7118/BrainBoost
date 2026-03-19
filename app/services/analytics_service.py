from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import RevisionItem, StudySession


def compute_streak_days(db: Session, student_id: int) -> int:
    today = date.today()
    days = 0
    while True:
        target_day = today - timedelta(days=days)
        has_session = (
            db.query(StudySession.id)
            .filter(StudySession.student_id == student_id, StudySession.session_date == target_day)
            .first()
            is not None
        )
        if not has_session:
            return days
        days += 1


def aggregate_daily(db: Session, student_id: int, days: int) -> list[tuple[date, int, int]]:
    start_date = date.today() - timedelta(days=days - 1)
    return (
        db.query(
            StudySession.session_date,
            func.sum(StudySession.duration_minutes).label("total_minutes"),
            func.count(StudySession.id).label("sessions_count"),
        )
        .filter(StudySession.student_id == student_id, StudySession.session_date >= start_date)
        .group_by(StudySession.session_date)
        .order_by(StudySession.session_date.asc())
        .all()
    )


def aggregate_weekly(db: Session, student_id: int, weeks: int):
    # SQLite-compatible week bucketing with strftime
    return (
        db.query(
            func.strftime("%Y-W%W", StudySession.session_date).label("week"),
            func.sum(StudySession.duration_minutes).label("total_minutes"),
            func.count(StudySession.id).label("sessions_count"),
        )
        .filter(StudySession.student_id == student_id)
        .group_by(func.strftime("%Y-W%W", StudySession.session_date))
        .order_by(func.strftime("%Y-W%W", StudySession.session_date).desc())
        .limit(weeks)
        .all()[::-1]
    )


def aggregate_monthly(db: Session, student_id: int, months: int):
    return (
        db.query(
            func.strftime("%Y-%m", StudySession.session_date).label("month"),
            func.sum(StudySession.duration_minutes).label("total_minutes"),
            func.count(StudySession.id).label("sessions_count"),
        )
        .filter(StudySession.student_id == student_id)
        .group_by(func.strftime("%Y-%m", StudySession.session_date))
        .order_by(func.strftime("%Y-%m", StudySession.session_date).desc())
        .limit(months)
        .all()[::-1]
    )


def due_revisions_count(db: Session, student_id: int) -> int:
    return (
        db.query(func.count(RevisionItem.id))
        .filter(RevisionItem.student_id == student_id, RevisionItem.next_review_date <= date.today())
        .scalar()
        or 0
    )
