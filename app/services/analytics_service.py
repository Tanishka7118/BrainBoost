from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import RevisionItem, StudySession


def compute_streak_days(db: Session, user_id: int) -> int:
    today = date.today()
    days = 0
    while True:
        target_day = today - timedelta(days=days)
        has_session = (
            db.query(StudySession.id)
            .filter(StudySession.user_id == user_id, StudySession.session_date == target_day)
            .first()
            is not None
        )
        if not has_session:
            return days
        days += 1


def aggregate_daily(db: Session, user_id: int, days: int) -> list[tuple[date, int, int]]:
    start_date = date.today() - timedelta(days=days - 1)
    rows = (
        db.query(
            StudySession.session_date,
            func.sum(StudySession.duration_minutes).label("total_minutes"),
            func.count(StudySession.id).label("sessions_count"),
        )
        .filter(StudySession.user_id == user_id, StudySession.session_date >= start_date)
        .group_by(StudySession.session_date)
        .order_by(StudySession.session_date.asc())
        .all()
    )
    by_day = {row[0]: (int(row[1] or 0), int(row[2] or 0)) for row in rows}
    return [
        (target, *by_day.get(target, (0, 0)))
        for target in (start_date + timedelta(days=offset) for offset in range(days))
    ]


def aggregate_weekly(db: Session, user_id: int, weeks: int):
    dialect = db.bind.dialect.name if db.bind else ""
    if dialect == "postgresql":
        week_bucket = func.to_char(func.date_trunc("week", StudySession.session_date), 'IYYY-"W"IW')
    else:
        week_bucket = func.strftime("%Y-W%W", StudySession.session_date)

    return (
        db.query(
            week_bucket.label("week"),
            func.sum(StudySession.duration_minutes).label("total_minutes"),
            func.count(StudySession.id).label("sessions_count"),
        )
        .filter(StudySession.user_id == user_id)
        .group_by(week_bucket)
        .order_by(week_bucket.desc())
        .limit(weeks)
        .all()[::-1]
    )


def aggregate_monthly(db: Session, user_id: int, months: int):
    dialect = db.bind.dialect.name if db.bind else ""
    if dialect == "postgresql":
        month_bucket = func.to_char(func.date_trunc("month", StudySession.session_date), "YYYY-MM")
    else:
        month_bucket = func.strftime("%Y-%m", StudySession.session_date)

    return (
        db.query(
            month_bucket.label("month"),
            func.sum(StudySession.duration_minutes).label("total_minutes"),
            func.count(StudySession.id).label("sessions_count"),
        )
        .filter(StudySession.user_id == user_id)
        .group_by(month_bucket)
        .order_by(month_bucket.desc())
        .limit(months)
        .all()[::-1]
    )


def due_revisions_count(db: Session, user_id: int) -> int:
    return (
        db.query(func.count(RevisionItem.id))
        .filter(RevisionItem.user_id == user_id, RevisionItem.next_review_date <= date.today())
        .scalar()
        or 0
    )
