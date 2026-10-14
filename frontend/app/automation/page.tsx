import { Card } from "@/components/ui";
export default function Automation() {
  return (
    <div className="grid">
      <Card>
        <h3>Support Ticket Automation</h3>
        <p className="muted">
          Webhook → FastAPI classification → persistence → simulated
          notification.
        </p>
        <span className="badge healthy">Workflow template included</span>
      </Card>
      <Card>
        <h3>Knowledge Ingestion Notification</h3>
        <p className="muted">
          The backend calls n8n after document indexing; failures are retried
          and do not corrupt ingestion.
        </p>
        <a className="button" href="http://localhost:5678" target="_blank">
          Open n8n
        </a>
      </Card>
    </div>
  );
}
