# What is RAG?

Retrieval-Augmented Generation (RAG) is a technique that enhances large language models (LLMs) by retrieving facts from an external knowledge base to ground its responses on the most accurate, up-to-date information.

## How it works
1. **Ingestion**: Documents are divided into chunks and converted to embeddings (vectors) using an embedding model. These are stored in a vector database like ChromaDB.
2. **Retrieval**: When a user asks a question, the system searches the vector database for the most relevant document chunks.
3. **Generation**: The retrieved chunks are passed to the LLM along with the original question to generate an accurate, grounded answer.

RAG prevents hallucinations because the LLM relies on your actual documents rather than its pre-trained memory.
