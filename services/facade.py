"""
SmartDocs Facade — Unified simple interface over the complex subsystem.

Facade Pattern: hides Factory, Builder, Adapters, Decorators, and Events
behind two simple methods: ingest() and search().
"""

from pathlib import Path

from core.models import SearchResult
from core.events import EventBus, LoggingObserver, MetricsObserver
from services.factory import ChunkerFactory
from services.pipeline import IngestPipelineBuilder
from services.search_service import SearchService
from infrastructure.vectorstores import ChromaDBAdapter
from infrastructure.providers import OpenAIProvider
from infrastructure.decorators import CacheDecorator, RetryDecorator, TimingDecorator


class SmartDocsService:
    """
    Facade Pattern — simple API over the entire SmartDocs system.

    Caller only needs:
      service = SmartDocsService()
      service.ingest(docs_dir)
      result = service.search("How to install Docker?")

    Internally it orchestrates Factory, Builder, Adapters, Decorators, Events.
    """

    def __init__(self) -> None:
        self._collection = None

        # Initialize EventBus and subscribe observers (Observer Pattern)
        self.event_bus = EventBus()
        self.event_bus.subscribe(LoggingObserver())
        self.metrics = MetricsObserver()
        self.event_bus.subscribe(self.metrics)

    def ingest(
        self, docs_dir: Path, strategy: str = "heading", use_context: bool = False
    ) -> None:
        """Ingest documents — hides Builder and Factory complexity."""
        chunker = ChunkerFactory.create(strategy)

        builder = IngestPipelineBuilder()
        builder.load_from(docs_dir)
        builder.with_strategy(chunker)

        if use_context:
            builder.with_context()

        self._collection = builder.build()

    def search(self, query: str, use_rerank: bool = True) -> SearchResult:
        """Search ingested documents — hides Adapter, Decorator, and DIP."""
        if self._collection is None:
            raise RuntimeError("Must call ingest() before search().")

        # Adapter Pattern: wrap Chroma collection
        vector_store = ChromaDBAdapter(self._collection)

        # Decorator Pattern: stack decorators on the base LLM provider
        llm = CacheDecorator(
            TimingDecorator(
                RetryDecorator(
                    OpenAIProvider(),
                    retries=3,
                    backoff=1.0,
                )
            )
        )

        search_service = SearchService(llm=llm, vector_store=vector_store)
        return search_service.search(query, use_rerank=use_rerank)
