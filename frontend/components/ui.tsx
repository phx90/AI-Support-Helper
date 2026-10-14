import { ReactNode } from "react";
export function Card({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return <div className={`card ${className}`}>{children}</div>;
}
export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: string;
}) {
  return <span className={`badge ${tone}`}>{children}</span>;
}
export function Empty({ title, body }: { title: string; body: string }) {
  return (
    <div className="empty">
      <div className="empty-icon">✦</div>
      <h3>{title}</h3>
      <p>{body}</p>
    </div>
  );
}
export function ErrorBox({ message }: { message: string }) {
  return <div className="error">{message}</div>;
}
export function Loader() {
  return <div className="loader">Loading…</div>;
}
