from fastapi import APIRouter, Depends

from app.core.security import get_current_student
from app.models.models import Student
from app.schemas.schemas import (
    AIResponse,
    AssessmentRequest,
    ExplainRequest,
    QuestionRequest,
)
from app.services.ai_service import hf_service

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/generate-questions", response_model=AIResponse)
async def generate_questions(
    payload: QuestionRequest,
    _: Student = Depends(get_current_student),
):
    content = await hf_service.generate_mcqs(
        payload.topic,
        payload.difficulty,
        payload.count,
    )
    return AIResponse(content=content, model=hf_service.model)


@router.post("/explain", response_model=AIResponse)
async def explain_answer(
    payload: ExplainRequest,
    _: Student = Depends(get_current_student),
):
    content = await hf_service.explain_answer(payload.question, payload.answer)
    return AIResponse(content=content, model=hf_service.model)


@router.post("/assessment", response_model=AIResponse)
async def generate_assessment(
    payload: AssessmentRequest,
    _: Student = Depends(get_current_student),
):
    content = await hf_service.generate_assessment(
        payload.topics,
        payload.count_per_topic,
    )
    return AIResponse(content=content, model=hf_service.model)
