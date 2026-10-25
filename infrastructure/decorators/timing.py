"""
Timing Decorator — Logs execution time for LLM calls.

Wraps any LLMProvider to measure and print latency.
Essential for production performance monitoring.
"""

import time

from infrastructure.decorators.base import LLMDecorator


class TimingDecorator(LLMDecorator):
    """Wraps LLMProvider to log execution time of each call."""

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        start_time = time.time()
        result = super().complete(system_prompt, user_prompt)
        elapsed = time.time() - start_time
        print(f"  [TIMING] LLM.complete took {elapsed:.2f}s")
        return result

    def complete_json(self, system_prompt: str, user_prompt: str) -> str:
        start_time = time.time()
        result = super().complete_json(system_prompt, user_prompt)
        elapsed = time.time() - start_time
        print(f"  [TIMING] LLM.complete_json took {elapsed:.2f}s")
        return result
