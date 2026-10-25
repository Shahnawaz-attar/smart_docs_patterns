"""
OpenAI Provider — Concrete LLMProvider implementation.

Low-level module: SearchService never imports this directly.
It receives it via DIP injection through the LLMProvider abstraction.
"""

from openai import OpenAI
from dotenv import load_dotenv

from core.abstractions import LLMProvider
from infrastructure.config import config

load_dotenv()


class OpenAIProvider(LLMProvider):
    """OpenAI GPT implementation of the LLMProvider contract."""

    def __init__(self) -> None:
        self._client = OpenAI()
        self._model = config.chat_model

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
        )
        content = response.choices[0].message.content
        return content if content else ""

    def complete_json(self, system_prompt: str, user_prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return content if content else "{}"
