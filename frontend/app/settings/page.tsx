import { Card } from "@/components/ui";
export default function Settings() {
  return (
    <div className="split">
      <Card>
        <h3>Runtime configuration</h3>
        <p className="muted">
          Provider, model, chunking and relevance settings are controlled
          server-side through environment variables so API keys never reach the
          browser.
        </p>
        <div className="status-row">
          <b>LLM provider</b>
          <p className="muted">LLM_PROVIDER=openai | anthropic</p>
        </div>
        <div className="status-row">
          <b>Chunking</b>
          <p className="muted">CHUNK_SIZE and CHUNK_OVERLAP</p>
        </div>
        <div className="status-row">
          <b>Retrieval guardrail</b>
          <p className="muted">MIN_RELEVANCE_SCORE</p>
        </div>
      </Card>
      <Card>
        <h3>Safe by design</h3>
        <p>
          Secrets remain in backend environment variables. Retrieved documents
          are wrapped as untrusted data and cannot override system instructions.
        </p>
        <span className="badge healthy">Mock mode available</span>
      </Card>
    </div>
  );
}
