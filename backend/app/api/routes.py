import uuid

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, File, Query, UploadFile
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import NotFoundError
from app.core.logging import logger
from app.database.base import SessionLocal, get_db
from app.integrations.n8n import notify_document_indexed
from app.models.entities import Conversation, Document, DocumentChunk, Feedback, Message, Ticket
from app.repositories.base import Repository
from app.schemas.api import (
    ChatRequest,
    ChatResponse,
    ClassificationRequest,
    ClassificationResult,
    ConversationOut,
    ConversationRename,
    DocumentOut,
    FeedbackCreate,
    FeedbackOut,
    Page,
    TicketCreate,
    TicketOut,
    TicketUpdate,
)
from app.services.chat_service import chat
from app.services.document_service import create_document, delete_document, process_document
from app.services.ticket_service import classify_incident, create_ticket, get_ticket

router = APIRouter()


def process_in_background(document_id: uuid.UUID):
    with SessionLocal() as db:
        try:
            doc = process_document(db, document_id)
            try:
                notify_document_indexed(
                    {
                        "document_id": str(doc.id),
                        "name": doc.name,
                        "chunks": doc.chunk_count,
                        "status": "indexed",
                    }
                )
            except Exception as exc:
                logger.warning(
                    "indexing_webhook_failed", document_id=str(document_id), error=str(exc)
                )
        except Exception as exc:
            logger.exception(
                "document_indexing_failed", document_id=str(document_id), error=str(exc)
            )


