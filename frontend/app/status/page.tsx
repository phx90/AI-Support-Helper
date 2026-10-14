"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Badge, Card, ErrorBox, Loader } from "@/components/ui";
type Status = Record<string, string | boolean>;
export default function StatusPage() {
  const [data, setData] = useState<Status>(),
    [error, setError] = useState("");
  useEffect(() => {
    api<Status>("/status")
      .then(setData)
      .catch((x) => setError(x.message));
  }, []);
  if (error) return <ErrorBox message={error} />;
  if (!data) return <Loader />;
  return (
    <Card>
      <h3>Service health</h3>
      <p className="muted">Live checks from the backend network.</p>
      {Object.entries(data).map(([k, v]) => (
        <div className="row status-row" key={k}>
          <span style={{ textTransform: "capitalize" }}>
            {k.replace("_", " ")}
          </span>
          {typeof v === "boolean" ? (
            <Badge>{v ? "Enabled" : "Disabled"}</Badge>
          ) : (
            <Badge tone={v}>{v}</Badge>
          )}
        </div>
      ))}
    </Card>
  );
}
