# RAG Pipeline

`TechnicalTextChunker` normalizes whitespace, prefers paragraph/sentence boundaries, preserves page and detected heading, and uses configurable overlap. Each chunk carries document ID, filename, page, index, section and source. `EmbeddingProvider` decouples vectors from OpenAI; mock embeddings are normalized deterministic hashing for testability.

Queries are embedded once and ranked using pgvector cosine distance. Scores are converted to similarity (`1 - distance`); only chunks above the configured threshold enter the prompt. Context is serialized inside labeled source boundaries. Source cards are created from database rows, never from model prose.

Evaluation cases measure whether the expected file was retrieved, whether the cited source was correct, and how many expected concepts appear in the answer. Mock mode is useful for pipeline tests; provider-mode evaluation is needed for semantic quality.