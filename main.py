"""
Smart Docs v2 — Enterprise Edition (All Design Patterns in Action)

ARCHITECTURE:
  core/           → Domain models + abstractions (zero external deps)
  infrastructure/ → OpenAI, ChromaDB, Decorators (adapters)
  services/       → Factory, Pipeline, SearchService, Facade (orchestration)
  main.py         → Composition Root (wires everything together)

PATTERNS USED:
  1. Singleton    → infrastructure/config.py
  2. SRP          → core/models.py
  3. Strategy     → infrastructure/chunking/
  4. Factory      → services/factory.py
  5. Observer     → core/events.py
  6. Builder      → services/pipeline.py
  7. DIP+Adapter  → core/abstractions.py + infrastructure/vectorstores/
  8. Decorator    → infrastructure/decorators/
  9. Facade       → services/facade.py

HOW TO RUN:
  python main.py                    → Heading + Rerank (default)
  python main.py --strategy fixed   → Fixed chunking
  python main.py --no-rerank        → Skip reranking
  python main.py --context          → Contextual Retrieval ON
"""

import sys

from infrastructure.config import config
from services.factory import ChunkerFactory
from services.pipeline import IngestPipelineBuilder
from services.search_service import SearchService
from services.facade import SmartDocsService  # ← Pattern 09: Facade (optional one-line usage)
from infrastructure.providers import OpenAIProvider
from infrastructure.vectorstores import ChromaDBAdapter


def print_banner() -> None:
    """Project banner."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   📚  SMART DOCS v2 — Enterprise Edition 🏗️              ║
    ║                                                           ║
    ║   Architecture: Clean Architecture (core → infra → svc)  ║
    ║   Patterns: Singleton + SRP + Strategy + Factory +        ║
    ║             Observer + Builder + DIP + Adapter +           ║
    ║             Decorator + Facade                            ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)


def parse_args() -> dict[str, str | bool]:
    """Parse command-line arguments."""
    args: dict[str, str | bool] = {
        "strategy": "heading",
        "use_context": False,
        "use_rerank": True,
    }

    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--context":
            args["use_context"] = True
        elif arg == "--no-rerank":
            args["use_rerank"] = False
        elif arg == "--strategy" and i + 2 < len(sys.argv):
            args["strategy"] = sys.argv[i + 2]
        elif arg in ("fixed", "recursive", "heading"):
            args["strategy"] = arg
        elif arg in ("--help", "-h"):
            print(
                "Usage: python main.py "
                "[--strategy fixed|recursive|heading] [--context] [--no-rerank]"
            )
            sys.exit(0)

    return args


def main() -> None:
    """
    Composition Root — wires all layers together and runs the app.

    This is the ONLY place where concrete classes meet.
    Services never import concrete implementations directly.
    """
    print_banner()

    args = parse_args()
    strategy_name = str(args["strategy"])
    use_context = bool(args["use_context"])
    use_rerank = bool(args["use_rerank"])

    print(f"    ⚙️  Strategy: {strategy_name}")
    print(f"    ⚙️  Contextual Retrieval: {'ON' if use_context else 'OFF'}")
    print(f"    ⚙️  Reranking: {'ON' if use_rerank else 'OFF'}")

    # ══════════════════════════════════════════════════════════════════
    # 💡 ALTERNATIVE: FACADE PATTERN (services/facade.py)
    # ══════════════════════════════════════════════════════════════════
    # Production ya APIs (FastAPI) mein hum niche ke saare manual steps
    # (Factory, Builder, Adapter, DIP) ki jagah sirf 2 lines likhte hain:
    #
    # service = SmartDocsService()
    # service.ingest(config.docs_dir, strategy=strategy_name, use_context=use_context)
    
    #
    # Yahan learning ke liye hum step-by-step khol ke chala rahe hain 👇
    # ══════════════════════════════════════════════════════════════════

    # ── FACTORY PATTERN: Create chunker by name ──
    chunker = ChunkerFactory.create(strategy_name)
    print(f"\n  🏭 Factory created: {chunker.__class__.__name__}")

    # # ── BUILDER PATTERN: Pipeline step-by-step ──
    builder = IngestPipelineBuilder()
    builder.load_from(config.docs_dir)
    builder.with_strategy(chunker)

    if use_context:
        builder.with_context()

    collection = builder.build()

    # # ── DIP + ADAPTER: Inject abstractions into SearchService ──
    llm = OpenAIProvider()
    vector_store = ChromaDBAdapter(collection)
    search_service = SearchService(llm=llm, vector_store=vector_store)

    # ── Interactive Search Loop ──
    print("\n" + "=" * 60)
    print("  🔎 Ready! Type your question (or 'quit' to exit)")
    print("=" * 60)

    while True:
        print()
        query = input("  ❓ Your question: ").strip()

        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            print("\n  👋 Goodbye! Happy learning!")
            break
        # result = service.search(query, use_rerank=use_rerank)
        result = search_service.search(query, use_rerank=use_rerank)

        print(f"\n  {'─' * 56}")
        print(f"  📝 ANSWER:\n")
        print(f"  {result.answer}")
        print(f"\n  {'─' * 56}")
        print(f"  📚 Sources: {', '.join(result.sources)}")
        print(f"  📊 Chunks used: {result.chunks_used}")


if __name__ == "__main__":
    main()
