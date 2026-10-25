"""
Cache Decorator — Adds in-memory caching to LLM calls.

Same prompt → cached response returned instantly.
Saves API cost and latency on repeated queries.
"""

from core.abstractions import LLMProvider
from infrastructure.decorators.base import LLMDecorator


class CacheDecorator(LLMDecorator):
    """Wraps LLMProvider with in-memory response caching."""

    def __init__(self, wrapped: LLMProvider) -> None:
        super().__init__(wrapped)
        self._cache: dict[str, str] = {}

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        key = f"complete:{system_prompt}:{user_prompt}"
        if key in self._cache:
            print("  [CACHE HIT] LLM.complete")
            return self._cache[key]

        result = super().complete(system_prompt, user_prompt)
        self._cache[key] = result
        return result

    def complete_json(self, system_prompt: str, user_prompt: str) -> str:
        key = f"complete_json:{system_prompt}:{user_prompt}"
        if key in self._cache:
            print("  [CACHE HIT] LLM.complete_json")
            return self._cache[key]

        result = super().complete_json(system_prompt, user_prompt)
        self._cache[key] = result
        return result
