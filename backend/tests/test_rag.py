from app.integrations.llm.providers import MockLLMProvider
from app.rag.chunking import TechnicalTextChunker
from app.rag.embeddings import MockEmbeddingProvider
from app.schemas.api import ClassificationResult
from app.services.document_service import extract_pages, safe_filename


def test_chunking_preserves_page_and_overlap():
    chunks = TechnicalTextChunker(200, 20).split(
        [(7, "Network guide. " + "diagnostic steps. " * 30)]
    )
    assert len(chunks) > 1
    assert all(x.page == 7 for x in chunks)
    assert [x.chunk_index for x in chunks] == list(range(len(chunks)))


def test_text_parsing_and_filename_safety():
    assert extract_pages(b"hello", ".txt") == [(None, "hello")]
    assert safe_filename("../../evil.md") == "evil.md"


def test_mock_embedding_is_deterministic():
    p = MockEmbeddingProvider(32)
    assert p.embed(["vpn issue"])[0] == p.embed(["vpn issue"])[0]
    assert len(p.embed(["x"])[0]) == 32


def test_mock_provider_and_structured_output():
    p = MockLLMProvider()
    assert "Não encontrei" in p.generate("q", "")
    result = p.structured("urgent VPN network outage", ClassificationResult)
    assert result.category.value == "network"
