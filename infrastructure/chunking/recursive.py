"""
Recursive Character Splitting Strategy.

LangChain's default — splits by paragraph → line → sentence → word.
Production-grade smart boundary detection. Most commonly used in real RAG systems.
"""

from core.abstractions import ChunkingStrategy
from core.models import Chunk
from infrastructure.config import config


class RecursiveChunking(ChunkingStrategy):
    """Recursive splitting with hierarchical separators."""

    def __init__(
        self,
        chunk_size: int = config.chunk_size,
        overlap: int = config.chunk_overlap,
    ) -> None:
        self._chunk_size = chunk_size
        self._overlap = overlap
        self._separators = ["\n\n", "\n", ". ", " "]

    def chunk(self, text: str, source: str) -> list[Chunk]:
        raw_chunks = self._split_recursive(text, sep_index=0)

        chunks: list[Chunk] = []
        for i, chunk_text in enumerate(raw_chunks):
            clean_text = chunk_text.strip()
            if clean_text:
                chunks.append(Chunk(
                    text=clean_text,
                    source=source,
                    strategy="recursive",
                    chunk_index=i,
                ))

        return chunks

    def _split_recursive(self, text_to_split: str, sep_index: int) -> list[str]:
        """Internal recursive splitter — tries biggest separator first."""
        if sep_index >= len(self._separators):
            return [
                text_to_split[i:i + self._chunk_size]
                for i in range(0, len(text_to_split), self._chunk_size - self._overlap)
            ]

        separator = self._separators[sep_index]
        parts = text_to_split.split(separator)

        result: list[str] = []
        current = ""

        for part in parts:
            test = current + separator + part if current else part
            if len(test) <= self._chunk_size:
                current = test
            else:
                if current:
                    result.append(current)
                if len(part) > self._chunk_size:
                    result.extend(self._split_recursive(part, sep_index + 1))
                else:
                    current = part

        if current:
            result.append(current)

        return result
