"""
Retry Decorator — Adds retry with exponential backoff to LLM calls.

Wraps any LLMProvider. If API call fails, retries up to N times
with increasing delay. Production-essential for flaky network calls.
"""

import time

from core.abstractions import LLMProvider
from infrastructure.decorators.base import LLMDecorator


class RetryDecorator(LLMDecorator):
    """Wraps LLMProvider with automatic retry on failure."""

    def __init__(
        self, wrapped: LLMProvider, retries: int = 3, backoff: float = 1.0
    ) -> None:
        super().__init__(wrapped)
        self._retries = retries
        self._backoff = backoff

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        attempt = 0
        while attempt < self._retries:
            try:
                return super().complete(system_prompt, user_prompt)
            except Exception as e:
                attempt += 1
                if attempt == self._retries:
                    raise e
                time.sleep(self._backoff * attempt)
        return ""

    def complete_json(self, system_prompt: str, user_prompt: str) -> str:
        attempt = 0
        while attempt < self._retries:
            try:
                return super().complete_json(system_prompt, user_prompt)
            except Exception as e:
                attempt += 1
                if attempt == self._retries:
                    raise e
                time.sleep(self._backoff * attempt)
        return "{}"