@router.post("/documents", response_model=DocumentOut, status_code=202)
async def upload_document(
    background: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    data = await file.read()
    doc = create_document(db, file.filename or "document", data)
    background.add_task(process_in_background, doc.id)
    return doc


@router.get("/documents", response_model=Page)
def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    q = select(Document)
    count = select(func.count()).select_from(Document)
    if status:
        q = q.where(Document.status == status)
        count = count.where(Document.status == status)
    if search:
        q = q.where(Document.name.ilike(f"%{search}%"))
        count = count.where(Document.name.ilike(f"%{search}%"))
    return Page(
        items=[
            DocumentOut.model_validate(x).model_dump(mode="json", by_alias=True)
            for x in db.scalars(
                q.order_by(Document.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ],
        total=db.scalar(count) or 0,
        page=page,
        page_size=page_size,
    )


@router.get("/documents/{document_id}", response_model=DocumentOut)
def document_detail(document_id: uuid.UUID, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if not doc:
        raise NotFoundError("Document not found")
    return doc


@router.post("/documents/{document_id}/reprocess", response_model=DocumentOut)
def reprocess(document_id: uuid.UUID, db: Session = Depends(get_db)):
    return process_document(db, document_id)


@router.delete("/documents/{document_id}", status_code=204)
def remove_document(document_id: uuid.UUID, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if not doc:
        raise NotFoundError("Document not found")
    delete_document(db, doc)


@router.post("/chat", response_model=ChatResponse)
def ask(data: ChatRequest, db: Session = Depends(get_db)):
    return chat(db, data)


@router.get("/conversations", response_model=Page)
def conversations(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    items, total = Repository(db, Conversation).list(
        page, page_size, Conversation.updated_at.desc()
    )
    return Page(
        items=[ConversationOut.model_validate(x).model_dump(mode="json") for x in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationOut)
def conversation(conversation_id: uuid.UUID, db: Session = Depends(get_db)):
    value = db.get(Conversation, conversation_id)
    if not value:
        raise NotFoundError("Conversation not found")
    return value


@router.patch("/conversations/{conversation_id}", response_model=ConversationOut)
def rename_conversation(
    conversation_id: uuid.UUID, data: ConversationRename, db: Session = Depends(get_db)
):
    value = db.get(Conversation, conversation_id)
    if not value:
        raise NotFoundError("Conversation not found")
    value.title = data.title
    db.commit()
    db.refresh(value)
    return value


@router.delete("/conversations/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: uuid.UUID, db: Session = Depends(get_db)):
    value = db.get(Conversation, conversation_id)
    if not value:
        raise NotFoundError("Conversation not found")
    db.delete(value)
    db.commit()


@router.post("/tickets", response_model=TicketOut, status_code=201)
def new_ticket(data: TicketCreate, db: Session = Depends(get_db)):
    return create_ticket(db, data)


@router.get("/tickets", response_model=Page)
def tickets(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    items, total = Repository(db, Ticket).list(page, page_size, Ticket.created_at.desc())
    return Page(
        items=[TicketOut.model_validate(x).model_dump(mode="json") for x in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/tickets/{ticket_id}", response_model=TicketOut)
def ticket(ticket_id: uuid.UUID, db: Session = Depends(get_db)):
    return get_ticket(db, ticket_id)


@router.patch("/tickets/{ticket_id}", response_model=TicketOut)
def update_ticket(ticket_id: uuid.UUID, data: TicketUpdate, db: Session = Depends(get_db)):
    value = get_ticket(db, ticket_id)
    value.status = data.status
    db.commit()
    db.refresh(value)
    return value


@router.post("/classify", response_model=ClassificationResult)
def classify(data: ClassificationRequest):
    return classify_incident(data.description)


@router.post("/feedback", response_model=FeedbackOut, status_code=201)
def feedback(data: FeedbackCreate, db: Session = Depends(get_db)):
    if not db.get(Message, data.message_id):
        raise NotFoundError("Message not found")
    existing = db.scalar(select(Feedback).where(Feedback.message_id == data.message_id))
    value = existing or Feedback(
        message_id=data.message_id, rating=data.rating, optional_comment=data.optional_comment
    )
    value.rating = data.rating
    value.optional_comment = data.optional_comment
    db.add(value)
    db.commit()
    db.refresh(value)
    return value


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    positive = (
        db.scalar(select(func.count()).select_from(Feedback).where(Feedback.rating == 1)) or 0
    )
    feedback_total = db.scalar(select(func.count()).select_from(Feedback)) or 0
    recent = list(
        db.execute(
            select(Message.content, Message.latency_ms, Message.created_at)
            .where(Message.role == "user")
            .order_by(Message.created_at.desc())
            .limit(5)
        ).all()
    )
    return {
        "documents": db.scalar(select(func.count()).select_from(Document)) or 0,
        "chunks": db.scalar(select(func.count()).select_from(DocumentChunk)) or 0,
        "conversations": db.scalar(select(func.count()).select_from(Conversation)) or 0,
        "questions": db.scalar(
            select(func.count()).select_from(Message).where(Message.role == "user")
        )
        or 0,
        "positive_feedback_percentage": round(100 * positive / feedback_total, 1)
        if feedback_total
        else 0,
        "recent_queries": [
            {"question": r.content, "latency_ms": r.latency_ms, "created_at": r.created_at}
            for r in recent
        ],
    }


@router.get("/status")
def status(db: Session = Depends(get_db)):
    s = get_settings()
    database = "healthy"
    pgvector = "healthy"
    try:
        db.execute(text("SELECT 1"))
        db.execute(text("SELECT extversion FROM pg_extension WHERE extname='vector'"))
    except Exception:
        database = "unavailable"
        pgvector = "unavailable"
    llm = (
        "healthy"
        if s.llm_mock_mode
        or (s.openai_api_key if s.llm_provider == "openai" else s.anthropic_api_key)
        else "degraded"
    )
    try:
        httpx.get(f"{s.n8n_base_url}/healthz", timeout=1).raise_for_status()
        n8n = "healthy"
    except Exception:
        n8n = "unavailable"
    return {
        "backend": "healthy",
        "database": database,
        "pgvector": pgvector,
        "llm": llm,
        "n8n": n8n,
        "mock_mode": s.llm_mock_mode,
    }
