"""
Chunker Factory — Centralizes chunking strategy creation (Factory Pattern).

Factory + OCP: register new strategies at runtime without modifying existing code.
  ChunkerFactory.create("heading")   → HeadingChunking instance
  ChunkerFactory.register("semantic", SemanticChunking)  → extend without modify
"""

from typing import ClassVar

from core.abstractions import ChunkingStrategy
from infrastructure.chunking import FixedChunking, RecursiveChunking, HeadingChunking


class ChunkerFactory:
    """Factory for creating ChunkingStrategy instances by name."""

    _registry: ClassVar[dict[str, type[ChunkingStrategy]]] = {
        "fixed": FixedChunking,
        "recursive": RecursiveChunking,
        "heading": HeadingChunking,
    }

    @classmethod
    def create(cls, strategy_name: str, **kwargs: int) -> ChunkingStrategy:
        """
        Strategy name do, ready-to-use chunker object lo.

        Usage:
            chunker = ChunkerFactory.create("heading")
            chunker = ChunkerFactory.create("fixed", chunk_size=300, overlap=30)

        Raises:
            ValueError: If unknown strategy name provided.
        """
        chunker_class = cls._registry.get(strategy_name)
        if chunker_class is None:
            valid_options = ", ".join(cls._registry.keys())
            raise ValueError(
                f"Unknown strategy '{strategy_name}'. Choose from: {valid_options}"
            )
        return chunker_class(**kwargs)

    @classmethod
    def register(cls, name: str, strategy_class: type[ChunkingStrategy]) -> None:
        """Register a new strategy at runtime (OCP — Open for extension)."""
        cls._registry[name] = strategy_class

    @classmethod
    def available_strategies(cls) -> list[str]:
        """List all registered strategy names."""
        return list(cls._registry.keys())
