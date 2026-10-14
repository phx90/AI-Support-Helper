import time
import uuid

import httpx
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.entities import ToolExecution
from app.rag.retrieval import search
from app.schemas.api import TicketCreate
from app.services.ticket_service import create_ticket, get_ticket, recent_tickets


class SearchKnowledgeInput(BaseModel):
    query: str = Field(min_length=2)
    limit: int = Field(5, ge=1, le=10)


class CreateTicketInput(TicketCreate):
    """Validated support-ticket tool arguments."""


class SystemStatusInput(BaseModel):
    """No arguments are required for the system status tool."""


class TicketIdInput(BaseModel):
    ticket_id: uuid.UUID


class RecentTicketsInput(BaseModel):
    limit: int = Field(5, ge=1, le=20)


def record(db: Session, name: str, args: dict, result: dict, start: float, success: bool = True):
    db.add(
        ToolExecution(
            tool_name=name,
            arguments=args,
            result=result,
            success=success,
            duration_ms=(time.perf_counter() - start) * 1000,
        )
    )
    db.commit()


def search_knowledge_base(db: Session, args: SearchKnowledgeInput) -> dict:
    start = time.perf_counter()
    result = {
        "results": [
            {"document": x.document, "page": x.page, "content": x.content, "score": x.score}
            for x in search(db, args.query, args.limit)
        ]
    }
    record(db, "search_knowledge_base", args.model_dump(), result, start)
    return result


def create_support_ticket(db: Session, args: CreateTicketInput) -> dict:
    start = time.perf_counter()
    t = create_ticket(db, TicketCreate(**args.model_dump()))
    result = {"id": str(t.id), "status": t.status.value}
    record(db, "create_support_ticket", args.model_dump(mode="json"), result, start)
    return result


def get_ticket_tool(db: Session, args: TicketIdInput) -> dict:
    start = time.perf_counter()
    t = get_ticket(db, args.ticket_id)
    result = {"id": str(t.id), "title": t.title, "status": t.status.value}
    record(db, "get_ticket", args.model_dump(mode="json"), result, start)
    return result


def list_recent_tickets(db: Session, args: RecentTicketsInput) -> dict:
    start = time.perf_counter()
    result = {
        "tickets": [
            {"id": str(t.id), "title": t.title, "status": t.status.value}
            for t in recent_tickets(db, args.limit)
        ]
    }
    record(db, "list_recent_tickets", args.model_dump(), result, start)
    return result


def get_system_status(db: Session, args: SystemStatusInput | None = None) -> dict:
    start = time.perf_counter()
    settings = get_settings()
    result = {"database": "healthy", "pgvector": "healthy", "n8n": "unavailable"}
    try:
        db.execute(text("SELECT 1"))
        db.execute(text("SELECT extversion FROM pg_extension WHERE extname='vector'"))
    except Exception:
        result["database"] = "unavailable"
        result["pgvector"] = "unavailable"
    try:
        httpx.get(f"{settings.n8n_base_url}/healthz", timeout=1).raise_for_status()
        result["n8n"] = "healthy"
    except Exception:
        result["n8n"] = "unavailable"
    record(db, "get_system_status", {}, result, start)
    return result
