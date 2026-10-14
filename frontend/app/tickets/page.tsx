"use client";
import { FormEvent, useCallback, useEffect, useState } from "react";
import { api, Page, Ticket } from "@/lib/api";
import { Badge, Card, Empty, ErrorBox, Loader } from "@/components/ui";
export default function Tickets() {
  const [items, setItems] = useState<Ticket[]>([]),
    [loading, setLoading] = useState(true),
    [error, setError] = useState("");
  const load = useCallback(
    () =>
      api<Page<Ticket>>("/tickets")
        .then((x) => setItems(x.items))
        .catch((x) => setError(x.message))
        .finally(() => setLoading(false)),
    [],
  );
  useEffect(() => {
    load();
  }, [load]);
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    try {
      await api("/tickets", {
        method: "POST",
        body: JSON.stringify(Object.fromEntries(form)),
      });
      e.currentTarget.reset();
      load();
    } catch (x) {
      setError((x as Error).message);
    }
  }
  return (
    <div className="split">
      <Card>
        <h3>Create support ticket</h3>
        <form className="grid" onSubmit={submit}>
          <div>
            <label>Title</label>
            <input name="title" required minLength={3} />
          </div>
          <div>
            <label>Description</label>
            <textarea name="description" rows={5} required minLength={5} />
          </div>
          <div className="form-grid">
            <div>
              <label>Category</label>
              <select name="category">
                <option>software</option>
                <option>hardware</option>
                <option>network</option>
                <option>access</option>
                <option>erp</option>
                <option>other</option>
              </select>
            </div>
            <div>
              <label>Priority</label>
              <select name="priority">
                <option>medium</option>
                <option>low</option>
                <option>high</option>
                <option>critical</option>
              </select>
            </div>
          </div>
          <button>Create ticket</button>
          {error && <ErrorBox message={error} />}
        </form>
      </Card>
      <Card>
        <h3>Recent tickets</h3>
        {loading ? (
          <Loader />
        ) : items.length ? (
          <div>
            {items.map((t) => (
              <div className="status-row" key={t.id}>
                <div className="row">
                  <b>{t.title}</b>
                  <Badge tone={t.status}>{t.status}</Badge>
                </div>
                <p className="muted">
                  {t.category} · {t.priority} · #{t.id.slice(0, 8)}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <Empty
            title="No tickets yet"
            body="Create one here or ask the AI agent in natural language."
          />
        )}
      </Card>
    </div>
  );
}
