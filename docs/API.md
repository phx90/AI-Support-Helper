# API

The API is versioned under `/api/v1`; OpenAPI is at `/docs`. Resources include documents, chat, conversations, tickets, classification, feedback, dashboard and status. List responses use `{items,total,page,page_size}`. Domain failures use `{error:{code,message}}`; FastAPI validation uses HTTP 422.

Upload returns 202 because indexing continues in the background. Chat accepts an optional conversation UUID; omitting it creates a titled conversation. Feedback is an upsert per assistant message. `GET /health` is the container liveness/dependency endpoint, while `/api/v1/status` returns component detail.