from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.models import GeneratedQuestion, User
from app.schemas.schemas import (
    AIResponse,
    AssessmentRequest,
    ExplainRequest,
    GeneratedQuestionOut,
    QuestionRequest,
)
from app.services.ai_service import hf_service

router = APIRouter(tags=["practice"])


@router.post("/practice/generate", response_model=list[GeneratedQuestionOut])
@router.post("/api/ai/generate-questions", response_model=list[GeneratedQuestionOut])
async def generate_questions(
    payload: QuestionRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    questions = await hf_service.generate_mcqs(payload.topic, payload.difficulty, payload.count)
    for question in questions:
        db.add(
            GeneratedQuestion(
                user_id=user.id,
                topic=payload.topic,
                difficulty=payload.difficulty,
                question=question.question,
                options_json=question.options,
                answer=question.answer,
                explanation=question.explanation,
            )
        )
    db.commit()
    return questions


@router.post("/explain", response_model=AIResponse)
@router.post("/api/ai/explain", response_model=AIResponse)
async def explain_answer(
    payload: ExplainRequest,
    _: User = Depends(get_current_user),
):
    content = await hf_service.explain_answer(payload.question, payload.answer)
    return AIResponse(content=content, model=hf_service.model)


@router.post("/assessment", response_model=AIResponse)
@router.post("/api/ai/assessment", response_model=AIResponse)
async def generate_assessment(
    payload: AssessmentRequest,
    _: User = Depends(get_current_user),
):
    content = await hf_service.generate_assessment(payload.topics, payload.count_per_topic)
    return AIResponse(content=content, model=hf_service.model)
