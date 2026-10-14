import time

from sqlalchemy.orm import Session

from app.agents.support_agent import support_agent
from app.core.config import get_settings
from app.core.exceptions import NotFoundError
from app.integrations.llm.providers import get_llm_provider
from app.models.entities import Conversation, Message
from app.rag.retrieval import context_from, search
from app.schemas.api import ChatRequest, ChatResponse, Source
from app.services.ticket_service import classify_incident
from app.tools.support_tools import (
    CreateTicketInput,
    create_support_ticket,
    get_system_status,
)


def chat(db: Session, data: ChatRequest) -> ChatResponse:
    started = time.perf_counter()
    s = get_settings()
    conv = db.get(Conversation, data.conversation_id) if data.conversation_id else None
    if data.conversation_id and not conv:
        raise NotFoundError("Conversation not found")
    if not conv:
        conv = Conversation(title=data.question[:80])
        db.add(conv)
        db.flush()
    db.add(Message(conversation_id=conv.id, role="user", content=data.question))
    db.flush()
    action = support_agent.invoke({"question": data.question})["action"]
    tool_calls = []
    sources = []
    if action == "create_ticket":
        classification = classify_incident(data.question)
        result = create_support_ticket(
            db,
            CreateTicketInput(
                title=classification.summary[:200],
                description=data.question,
                category=classification.category,
                priority=classification.priority,
            ),
        )
        answer = f"Chamado #{result['id']} criado com sucesso. Status: open."
        tool_calls = ["create_support_ticket"]
    elif action == "status":
        health = get_system_status(db)
        answer = "Status atual: database={database}, pgvector={pgvector}, n8n={n8n}.".format(
            **health
        )
        tool_calls = ["get_system_status"]
    else:
        found = search(db, data.question)
        threshold = min(s.min_relevance_score, 0.05) if s.llm_mock_mode else s.min_relevance_score
        accepted = [x for x in found if x.score >= threshold]
        if accepted:
            answer = get_llm_provider().generate(data.question, context_from(accepted))
            sources = [
                Source(
                    chunk_id=x.chunk_id,
                    document_id=x.document_id,
                    document=x.document,
                    page=x.page,
                    chunk_index=x.chunk_index,
                    excerpt=x.content[:500],
                    similarity_score=round(x.score, 4),
                )
                for x in accepted
            ]
            tool_calls = ["search_knowledge_base"]
        else:
            answer = "Não encontrei informação suficiente na base de conhecimento para responder com segurança."
    latency = (time.perf_counter() - started) * 1000
    assistant = Message(
        conversation_id=conv.id,
        role="assistant",
        content=answer,
        model="mock" if s.llm_mock_mode else s.llm_model,
        latency_ms=latency,
        retrieved_chunks=[x.model_dump(mode="json") for x in sources],
    )
    db.add(assistant)
    db.commit()
    db.refresh(assistant)
    return ChatResponse(
        conversation_id=conv.id,
        message_id=assistant.id,
        answer=answer,
        sources=sources,
        tool_calls=tool_calls,
        latency_ms=round(latency, 2),
        model=assistant.model or "unknown",
    )
