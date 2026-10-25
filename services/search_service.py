"""
Search Service — RAG search pipeline (DIP Consumer).

High-level module: depends on LLMProvider and VectorStore ABSTRACTIONS,
never on concrete OpenAI or ChromaDB. Swap providers without changing this code.

Pipeline: Retrieve → Rerank → Generate Answer
"""

import json
import time

from core.abstractions import LLMProvider, VectorStore
from core.models import SearchResult
from core.events import EventBus, Event, EventType
from infrastructure.config import config


class SearchService:
    """
    Full search pipeline: Retrieve → Rerank → Answer.

    DIP in action:
      Constructor takes LLMProvider (abstraction) and VectorStore (abstraction).
      This service has ZERO knowledge of whether it's OpenAI or Claude,
      ChromaDB or Pinecone. It just calls the interface methods.
    """

    def __init__(self, llm: LLMProvider, vector_store: VectorStore) -> None:
        self._llm = llm
        self._vector_store = vector_store

    def search(self, query: str, use_rerank: bool = True) -> SearchResult:
        """Execute full search: Retrieve → Rerank → Generate Answer."""
        print(f"\n  🔍 Searching: '{query}'")

        EventBus().publish(Event(
            event_type=EventType.SEARCH_STARTED,
            data={"query": query},
            timestamp=time.time(),
        ))

        # Step 1: Retrieve top K chunks from vector DB
        chunks = self._retrieve(query)
        print(f"  📄 Retrieved {len(chunks)} candidate chunks")

        # Step 2: Rerank (optional but recommended)
        if use_rerank:
            chunks = self._rerank(query, chunks)
            print(f"  🏆 Reranked → top {len(chunks)} chunks selected")
        else:
            chunks = chunks[:config.top_k_final]
            print(f"  ⚡ Skipped reranking → top {len(chunks)} by distance")

        # Step 3: Generate answer using LLM
        result = self._generate_answer(query, chunks)
        print(f"  ✅ Answer generated from {result.chunks_used} chunks")
        print(f"  📚 Sources: {', '.join(result.sources)}")

        EventBus().publish(Event(
            event_type=EventType.SEARCH_COMPLETED,
            data={
                "query": query,
                "chunks_used": result.chunks_used,
                "sources": result.sources,
            },
            timestamp=time.time(),
        ))

        return result

    def _retrieve(self, query: str) -> list[dict[str, str | dict[str, str] | float]]:
        """Vector similarity search — nearest chunks."""
        return self._vector_store.query(
            query_text=query,
            n_results=config.top_k_retrieve,
        )

    def _rerank(
        self,
        query: str,
        chunks: list[dict[str, str | dict[str, str] | float]],
    ) -> list[dict[str, str | dict[str, str] | float]]:
        """LLM-based reranking — score each chunk's relevance."""
        if not chunks:
            return []

        chunks_text = ""
        for i, chunk in enumerate(chunks):
            text = str(chunk["text"])[:300]
            chunks_text += f"\n[CHUNK {i}]:\n{text}\n"

        system_prompt = (
            "You are a relevance scoring system.\n"
            "Score each chunk's relevance to the query on a scale of 0-10.\n"
            "Return ONLY a JSON object with a 'scores' key containing an array."
        )
        user_prompt = f"Query: {query}\n\nChunks to score:{chunks_text}"

        raw_response = self._llm.complete_json(system_prompt, user_prompt)

        try:
            parsed = json.loads(raw_response)
            scores: list[int] = (
                list(parsed.values())[0]
                if isinstance(parsed, dict) else parsed
            )
        except (json.JSONDecodeError, KeyError, IndexError):
            return chunks[:config.top_k_final]

        for i, chunk in enumerate(chunks):
            chunk["rerank_score"] = scores[i] if i < len(scores) else 0

        ranked = sorted(
            chunks,
            key=lambda x: int(x.get("rerank_score", 0)),
            reverse=True,
        )
        return ranked[:config.top_k_final]

    def _generate_answer(
        self,
        query: str,
        chunks: list[dict[str, str | dict[str, str] | float]],
    ) -> SearchResult:
        """RAG answer generation — context + LLM = answer."""
        if not chunks:
            return SearchResult(
                answer="Sorry, no relevant documents found.",
                sources=[],
                chunks_used=0,
            )

        context = ""
        sources: set[str] = set()
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            source = (
                str(metadata.get("source", "unknown"))
                if isinstance(metadata, dict) else "unknown"
            )
            context += f"\n--- Source: {source} ---\n{chunk['text']}\n"
            sources.add(source)

        system_prompt = (
            "You are a helpful documentation search assistant.\n"
            "Answer ONLY using the provided context.\n"
            "If the answer is not in the context, say so.\n"
            "Be concise, reference the source document."
        )
        user_prompt = f"Question: {query}\n\nContext:\n{context}"

        answer = self._llm.complete(system_prompt, user_prompt)

        return SearchResult(
            answer=answer,
            sources=list(sources),
            chunks_used=len(chunks),
        )
