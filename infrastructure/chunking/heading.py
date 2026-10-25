"""
Heading-Based Chunking Strategy.

Best for documentation — each Markdown heading creates a natural chunk boundary.
Falls back to RecursiveChunking for oversized sections.
"""

from core.abstractions import ChunkingStrategy
from core.models import Chunk
from infrastructure.config import config
from infrastructure.chunking.recursive import RecursiveChunking


class HeadingChunking(ChunkingStrategy):
    """Split on Markdown headings. Oversized sections get recursive sub-splitting."""

    def __init__(self, chunk_size: int = config.chunk_size) -> None:
        self._chunk_size = chunk_size
        self._fallback = RecursiveChunking(chunk_size=chunk_size)

    def chunk(self, text: str, source: str) -> list[Chunk]:
        sections = self._extract_sections(text)

        chunks: list[Chunk] = []
        for section in sections:
            content = section["content"]
            if not content:
                continue

            heading = section["heading"]

            if len(content) <= self._chunk_size:
                chunks.append(Chunk(
                    text=f"## {heading}\n\n{content}",
                    source=source,
                    strategy="heading",
                    chunk_index=len(chunks),
                    heading=heading,
                ))
            else:
                sub_chunks = self._fallback.chunk(content, source)
                for j, sub in enumerate(sub_chunks):
                    chunks.append(Chunk(
                        text=f"## {heading} (Part {j + 1})\n\n{sub.text}",
                        source=source,
                        strategy="heading",
                        chunk_index=len(chunks),
                        heading=heading,
                    ))

        return chunks

    def _extract_sections(self, text: str) -> list[dict[str, str]]:
        """Extract heading-content pairs from Markdown text."""
        lines = text.split("\n")
        sections: list[dict[str, str]] = []
        current_heading = "Introduction"
        current_content: list[str] = []

        for line in lines:
            if line.startswith("#"):
                if current_content:
                    sections.append({
                        "heading": current_heading,
                        "content": "\n".join(current_content).strip(),
                    })
                current_heading = line.lstrip("#").strip()
                current_content = []
            else:
                current_content.append(line)

        if current_content:
            sections.append({
                "heading": current_heading,
                "content": "\n".join(current_content).strip(),
            })

        return sections
