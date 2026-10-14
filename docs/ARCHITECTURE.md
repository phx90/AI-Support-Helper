# Architecture

The system uses a layered modular monolith for the API and separate deployable UI, database and automation services. Routes validate HTTP contracts and delegate; services own use cases; repositories provide common query behavior; SQLAlchemy models own persistence shape. RAG, agents, tools and vendor integrations are separate modules because they evolve and fail differently.

A document transitions through `uploaded → processing → indexed` or `error`. File bytes use a generated UUID path while searchable metadata stays in PostgreSQL. A conversation stores user and assistant messages plus model, latency and the exact retrieved chunks. Tool executions form an audit trail.

Compose service health checks create deterministic startup ordering. Alembic owns schema evolution and enables pgvector before defining its column. Mock mode preserves the same interfaces as network providers, making local behavior representative without claiming equivalent model quality.