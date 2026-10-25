"""
Fixed-Size Chunking Strategy.

Simplest approach: cut every N characters with configurable overlap.
Fast but may split mid-sentence. Best for quick prototyping or very large files.
"""

from core.abstractions import ChunkingStrategy
from core.models import Chunk
from infrastructure.config import config


class FixedChunking(ChunkingStrategy):
    """Cut text into fixed-size windows with configurable overlap."""

    def __init__(
        self,
        chunk_size: int = config.chunk_size,
        overlap: int = config.chunk_overlap,
    ) -> None:
        self._chunk_size = chunk_size
        self._overlap = overlap

    def chunk(self, text: str, source: str) -> list[Chunk]:
        chunks: list[Chunk] = []
        start = 0
        index = 0

        while start < len(text):
            end = start + self._chunk_size
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(Chunk(
                    text=chunk_text,
                    source=source,
                    strategy="fixed",
                    chunk_index=index,
                ))
                index += 1

            start += self._chunk_size - self._overlap

        return chunks
