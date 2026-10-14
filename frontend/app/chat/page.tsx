"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { api, Page, Source } from "@/lib/api";
import { Card, Empty, ErrorBox } from "@/components/ui";

type Msg = {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  tools?: string[];
  messageId?: string;
};
type ChatResponse = {
  conversation_id: string;
  message_id: string;
  answer: string;
  sources: Source[];
  tool_calls: string[];
  latency_ms: number;
};
type ConversationSummary = { id: string; title: string; updated_at: string };
type StoredMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  retrieved_chunks: Source[];
};
type ConversationDetail = ConversationSummary & { messages: StoredMessage[] };

export default function Chat() {
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [q, setQ] = useState("");
  const [cid, setCid] = useState<string>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const loadList = useCallback(
    () =>
      api<Page<ConversationSummary>>("/conversations")
        .then((x) => setConversations(x.items))
        .catch(() => undefined),
    [],
  );
  useEffect(() => {
    void loadList();
  }, [loadList]);

  async function openConversation(id: string) {
    setError("");
    try {
      const item = await api<ConversationDetail>(`/conversations/${id}`);
      setCid(id);
      setMsgs(
        item.messages.map((m) => ({
          role: m.role,
          content: m.content,
          sources: m.retrieved_chunks,
          messageId: m.role === "assistant" ? m.id : undefined,
        })),
      );
    } catch (x) {
      setError((x as Error).message);
    }
  }
  async function send(e: FormEvent) {
    e.preventDefault();
    if (!q.trim()) return;
    const question = q;
    setMsgs((x) => [...x, { role: "user", content: question }]);
    setQ("");
    setLoading(true);
    setError("");
    try {
      const result = await api<ChatResponse>("/chat", {
        method: "POST",
        body: JSON.stringify({ question, conversation_id: cid }),
      });
      setCid(result.conversation_id);
      setMsgs((x) => [
        ...x,
        {
          role: "assistant",
          content: result.answer,
          sources: result.sources,
          tools: result.tool_calls,
          messageId: result.message_id,
        },
      ]);
      await loadList();
    } catch (x) {
      setError((x as Error).message);
    } finally {
      setLoading(false);
    }
  }
  async function rate(id: string, rating: number) {
    await api("/feedback", {
      method: "POST",
      body: JSON.stringify({ message_id: id, rating }),
    });
  }
  async function rename(item: ConversationSummary) {
    const title = window.prompt("Conversation title", item.title);
    if (!title?.trim()) return;
    await api(`/conversations/${item.id}`, {
      method: "PATCH",
      body: JSON.stringify({ title }),
    });
    await loadList();
  }
  async function remove(id: string) {
    if (!window.confirm("Delete this conversation?")) return;
    await api(`/conversations/${id}`, { method: "DELETE" });
    if (cid === id) {
      setCid(undefined);
      setMsgs([]);
    }
    await loadList();
  }
  function fresh() {
    setMsgs([]);
    setCid(undefined);
    setError("");
  }

  return (
    <div className="chat-layout">
      <Card className="conversation-list">
        <div className="row">
          <b>Conversations</b>
          <button onClick={fresh}>+</button>
        </div>
        {conversations.length ? (
          conversations.map((item) => (
            <div className="status-row" key={item.id}>
              <button
                className="secondary"
                style={{ width: "100%", textAlign: "left" }}
                onClick={() => openConversation(item.id)}
              >
                {item.title}
              </button>
              <div style={{ marginTop: 7 }}>
                <button className="secondary" onClick={() => rename(item)}>
                  Rename
                </button>{" "}
                <button className="danger" onClick={() => remove(item.id)}>
                  Delete
                </button>
              </div>
            </div>
          ))
        ) : (
          <p className="muted">No saved conversations.</p>
        )}
      </Card>
      <Card className="chat-panel">
        <div className="messages">
          {!msgs.length && (
            <Empty
              title="Ask your knowledge base"
              body="Get grounded answers, exact sources, or ask the agent to create a support ticket."
            />
          )}
          {msgs.map((m, i) => (
            <div
              className={`message ${m.role}`}
              key={`${m.messageId || i}-${i}`}
            >
              <b>{m.role === "user" ? "You" : "AI Support"}</b>
              <div>{m.content}</div>
              {m.tools?.map((t) => (
                <span className="badge" key={t}>
                  Tool: {t}
                </span>
              ))}
              {m.sources && m.sources.length > 0 && (
                <div className="sources">
                  <b>Sources</b>
                  {m.sources.map((s) => (
                    <details className="source" key={s.chunk_id}>
                      <summary>
                        {s.document}
                        {s.page ? ` — page ${s.page}` : ""} ·{" "}
                        {(s.similarity_score * 100).toFixed(0)}%
                      </summary>
                      <p>{s.excerpt}</p>
                    </details>
                  ))}
                </div>
              )}
              {m.messageId && (
                <div style={{ marginTop: 10 }}>
                  <button
                    className="secondary"
                    onClick={() => rate(m.messageId!, 1)}
                  >
                    👍
                  </button>{" "}
                  <button
                    className="secondary"
                    onClick={() => rate(m.messageId!, -1)}
                  >
                    👎
                  </button>
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="message assistant">
              Searching knowledge base and reasoning…
            </div>
          )}
          {error && <ErrorBox message={error} />}
        </div>
        <form className="composer" onSubmit={send}>
          <textarea
            rows={2}
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Ask a technical question or request a support ticket…"
          />
          <button disabled={loading}>Send</button>
        </form>
      </Card>
    </div>
  );
}
