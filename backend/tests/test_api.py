def test_health(client):
    assert client.get("/health").status_code == 200


def test_ticket_lifecycle(client):
    body = {
        "title": "ERP unavailable",
        "description": "Unable to open ERP after login",
        "category": "erp",
        "priority": "high",
    }
    created = client.post("/api/v1/tickets", json=body)
    assert created.status_code == 201
    assert created.json()["status"] == "open"
    listed = client.get("/api/v1/tickets").json()
    assert listed["total"] == 1


def test_structured_classification_in_mock_mode(client):
    result = client.post(
        "/api/v1/classify", json={"description": "VPN network is unavailable for everyone"}
    )
    assert result.status_code == 200
    assert result.json()["category"] == "network"
    assert result.json()["priority"] == "critical"


def test_invalid_upload(client):
    result = client.post(
        "/api/v1/documents", files={"file": ("malware.exe", b"bad", "application/octet-stream")}
    )
    assert result.status_code == 422
    assert result.json()["error"]["code"] == "document_processing_error"


def test_validation(client):
    assert client.post("/api/v1/tickets", json={}).status_code == 422


def test_chat_persists_no_context_response(client):
    result = client.post("/api/v1/chat", json={"question": "What is the secret launch code?"})
    assert result.status_code == 200
    body = result.json()
    assert "Não encontrei" in body["answer"]
    history = client.get(f"/api/v1/conversations/{body['conversation_id']}").json()
    assert len(history["messages"]) == 2


def test_agent_creates_ticket(client):
    result = client.post(
        "/api/v1/chat", json={"question": "Abra um chamado porque meu computador não acessa o ERP"}
    )
    assert result.status_code == 200
    assert "create_support_ticket" in result.json()["tool_calls"]
    assert client.get("/api/v1/tickets").json()["total"] == 1


def test_document_ingestion_and_retrieval(client):
    content = b"DNS resolution failures require checking the configured DNS resolver and cache."
    uploaded = client.post(
        "/api/v1/documents", files={"file": ("dns_runbook.md", content, "text/markdown")}
    )
    assert uploaded.status_code == 202
    document_id = uploaded.json()["id"]
    detail = client.get(f"/api/v1/documents/{document_id}").json()
    assert detail["status"] == "indexed"
    result = client.post(
        "/api/v1/chat", json={"question": "How do I check a DNS resolution failure?"}
    )
    assert result.status_code == 200
    assert result.json()["sources"][0]["document"] == "dns_runbook.md"


def test_agent_reports_system_status(client):
    result = client.post("/api/v1/chat", json={"question": "What is the system status?"})
    assert result.status_code == 200
    assert result.json()["tool_calls"] == ["get_system_status"]
    assert "database=healthy" in result.json()["answer"]
