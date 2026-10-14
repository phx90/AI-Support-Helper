import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.integrations.llm.providers import get_llm_provider
from app.models.entities import Ticket
from app.schemas.api import ClassificationResult, TicketCreate


def create_ticket(db: Session, data: TicketCreate) -> Ticket:
    ticket = Ticket(**data.model_dump())
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_ticket(db: Session, ticket_id: uuid.UUID) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise NotFoundError("Ticket not found")
    return ticket


def recent_tickets(db: Session, limit: int = 10) -> list[Ticket]:
    return list(db.scalars(select(Ticket).order_by(Ticket.created_at.desc()).limit(limit)))


def classify_incident(description: str) -> ClassificationResult:
    return get_llm_provider().structured(description, ClassificationResult)
