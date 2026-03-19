from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class StudentBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr


class StudentCreate(StudentBase):
    password: str = Field(min_length=6, max_length=120)


class StudentOut(StudentBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class StudySessionBase(BaseModel):
    subject: str = Field(min_length=2, max_length=120)
    topic: str = Field(min_length=2, max_length=255)
    duration_minutes: int = Field(gt=0, le=720)
    notes: str | None = None
    session_date: date


class StudySessionCreate(StudySessionBase):
    pass


class StudySessionOut(StudySessionBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class RevisionItemCreate(BaseModel):
    topic: str = Field(min_length=2, max_length=255)
    source_session_id: int | None = None
    notes: str | None = None
    confidence_level: int = Field(default=3, ge=1, le=5)
    next_review_date: date


class RevisionReviewRequest(BaseModel):
    confidence_level: int = Field(ge=1, le=5)
    interval_days: int = Field(default=2, ge=1, le=60)
    notes: str | None = None


class RevisionItemOut(BaseModel):
    id: int
    topic: str
    source_session_id: int | None
    confidence_level: int
    notes: str | None
    next_review_date: date
    last_reviewed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalyticsBucket(BaseModel):
    bucket: str
    total_minutes: int
    sessions_count: int


class AnalyticsOverview(BaseModel):
    total_sessions: int
    total_minutes: int
    current_streak_days: int
    due_revisions: int


class QuestionRequest(BaseModel):
    topic: str = Field(min_length=2, max_length=255)
    difficulty: str = Field(default="intermediate")
    count: int = Field(default=5, ge=1, le=10)


class ExplainRequest(BaseModel):
    question: str = Field(min_length=4)
    answer: str = Field(min_length=1)


class AssessmentRequest(BaseModel):
    topics: list[str] = Field(min_length=1, max_length=10)
    count_per_topic: int = Field(default=3, ge=1, le=6)


class AIResponse(BaseModel):
    content: str
    model: str
