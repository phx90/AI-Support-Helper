"use client";
import { FormEvent, useState } from "react";
import { api } from "@/lib/api";
import { Badge, Card, ErrorBox } from "@/components/ui";
type Result = {
  category: string;
  priority: string;
  summary: string;
  suggested_action: string;
};
export default function Classifier() {
  const [result, setResult] = useState<Result>(),
    [loading, setLoading] = useState(false),
    [error, setError] = useState("");
  async function run(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError("");
    const description = new FormData(e.currentTarget).get("description");
    try {
      setResult(
        await api("/classify", {
          method: "POST",
          body: JSON.stringify({ description }),
        }),
      );
    } catch (x) {
      setError((x as Error).message);
    } finally {
      setLoading(false);
    }
  }
  return (
    <div className="split">
      <Card>
        <h3>Classify an incident</h3>
        <p className="muted">
          Structured AI output is validated by Pydantic before it reaches the
          UI.
        </p>
        <form className="grid" onSubmit={run}>
          <textarea
            name="description"
            rows={9}
            minLength={5}
            required
            placeholder="Describe the issue, impact and urgency…"
          />
          <button disabled={loading}>
            {loading ? "Classifying…" : "Classify with AI"}
          </button>
          {error && <ErrorBox message={error} />}
        </form>
      </Card>
      <Card>
        <h3>Classification result</h3>
        {result ? (
          <div className="grid">
            <div>
              <label>Category</label>
              <Badge>{result.category}</Badge>
            </div>
            <div>
              <label>Priority</label>
              <Badge tone={result.priority}>{result.priority}</Badge>
            </div>
            <div>
              <label>Summary</label>
              <p>{result.summary}</p>
            </div>
            <div>
              <label>Suggested action</label>
              <p>{result.suggested_action}</p>
            </div>
          </div>
        ) : (
          <p className="muted">The validated result will appear here.</p>
        )}
      </Card>
    </div>
  );
}
