"""
ChromaDB Adapter — Implements VectorStore abstraction (Adapter Pattern).

Wraps chromadb.Collection behind our VectorStore interface.
Swap to Qdrant or Pinecone by creating a new adapter — zero service changes.
"""

import chromadb

from core.abstractions import VectorStore


class ChromaDBAdapter(VectorStore):
    """Adapter bridging chromadb.Collection to our VectorStore contract."""

    def __init__(self, collection: chromadb.Collection) -> None:
        self._collection = collection

    def query(
        self, query_text: str, n_results: int
    ) -> list[dict[str, str | dict[str, str] | float]]:
        results = self._collection.query(
            query_texts=[query_text],
            n_results=n_results,
        )

        chunks: list[dict[str, str | dict[str, str] | float]] = []
        documents = results.get("documents")
        metadatas = results.get("metadatas")
        distances = results.get("distances")

        if documents and metadatas and distances and len(documents) > 0:
            for i in range(len(documents[0])):
                chunks.append({
                    "text": documents[0][i],
                    "metadata": metadatas[0][i],
                    "distance": distances[0][i],
                })
        return chunks
