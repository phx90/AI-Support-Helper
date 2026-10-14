import hashlib
import math
from abc import ABC, abstractmethod

from openai import OpenAI

from app.core.config import Settings, get_settings
from app.core.exceptions import EmbeddingError


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class MockEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimensions: int):
        self.dimensions = dimensions

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        for text in texts:
            v = [0.0] * self.dimensions
            for token in text.lower().split():
                digest = hashlib.sha256(token.encode()).digest()
                idx = int.from_bytes(digest[:4], "big") % self.dimensions
                v[idx] += 1.0 if digest[4] % 2 else -1.0
            norm = math.sqrt(sum(x * x for x in v)) or 1.0
            vectors.append([x / norm for x in v])
        return vectors


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, s: Settings):
        self.client = OpenAI(api_key=s.openai_api_key)
        self.model = s.embedding_model
        self.dimensions = s.embedding_dimensions

    def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            return [
                x.embedding
                for x in self.client.embeddings.create(
                    model=self.model, input=texts, dimensions=self.dimensions
                ).data
            ]
        except Exception as exc:
            raise EmbeddingError("Embedding provider unavailable") from exc


def get_embedding_provider(s: Settings | None = None) -> EmbeddingProvider:
    s = s or get_settings()
    return (
        MockEmbeddingProvider(s.embedding_dimensions)
        if s.llm_mock_mode
        else OpenAIEmbeddingProvider(s)
    )
