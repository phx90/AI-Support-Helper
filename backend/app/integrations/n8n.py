import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.logging import logger


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=4), reraise=True)
def notify_document_indexed(payload: dict) -> None:
    try:
        with httpx.Client(timeout=3) as client:
            client.post(get_settings().n8n_webhook_url, json=payload).raise_for_status()
    except Exception as exc:
        logger.warning("n8n_notification_failed", error=str(exc))
        raise
