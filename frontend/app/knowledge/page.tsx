"use client";
import { ChangeEvent, useCallback, useEffect, useState } from "react";
import { api, DocumentItem, Page } from "@/lib/api";
import { Badge, Card, Empty, ErrorBox, Loader } from "@/components/ui";
export default function Knowledge() {
  const [docs, setDocs] = useState<DocumentItem[]>([]),
    [loading, setLoading] = useState(true),
    [error, setError] = useState(""),
    [status, setStatus] = useState("");
  const load = useCallback(() => {
    setLoading(true);
    api<Page<DocumentItem>>(`/documents${status ? `?status=${status}` : ""}`)
      .then((x) => setDocs(x.items))
      .catch((x) => setError(x.message))
      .finally(() => setLoading(false));
  }, [status]);
  useEffect(load, [load]);
  async function upload(e: ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    const body = new FormData();
    body.append("file", f);
    setError("");
    try {
      await api("/documents", { method: "POST", body });
      load();
    } catch (x) {
      setError((x as Error).message);
    }
  }
  async function remove(id: string) {
    if (!confirm("Delete this document and all vector chunks?")) return;
    await api(`/documents/${id}`, { method: "DELETE" });
    load();
  }
  async function reprocess(id: string) {
    await api(`/documents/${id}/reprocess`, { method: "POST" });
    load();
  }
  return (
    <div className="grid" style={{ gap: 20 }}>
      <div className="row">
        <div>
          <h2>Knowledge Base</h2>
          <p className="muted">
            Upload technical material and turn it into searchable evidence.
          </p>
        </div>
        <select
          style={{ width: 160 }}
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        >
          <option value="">All statuses</option>
          <option value="indexed">Indexed</option>
          <option value="processing">Processing</option>
          <option value="error">Error</option>
        </select>
      </div>
      <Card>
        <label className="dropzone">
          Drop a file here or click to browse
          <input
            hidden
            type="file"
            accept=".pdf,.txt,.md,.docx"
            onChange={upload}
          />
          <p className="muted">PDF, TXT, Markdown or DOCX · maximum 15 MB</p>
        </label>
      </Card>
      {error && <ErrorBox message={error} />}
      <Card>
        {loading ? (
          <Loader />
        ) : docs.length ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Document</th>
                  <th>Type</th>
                  <th>Size</th>
                  <th>Chunks</th>
                  <th>Status</th>
                  <th>Uploaded</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {docs.map((d) => (
                  <tr key={d.id}>
                    <td>
                      <b>{d.name}</b>
                      {d.error_message && (
                        <div className="muted">{d.error_message}</div>
                      )}
                    </td>
                    <td>{d.file_type.toUpperCase()}</td>
                    <td>{(d.size / 1024).toFixed(1)} KB</td>
                    <td>{d.chunk_count}</td>
                    <td>
                      <Badge tone={d.status}>{d.status}</Badge>
                    </td>
                    <td>{new Date(d.created_at).toLocaleDateString()}</td>
                    <td>
                      <button
                        className="secondary"
                        onClick={() => reprocess(d.id)}
                      >
                        Reprocess
                      </button>{" "}
                      <button className="danger" onClick={() => remove(d.id)}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <Empty
            title="No documents indexed yet"
            body="Upload your first document to start using RAG."
          />
        )}
      </Card>
    </div>
  );
}
