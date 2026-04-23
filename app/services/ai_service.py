import json
import re

import httpx
from pydantic import TypeAdapter, ValidationError

from app.core.config import settings
from app.schemas.schemas import GeneratedQuestionOut

QuestionListAdapter = TypeAdapter(list[GeneratedQuestionOut])


class HuggingFaceService:
    def __init__(self) -> None:
        self.model = settings.hf_model
        self.base_url = f"https://api-inference.huggingface.co/models/{self.model}"

    async def _generate(self, prompt: str, max_new_tokens: int = 350) -> str:
        if not settings.hf_api_token:
            raise RuntimeError("HF_API_TOKEN is not configured")

        headers = {"Authorization": f"Bearer {settings.hf_api_token}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_new_tokens,
                "temperature": 0.7,
                "return_full_text": False,
            },
        }

        async with httpx.AsyncClient(timeout=40.0) as client:
            try:
                response = await client.post(self.base_url, headers=headers, json=payload)
            except httpx.HTTPError as exc:
                raise RuntimeError(f"Model request failed: {exc}") from exc

        if response.status_code >= 400:
            raise RuntimeError(
                f"Model request failed with status {response.status_code}: {response.text[:300]}"
            )

        try:
            data = response.json()
        except json.JSONDecodeError as exc:
            raise RuntimeError("Model returned a non-JSON response") from exc

        if isinstance(data, list) and data:
            candidate = data[0]
            if isinstance(candidate, dict) and "generated_text" in candidate:
                return str(candidate["generated_text"]).strip()
        if isinstance(data, dict) and "generated_text" in data:
            return str(data["generated_text"]).strip()
        return str(data)

    def _fallback_questions(
        self,
        topic: str,
        difficulty: str,
        count: int,
    ) -> list[GeneratedQuestionOut]:
        return [
            GeneratedQuestionOut(
                question=f"Which statement best describes {topic} at a {difficulty} level?",
                options=[
                    f"{topic} can be understood through definitions, examples, and practice.",
                    f"{topic} only requires memorizing unrelated facts.",
                    f"{topic} cannot be improved with revision.",
                    f"{topic} is useful only after exams are over.",
                ],
                answer=f"{topic} can be understood through definitions, examples, and practice.",
                explanation=(
                    "The correct option focuses on conceptual understanding and repeated "
                    "practice, which matches the BrainBoost learning workflow."
                ),
            )
            for _ in range(count)
        ]

    def _fallback_explanation(self, question: str, answer: str) -> str:
        return (
            "Concept summary: the answer should connect directly to the core idea in the question.\n"
            f"Why it works: '{answer}' matches the key point implied by '{question}'.\n"
            "Memory tip: restate the idea in your own words and test it with one example."
        )

    def _fallback_assessment(self, topics: list[str], count_per_topic: int) -> str:
        lines: list[str] = ["BrainBoost assessment"]
        number = 1
        for topic in topics:
            for _ in range(count_per_topic):
                lines.append(f"{number}. Which statement best describes {topic}?")
                lines.append("A. Review the definition and one worked example.")
                lines.append("B. Memorize unrelated facts only.")
                lines.append("C. Skip practice and move on immediately.")
                lines.append("D. Focus only on exam-day tricks.")
                lines.append(f"Answer: A. Review the definition and one worked example.\n")
                number += 1
        return "\n".join(lines).strip()

    def _extract_json_array(self, text: str) -> str:
        fenced = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, flags=re.DOTALL)
        if fenced:
            return fenced.group(1)

        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]
        raise ValueError("No JSON array found in model response")

    def _parse_questions(
        self,
        text: str,
        topic: str,
        difficulty: str,
        count: int,
    ) -> list[GeneratedQuestionOut]:
        try:
            raw = json.loads(self._extract_json_array(text))
            questions = QuestionListAdapter.validate_python(raw)
        except (json.JSONDecodeError, ValueError, ValidationError):
            return self._fallback_questions(topic, difficulty, count)
        return questions[:count] or self._fallback_questions(topic, difficulty, count)

    async def generate_mcqs(
        self,
        topic: str,
        difficulty: str,
        count: int,
    ) -> list[GeneratedQuestionOut]:
        prompt = (
            "You are an education assistant. Generate high-quality multiple-choice "
            "questions as strict JSON.\n"
            f"Topic: {topic}\n"
            f"Difficulty: {difficulty}\n"
            f"Number of questions: {count}\n"
            "Return only a JSON array. Each item must have exactly these keys: "
            "question, options, answer, explanation. options must contain exactly "
            "four strings and answer must exactly match one option."
        )
        try:
            text = await self._generate(prompt)
        except RuntimeError:
            return self._fallback_questions(topic, difficulty, count)
        return self._parse_questions(text, topic, difficulty, count)

    async def explain_answer(self, question: str, answer: str) -> str:
        prompt = (
            "You are a helpful tutor. Explain the answer in a concise but clear way.\n"
            f"Question: {question}\nStudent's answer/context: {answer}\n"
            "Include: concept summary, why the answer works, and one quick memory tip."
        )
        try:
            return await self._generate(prompt, max_new_tokens=280)
        except RuntimeError as exc:
            return self._fallback_explanation(question, answer)

    async def generate_assessment(self, topics: list[str], count_per_topic: int) -> str:
        topic_list = ", ".join(topics)
        prompt = (
            "Create a mixed-topic assessment for a student.\n"
            f"Topics: {topic_list}\n"
            f"Questions per topic: {count_per_topic}\n"
            "Output as numbered MCQs followed by an answer key at the end."
        )
        try:
            return await self._generate(prompt, max_new_tokens=500)
        except RuntimeError as exc:
            return self._fallback_assessment(topics, count_per_topic)


hf_service = HuggingFaceService()
