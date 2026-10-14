"use client";
import { useEffect, useState } from "react";
import {
  BookOpen,
  MessageSquare,
  MessagesSquare,
  ThumbsUp,
  Layers,
} from "lucide-react";
import { api } from "@/lib/api";
import { Card, ErrorBox, Loader } from "@/components/ui";
type Data = {
  documents: number;
  chunks: number;
  conversations: number;
  questions: number;
  positive_feedback_percentage: number;
  recent_queries: {
    question: string;
    created_at: string;
    latency_ms: number;
  }[];
};
export default function Dashboard() {
  const [d, setD] = useState<Data>();
  const [e, setE] = useState("");
  useEffect(() => {
    api<Data>("/dashboard")
      .then(setD)
      .catch((x) => setE(x.message));
  }, []);
  if (e) return <ErrorBox message={e} />;
  if (!d) return <Loader />;
  const metrics = [
    ["Documents", d.documents, BookOpen],
    ["Indexed chunks", d.chunks, Layers],
    ["Conversations", d.conversations, MessagesSquare],
    ["Questions", d.questions, MessageSquare],
    ["Positive feedback", `${d.positive_feedback_percentage}%`, ThumbsUp],
  ] as const;
  return (
    <div className="grid" style={{ gap: 22 }}>
      <div>
        <h2 style={{ marginBottom: 6 }}>Support intelligence at a glance</h2>
        <span className="muted">
          Live usage, knowledge and quality signals.
        </span>
      </div>
      <div className="grid stats">
        {metrics.map(([l, v, I]) => (
          <Card key={l}>
            <div className="metric">
              <div>
                <span>{l}</span>
                <strong>{v}</strong>
              </div>
              <div className="metric-icon">
                <I size={19} />
              </div>
            </div>
          </Card>
        ))}
      </div>
      <Card>
        <h3 className="section-title">Recent queries</h3>
        {d.recent_queries.length ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Question</th>
                  <th>Latency</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {d.recent_queries.map((q, i) => (
                  <tr key={i}>
                    <td>{q.question}</td>
                    <td>
                      {q.latency_ms ? `${q.latency_ms.toFixed(0)} ms` : "—"}
                    </td>
                    <td className="muted">
                      {new Date(q.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="muted">
            No questions yet. Start a conversation to see activity here.
          </p>
        )}
      </Card>
    </div>
  );
}
