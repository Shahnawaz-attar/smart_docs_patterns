"""
Base LLM Decorator — Foundation for the Decorator Pattern chain.

All concrete decorators (Retry, Cache, Timing) extend this.
It delegates all calls to the wrapped provider by default.
"""

from core.abstractions import LLMProvider


class LLMDecorator(LLMProvider):
    """Base Decorator — delegates all calls to the wrapped LLMProvider."""

    def __init__(self, wrapped: LLMProvider) -> None:
        self._wrapped = wrapped

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        return self._wrapped.complete(system_prompt, user_prompt)

    def complete_json(self, system_prompt: str, user_prompt: str) -> str:
        return self._wrapped.complete_json(system_prompt, user_prompt)
