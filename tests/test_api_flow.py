from datetime import date, timedelta
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./brainboost-test-suite.db")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base, get_db
from app.main import app


def test_brainboost_end_to_end_api_flow(tmp_path) -> None:
    db_path = tmp_path / "brainboost-test.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    try:
        register_response = client.post(
            "/auth/register",
            json={
                "name": "Test User",
                "email": "test@example.com",
                "password": "secret123",
            },
        )
        assert register_response.status_code == 201

        login_response = client.post(
            "/auth/login",
            data={"username": "test@example.com", "password": "secret123"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        session_response = client.post(
            "/sessions/",
            json={
                "subject": "DSA",
                "topic": "Graphs",
                "duration_minutes": 180,
                "notes": "I studied graphs today.",
                "session_date": date.today().isoformat(),
            },
            headers=headers,
        )
        assert session_response.status_code == 200

        sessions_response = client.get("/sessions/", headers=headers)
        assert sessions_response.status_code == 200
        assert len(sessions_response.json()) == 1

        daily_response = client.get("/analytics/daily?days=1", headers=headers)
        assert daily_response.status_code == 200
        assert daily_response.json()[0]["total_minutes"] == 180

        assert client.get("/analytics/weekly", headers=headers).status_code == 200
        assert client.get("/analytics/monthly", headers=headers).status_code == 200

        revision_response = client.post(
            "/revisions/",
            json={
                "topic": "Graphs",
                "confidence_level": 2,
                "notes": "Review traversals",
            },
            headers=headers,
        )
        assert revision_response.status_code == 200
        revision = revision_response.json()
        assert revision["next_review_date"] == (date.today() + timedelta(days=3)).isoformat()

        due_response = client.get("/revisions/due", headers=headers)
        assert due_response.status_code == 200
        assert due_response.json() == []

        practice_response = client.post(
            "/practice/generate",
            json={
                "topic": "Graphs",
                "difficulty": "intermediate",
                "count": 2,
            },
            headers=headers,
        )
        assert practice_response.status_code == 200
        questions = practice_response.json()
        assert len(questions) == 2
        assert set(questions[0]) == {"question", "options", "answer", "explanation"}
        assert len(questions[0]["options"]) == 4
    finally:
        app.dependency_overrides.clear()
