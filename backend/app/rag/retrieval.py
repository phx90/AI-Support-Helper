from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.entities import Document, DocumentChunk
from app.rag.embeddings import get_embedding_provider


@dataclass
class SearchResult:
    chunk_id: object
    document_id: object
    document: str
    content: str
    page: int | None
    chunk_index: int
    score: float


def search(db: Session, query: str, limit: int | None = None) -> list[SearchResult]:
    s = get_settings()
    vector = get_embedding_provider().embed([query])[0]
    distance = DocumentChunk.embedding.cosine_distance(vector).label("distance")
    rows = db.execute(
        select(DocumentChunk, Document.name, distance)
        .join(Document)
        .where(Document.status == "indexed")
        .order_by(distance)
        .limit(limit or s.top_k)
    ).all()
    return [
        SearchResult(
            c.id, c.document_id, name, c.content, c.page, c.chunk_index, max(0.0, 1.0 - float(d))
        )
        for c, name, d in rows
    ]


def context_from(results: list[SearchResult]) -> str:
    return "\n\n".join(
        f'<source id="{i}" document="{r.document}" page="{r.page}">\n{r.content}\n</source>'
        for i, r in enumerate(results, 1)
    )
