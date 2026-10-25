"""
In-Memory Provider — Mock LLMProvider for testing.

DIP's biggest benefit: inject this instead of OpenAI for fast, free, offline tests.
Production: SearchService(llm=OpenAIProvider())
Testing:    SearchService(llm=InMemoryProvider())
SearchService doesn't care which one it gets.
"""

import json

from core.abstractions import LLMProvider


class InMemoryProvider(LLMProvider):
    """Fake LLM for unit testing — no API calls, instant, free."""

    def __init__(self, fake_answer: str = "This is a test answer.") -> None:
        self._fake_answer = fake_answer
        self.call_count: int = 0

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        self.call_count += 1
        return self._fake_answer

    def complete_json(self, system_prompt: str, user_prompt: str) -> str:
        self.call_count += 1
        return json.dumps({"scores": [8, 6, 9, 3, 7, 5, 2, 4]})
