"""
Core Abstractions — Contracts that the entire system depends on.

DEPENDENCY INVERSION PRINCIPLE:
  High-level modules (services/) ──→ These Abstractions ←── Low-level modules (infrastructure/)

No external imports here. This is PURE Python — stdlib only.
"""

from abc import ABC, abstractmethod

from core.models import Chunk


class ChunkingStrategy(ABC):
    """
    Contract for all chunking algorithms (Strategy Pattern).

    Every chunking method (fixed, recursive, heading) implements this.
    Client code calls .chunk() without knowing which strategy is active.
    """

    @abstractmethod
    def chunk(self, text: str, source: str) -> list[Chunk]:
        """Split text into chunks. Each strategy implements differently."""


class LLMProvider(ABC):
    """
    Contract for LLM integrations (DIP — Dependency Inversion).

    SearchService depends on THIS abstraction, not on OpenAI directly.
    Swap OpenAI → Claude → Local LLM without touching service code.
    """

    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Generate text completion."""

    @abstractmethod
    def complete_json(self, system_prompt: str, user_prompt: str) -> str:
        """Generate JSON-formatted response (for reranking)."""


class VectorStore(ABC):
    """
    Contract for vector database adapters (Adapter Pattern).

    ChromaDB today, Qdrant/Pinecone tomorrow — services don't care.
    """

    @abstractmethod
    def query(
        self, query_text: str, n_results: int
    ) -> list[dict[str, str | dict[str, str] | float]]:
        """Search for nearest vectors matching query text."""
