"""
Application Configuration — Singleton Pattern (Module-Level).

Single Source of Truth for all settings across the entire application.
`from infrastructure.config import config` → always returns the SAME instance.
"""

from pathlib import Path


class _SmartDocsConfig:
    """
    Private config class — never instantiate directly.

    Import the `config` singleton instance instead:
        from infrastructure.config import config

    Python caches module-level objects on first import.
    Every subsequent import returns the SAME instance.
    """

    def __init__(self) -> None:
        # ── Paths ──
        self.project_dir: Path = Path(__file__).parent.parent
        self.docs_dir: Path = self.project_dir / "sample_docs"

        # ── Chunking Settings ──
        self.chunk_size: int = 500
        self.chunk_overlap: int = 50

        # ── Model Settings ──
        self.embedding_model: str = "text-embedding-3-small"
        self.chat_model: str = "gpt-4o-mini"

        # ── Retrieval Settings ──
        self.top_k_retrieve: int = 8
        self.top_k_final: int = 3

        # ── Collection Name ──
        self.collection_name: str = "smart_docs_v2"

    def __repr__(self) -> str:
        return (
            f"SmartDocsConfig(model='{self.chat_model}', "
            f"chunk_size={self.chunk_size}, "
            f"docs='{self.docs_dir.name}')"
        )


config = _SmartDocsConfig()
