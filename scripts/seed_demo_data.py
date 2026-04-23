from pathlib import Path
import sys
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.security import get_password_hash
from app.db.database import SessionLocal, init_db
from app.models.models import GeneratedQuestion, RevisionItem, StudySession, User


SEED_EMAIL = "tanishka@example.com"
SEED_PASSWORD = "Pass@123"


def _seed_user(db: Session) -> User:
    user = db.query(User).filter(User.email == SEED_EMAIL).first()
    if user is None:
        user = User(
            name="Tanishka",
            email=SEED_EMAIL,
            hashed_password=get_password_hash(SEED_PASSWORD),
            created_at=datetime.utcnow(),
        )
        db.add(user)
        db.flush()
        return user

    user.name = "Tanishka"
    user.hashed_password = get_password_hash(SEED_PASSWORD)
    return user


def _replace_user_data(db: Session, user_id: int) -> None:
    db.query(GeneratedQuestion).filter(GeneratedQuestion.user_id == user_id).delete()
    db.query(RevisionItem).filter(RevisionItem.user_id == user_id).delete()
    db.query(StudySession).filter(StudySession.user_id == user_id).delete()
    db.flush()


def seed_demo_data() -> None:
    init_db()

    with SessionLocal() as db:
        user = _seed_user(db)
        db.flush()
        _replace_user_data(db, user.id)

        today = date.today()

        sessions = [
            StudySession(
                user_id=user.id,
                subject="Computer Science",
                topic="Data Structures",
                duration_minutes=90,
                notes="Reviewed stacks, queues, and linked lists.",
                session_date=today - timedelta(days=0),
            ),
            StudySession(
                user_id=user.id,
                subject="Computer Science",
                topic="Algorithms",
                duration_minutes=120,
                notes="Practiced sorting and graph traversal problems.",
                session_date=today - timedelta(days=1),
            ),
            StudySession(
                user_id=user.id,
                subject="Database Systems",
                topic="PostgreSQL Basics",
                duration_minutes=75,
                notes="Covered tables, indexes, and simple joins.",
                session_date=today - timedelta(days=2),
            ),
            StudySession(
                user_id=user.id,
                subject="Operating Systems",
                topic="Process Scheduling",
                duration_minutes=60,
                notes="Round robin vs FCFS comparison.",
                session_date=today - timedelta(days=7),
            ),
            StudySession(
                user_id=user.id,
                subject="Machine Learning",
                topic="Model Evaluation",
                duration_minutes=110,
                notes="Precision, recall, F1, and overfitting notes.",
                session_date=today - timedelta(days=14),
            ),
        ]
        db.add_all(sessions)
        db.flush()

        source_session_by_topic = {session.topic: session for session in sessions}

        revisions = [
            RevisionItem(
                user_id=user.id,
                source_session_id=source_session_by_topic["Data Structures"].id,
                topic="Data Structures",
                confidence_level=3,
                notes="Review stack operations and queue applications.",
                next_review_date=today - timedelta(days=1),
                last_reviewed_at=datetime.utcnow() - timedelta(days=1),
            ),
            RevisionItem(
                user_id=user.id,
                source_session_id=source_session_by_topic["Algorithms"].id,
                topic="Algorithms",
                confidence_level=4,
                notes="Focus on graph DFS/BFS and complexity.",
                next_review_date=today,
                last_reviewed_at=datetime.utcnow() - timedelta(days=2),
            ),
            RevisionItem(
                user_id=user.id,
                source_session_id=source_session_by_topic["PostgreSQL Basics"].id,
                topic="PostgreSQL Basics",
                confidence_level=2,
                notes="Revisit index usage and normalization.",
                next_review_date=today + timedelta(days=3),
                last_reviewed_at=None,
            ),
        ]
        db.add_all(revisions)

        generated_questions = [
            GeneratedQuestion(
                user_id=user.id,
                topic="Data Structures",
                difficulty="beginner",
                question="Which data structure follows LIFO order?",
                options_json=[
                    "Stack",
                    "Queue",
                    "Graph",
                    "Tree",
                ],
                answer="Stack",
                explanation="A stack is last-in, first-out, which matches LIFO order.",
            ),
            GeneratedQuestion(
                user_id=user.id,
                topic="Algorithms",
                difficulty="intermediate",
                question="What is the average-case time complexity of binary search?",
                options_json=[
                    "O(1)",
                    "O(log n)",
                    "O(n)",
                    "O(n log n)",
                ],
                answer="O(log n)",
                explanation="Binary search halves the search space each step, so it is logarithmic.",
            ),
            GeneratedQuestion(
                user_id=user.id,
                topic="PostgreSQL Basics",
                difficulty="intermediate",
                question="What feature helps speed up lookups on a frequently filtered column?",
                options_json=[
                    "Trigger",
                    "View",
                    "Index",
                    "Sequence",
                ],
                answer="Index",
                explanation="Indexes improve lookup performance for filtered and sorted queries.",
            ),
        ]
        db.add_all(generated_questions)

        db.commit()


if __name__ == "__main__":
    seed_demo_data()