import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.entities import DocumentStatus, TicketCategory, TicketPriority, TicketStatus


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Page(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int


class DocumentOut(ORMModel):
    id: uuid.UUID
    name: str
    file_type: str
    size: int
    status: DocumentStatus
    chunk_count: int
    processed_at: datetime | None
    error_message: str | None
    metadata_: dict[str, Any] = Field(serialization_alias="metadata")
    created_at: datetime


class TicketCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=5, max_length=5000)
    category: TicketCategory = TicketCategory.other
    priority: TicketPriority = TicketPriority.medium


class TicketUpdate(BaseModel):
    status: TicketStatus


class TicketOut(ORMModel):
    id: uuid.UUID
    title: str
    description: str
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus
    created_at: datetime
    updated_at: datetime


class ClassificationRequest(BaseModel):
    description: str = Field(min_length=5, max_length=5000)


class ClassificationResult(BaseModel):
    category: TicketCategory
    priority: TicketPriority
    summary: str
    suggested_action: str


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=5000)
    conversation_id: uuid.UUID | None = None


class Source(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document: str
    page: int | None
    chunk_index: int
    excerpt: str
    similarity_score: float


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    message_id: uuid.UUID
    answer: str
    sources: list[Source]
    tool_calls: list[str] = []
    latency_ms: float
    model: str


class MessageOut(ORMModel):
    id: uuid.UUID
    role: str
    content: str
    model: str | None
    latency_ms: float | None
    retrieved_chunks: list[dict[str, Any]]
    created_at: datetime


class ConversationOut(ORMModel):
    id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageOut] = []


class ConversationRename(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class FeedbackCreate(BaseModel):
    message_id: uuid.UUID
    rating: Literal[-1, 1]
    optional_comment: str | None = Field(None, max_length=1000)


class FeedbackOut(ORMModel):
    id: uuid.UUID
    message_id: uuid.UUID
    rating: int
    optional_comment: str | None
    created_at: datetime
