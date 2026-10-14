class AppError(Exception):
    status_code, code = 500, "internal_error"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    status_code, code = 404, "not_found"


class DocumentProcessingError(AppError):
    status_code, code = 422, "document_processing_error"


class LLMProviderError(AppError):
    status_code, code = 502, "llm_provider_error"


class EmbeddingError(AppError):
    status_code, code = 502, "embedding_error"


class VectorSearchError(AppError):
    status_code, code = 500, "vector_search_error"


class IntegrationError(AppError):
    status_code, code = 502, "integration_error"
