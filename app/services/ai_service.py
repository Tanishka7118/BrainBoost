import json

import httpx

from app.core.config import settings


class HuggingFaceService:
    def __init__(self) -> None:
        self.model = settings.hf_model
        self.base_url = (
            f"https://api-inference.huggingface.co/models/{self.model}"
        )

    async def _generate(self, prompt: str, max_new_tokens: int = 350) -> str:
        if not settings.hf_api_token:
            return (
                "Hugging Face API token is not configured. "
                "Set HF_API_TOKEN in your environment "
                "to enable AI generation."
            )

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
            response = await client.post(
                self.base_url,
                headers=headers,
                json=payload,
            )

        if response.status_code >= 400:
            return (
                f"Model request failed with status {response.status_code}: "
                f"{response.text[:300]}"
            )

        try:
            data = response.json()
        except json.JSONDecodeError:
            return response.text

        if isinstance(data, list) and data:
            candidate = data[0]
            if isinstance(candidate, dict) and "generated_text" in candidate:
                return str(candidate["generated_text"]).strip()
        if isinstance(data, dict) and "generated_text" in data:
            return str(data["generated_text"]).strip()
        return str(data)

    async def generate_mcqs(
        self,
        topic: str,
        difficulty: str,
        count: int,
    ) -> str:
        prompt = (
            "You are an education assistant. "
            "Generate high-quality multiple-choice questions.\n"
            f"Topic: {topic}\nDifficulty: {difficulty}\n"
            f"Number of questions: {count}\n"
            "Return in plain text with this structure for each question:\n"
            "Q1: ...\nA) ...\nB) ...\nC) ...\nD) ...\n"
            "Answer: ...\nExplanation: ...\n"
        )
        return await self._generate(prompt)

    async def explain_answer(self, question: str, answer: str) -> str:
        prompt = (
            "You are a helpful tutor. "
            "Explain the answer in a concise but clear way.\n"
            f"Question: {question}\nStudent's answer/context: {answer}\n"
            "Include: concept summary, why the answer works, "
            "and one quick memory tip."
        )
        return await self._generate(prompt, max_new_tokens=280)

    async def generate_assessment(
        self,
        topics: list[str],
        count_per_topic: int,
    ) -> str:
        topic_list = ", ".join(topics)
        prompt = (
            "Create a mixed-topic assessment for a student.\n"
            f"Topics: {topic_list}\n"
            f"Questions per topic: {count_per_topic}\n"
            "Output as numbered MCQs followed by an answer key at the end."
        )
        return await self._generate(prompt, max_new_tokens=500)


hf_service = HuggingFaceService()
