# 🏗️ Smart Docs v2 — Enterprise Edition (Clean Architecture)

## 📌 Ye Project Kya Hai?

AI Documentation Search Engine (RAG Pipeline) built with **9 Design Patterns** 
organized in **Clean Architecture** — the same structure used at Google, Netflix, 
and top tech companies for production systems.

---

## 🏛️ Architecture Overview

```
06_smart_docs_patterns/
│
├── core/                          ← DOMAIN LAYER (Pure Logic, Zero External Deps)
│   ├── models.py                  │  Document, Chunk, SearchResult (SRP)
│   ├── abstractions.py            │  ChunkingStrategy, LLMProvider, VectorStore (DIP)
│   └── events.py                  │  EventBus, Observer, EventType (Observer Pattern)
│
├── infrastructure/                ← ADAPTER LAYER (External Tech Integrations)
│   ├── config.py                  │  Singleton settings
│   ├── vectorstores/              │
│   │   └── chroma_adapter.py      │  ChromaDB ↔ VectorStore (Adapter Pattern)
│   ├── providers/                 │
│   │   ├── openai_provider.py     │  OpenAI ↔ LLMProvider
│   │   └── inmemory_provider.py   │  Mock LLM for testing
│   ├── chunking/                  │
│   │   ├── fixed.py               │  FixedChunking (Strategy)
│   │   ├── recursive.py           │  RecursiveChunking (Strategy)
│   │   └── heading.py             │  HeadingChunking (Strategy)
│   └── decorators/                │
│       ├── base.py                │  LLMDecorator base
│       ├── retry.py               │  RetryDecorator (Decorator Pattern)
│       ├── cache.py               │  CacheDecorator
│       └── timing.py              │  TimingDecorator
│
├── services/                      ← APPLICATION LAYER (Business Orchestration)
│   ├── factory.py                 │  ChunkerFactory (Factory + OCP)
│   ├── pipeline.py                │  IngestPipelineBuilder (Builder Pattern)
│   ├── search_service.py          │  SearchService (DIP Consumer)
│   └── facade.py                  │  SmartDocsService (Facade Pattern)
│
├── main.py                        ← COMPOSITION ROOT (Wires everything)
├── sample_docs/                   ← Data files
└── requirements.txt
```

---

## 🗺️ PATTERN MAP — Kaunsi File Mein Kaunsa Pattern?

| Pattern | File | Purpose |
|---------|------|---------|
| **Singleton** | `infrastructure/config.py` | Settings ek jagah centralized |
| **SRP** | `core/models.py` | Pure data containers, zero logic |
| **Strategy** | `infrastructure/chunking/` | 3 chunking algorithms, runtime swap |
| **Factory + OCP** | `services/factory.py` | Create chunkers by name, register new ones |
| **Observer** | `core/events.py` | Decoupled event broadcasting & metrics |
| **Builder** | `services/pipeline.py` | Step-by-step ingestion with method chaining |
| **DIP + Adapter** | `core/abstractions.py` + `infrastructure/vectorstores/` | Abstract contracts + concrete wrappers |
| **Decorator** | `infrastructure/decorators/` | Retry, Cache, Timing wrapped on LLM |
| **Facade** | `services/facade.py` | Simple interface over the complex system |

---

## 🧠 Dependency Flow (Clean Architecture)

```
main.py (Composition Root)
  │
  ├── core/ ──────────────── PURE DOMAIN (zero external deps)
  │   ├── models             Document, Chunk, SearchResult
  │   ├── abstractions       ChunkingStrategy, LLMProvider, VectorStore
  │   └── events             EventBus, Observer
  │
  ├── infrastructure/ ────── ADAPTERS (implements core abstractions)
  │   ├── config             Singleton settings
  │   ├── chunking/          Fixed, Recursive, Heading → ChunkingStrategy
  │   ├── providers/         OpenAI, InMemory → LLMProvider
  │   ├── vectorstores/      ChromaDB → VectorStore
  │   └── decorators/        Retry, Cache, Timing → LLMProvider wrapper
  │
  └── services/ ─────────── ORCHESTRATION (uses core abstractions)
      ├── factory            ChunkerFactory.create("heading")
      ├── pipeline           IngestPipelineBuilder().load().chunk().build()
      ├── search_service     SearchService(llm, vector_store)
      └── facade             SmartDocsService — one simple API
```

**Key Rule:** `core/` never imports from `infrastructure/` or `services/`. Dependencies flow INWARD only.

---

## 🎯 KAISE PADHNA HAI? (Step-by-Step Roadmap)

1. `core/models.py` → **SRP** — Pure data containers
2. `core/abstractions.py` → **DIP** — Contracts/Interfaces everyone depends on
3. `core/events.py` → **Observer** — Decoupled event system
4. `infrastructure/config.py` → **Singleton** — Centralized settings
5. `infrastructure/chunking/` → **Strategy** — 3 interchangeable chunking algorithms
6. `infrastructure/providers/` → **DIP Concrete** — OpenAI + Mock implementations
7. `infrastructure/vectorstores/` → **Adapter** — ChromaDB behind abstract interface
8. `infrastructure/decorators/` → **Decorator** — Retry, Cache, Timing layers
9. `services/factory.py` → **Factory + OCP** — Create chunkers, register new ones
10. `services/pipeline.py` → **Builder** — Step-by-step ingestion pipeline
11. `services/search_service.py` → **DIP Consumer** — Search using injected abstractions
12. `services/facade.py` → **Facade** — Simple API over the complex system
13. `main.py` → **Composition Root** — Where concrete meets abstract

---

## 🚀 How to Run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### CLI Options
```bash
python main.py                      # Heading + Rerank (default)
python main.py --strategy fixed     # Fixed chunking
python main.py --strategy recursive # Recursive chunking
python main.py --no-rerank          # Skip LLM reranking
python main.py --context            # Enable Contextual Retrieval
```
# 06_smart_docs_patterns
# 06_smart_docs_patterns
