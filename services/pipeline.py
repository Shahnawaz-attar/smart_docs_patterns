"""
Ingest Pipeline — Builder Pattern for step-by-step document ingestion.

Builder Pattern: construct the pipeline with method chaining.
  collection = (
      IngestPipelineBuilder()
      .load_from(docs_dir)
      .with_strategy(chunker)
      .with_context()          ← optional step
      .build()
  )
"""

import time
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions

from core.models import Document, Chunk
from core.abstractions import ChunkingStrategy
from core.events import EventBus, Event, EventType
from infrastructure.config import config

load_dotenv()


class IngestPipelineBuilder:
    """
    Builder for constructing the document ingestion pipeline step-by-step.

    Each method returns self for method chaining.
    .build() executes the full pipeline and returns the ChromaDB collection.
    """

    def __init__(self) -> None:
        self._documents: list[Document] = []
        self._chunks: list[Chunk] = []
        self._strategy: ChunkingStrategy | None = None
        self._use_context: bool = False
        self._docs_loaded: bool = False
        self._chunks_created: bool = False

    # ── Step 1: Load Documents ──
    def load_from(self, docs_dir: Path) -> "IngestPipelineBuilder":
        """Step 1: Load all .md documents from the given directory."""
        print("\n  📥 Step 1: Loading documents...")

        if not docs_dir.exists():
            raise FileNotFoundError(f"Docs directory not found: {docs_dir}")

        for file_path in sorted(docs_dir.glob("*.md")):
            content = file_path.read_text(encoding="utf-8")
            self._documents.append(Document(
                filename=file_path.name,
                content=content,
            ))
            print(f"    📄 Loaded: {file_path.name} ({len(content)} chars)")

        if not self._documents:
            raise FileNotFoundError(f"No .md files found in {docs_dir}")

        self._docs_loaded = True
        print(f"    ✅ {len(self._documents)} documents loaded")

        EventBus().publish(Event(
            event_type=EventType.DOCS_LOADED,
            data={"count": len(self._documents), "dir": str(docs_dir)},
            timestamp=time.time(),
        ))

        return self

    # ── Step 2: Set Chunking Strategy ──
    def with_strategy(self, strategy: ChunkingStrategy) -> "IngestPipelineBuilder":
        """Step 2: Set the chunking strategy (accepts any ChunkingStrategy)."""
        self._strategy = strategy
        print(f"\n  ⚙️  Step 2: Strategy set → {strategy.__class__.__name__}")
        return self

    # ── Step 3: Enable Contextual Retrieval (OPTIONAL) ──
    def with_context(self) -> "IngestPipelineBuilder":
        """Step 3 (OPTIONAL): Enable contextual retrieval headers via LLM."""
        self._use_context = True
        print("\n  🔗 Step 3: Contextual Retrieval ENABLED")
        return self

    # ── Final Step: BUILD ──
    def build(self) -> chromadb.Collection:
        """Execute the full pipeline and return the ChromaDB collection."""
        if not self._docs_loaded:
            raise RuntimeError("Call .load_from() before .build()!")
        if self._strategy is None:
            raise RuntimeError("Call .with_strategy() before .build()!")

        # ── Chunk all documents ──
        print(f"\n  ✂️  Chunking {len(self._documents)} documents...")
        for doc in self._documents:
            doc_chunks = self._strategy.chunk(doc.content, doc.filename)
            self._chunks.extend(doc_chunks)
            print(f"    📄 {doc.filename} → {len(doc_chunks)} chunks")
        print(f"    ✅ Total: {len(self._chunks)} chunks")

        EventBus().publish(Event(
            event_type=EventType.CHUNKS_CREATED,
            data={"total_chunks": len(self._chunks)},
            timestamp=time.time(),
        ))

        # ── Contextual Retrieval (optional) ──
        if self._use_context:
            self._add_context_to_chunks()

        # ── Embed and Store ──
        return self._store_in_chromadb()

    def _add_context_to_chunks(self) -> None:
        """Add contextual headers using LLM (Anthropic technique)."""
        print("\n  🔗 Adding contextual headers...")
        llm_client = OpenAI()

        for i, chunk in enumerate(self._chunks):
            full_doc = next(
                (d.content for d in self._documents if d.filename == chunk.source),
                "",
            )
            response = llm_client.chat.completions.create(
                model=config.chat_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Generate a 2-sentence context for this document chunk. "
                            "Include the source topic and what this section discusses."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Document: {chunk.source}\n"
                            f"Preview: {full_doc[:800]}\n\n"
                            f"Chunk:\n{chunk.text}"
                        ),
                    },
                ],
                temperature=0,
                max_tokens=100,
            )
            context = response.choices[0].message.content
            if context:
                chunk.text = f"[CONTEXT: {context.strip()}]\n\n{chunk.text}"
            print(f"    ✅ Chunk {i + 1}/{len(self._chunks)} contextualized")

    def _store_in_chromadb(self) -> chromadb.Collection:
        """Embed chunks and store in ChromaDB."""
        print("\n  💾 Storing in ChromaDB...")

        chroma_client = chromadb.Client()
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            model_name=config.embedding_model,
        )

        # Fresh collection (safe delete for demo)
        try:
            chroma_client.delete_collection(config.collection_name)
        except Exception:
            pass

        collection = chroma_client.create_collection(
            name=config.collection_name,
            embedding_function=openai_ef,
        )

        collection.add(
            ids=[f"chunk_{i}" for i in range(len(self._chunks))],
            documents=[chunk.text for chunk in self._chunks],
            metadatas=[
                {
                    "source": chunk.source,
                    "strategy": chunk.strategy,
                    "heading": chunk.heading,
                }
                for chunk in self._chunks
            ],
        )

        print(f"    ✅ {collection.count()} chunks stored")
        print(f"    ✅ Embedding model: {config.embedding_model}")
        return collection
