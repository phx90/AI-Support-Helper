import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database.base import engine
from app.main import app


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    with engine.begin() as conn:
        for table in [
            "feedback",
            "tool_executions",
            "messages",
            "conversations",
            "document_chunks",
            "documents",
            "tickets",
        ]:
            conn.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
    yield
