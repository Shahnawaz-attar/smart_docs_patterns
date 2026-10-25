"""
Core Domain Models — Pure Data Containers (SRP).

These dataclasses hold data only. No business logic, no I/O, no external deps.
Each class has a SINGLE responsibility: hold its data with type safety.
"""

from dataclasses import dataclass, field


@dataclass
class Document:
    """Loaded document file representation."""
    filename: str
    content: str


@dataclass
class Chunk:
    """A chunked piece of a document after splitting."""
    text: str
    source: str          # Which file this came from (e.g., "docker_basics.md")
    strategy: str        # Which strategy created it (e.g., "heading")
    chunk_index: int = 0
    heading: str = ""    # Populated by heading-based chunking
    extra: dict[str, str] = field(default_factory=dict)


@dataclass
class SearchResult:
    """Final output of the search pipeline."""
    answer: str
    sources: list[str]
    chunks_used: int
