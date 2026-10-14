# n8n Workflows

Start Compose, open `http://localhost:5678`, complete local owner setup, then use **Import from File** for each JSON file under `n8n/workflows/`. Review node URLs, save and activate.

`SUPPORT TICKET AUTOMATION` receives a description, calls `/classify`, persists the ticket through the backend, then writes a simulated notification to execution logs. `KNOWLEDGE INGESTION NOTIFICATION` accepts the completion payload emitted after indexing and logs it. Backend outbound calls use a short timeout and three exponential-backoff attempts; ingestion still succeeds if automation is unavailable.

For production, protect webhook paths with authentication or signatures and replace the simulation with an approved email/chat connector.