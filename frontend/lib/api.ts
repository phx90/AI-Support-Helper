export const API =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, {
    ...init,
    headers: {
      ...(init?.body instanceof FormData
        ? {}
        : { "Content-Type": "application/json" }),
      ...init?.headers,
    },
    cache: "no-store",
  });
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      message = body.error?.message || body.detail || message;
    } catch {
      /* Non-JSON error response; retain the HTTP fallback. */
    }
    throw new Error(message);
  }
  return response.status === 204 ? (undefined as T) : response.json();
}
export type Page<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
};
export type DocumentItem = {
  id: string;
  name: string;
  file_type: string;
  size: number;
  status: "uploaded" | "processing" | "indexed" | "error";
  chunk_count: number;
  created_at: string;
  error_message?: string;
};
export type Ticket = {
  id: string;
  title: string;
  description: string;
  category: string;
  priority: string;
  status: string;
  created_at: string;
};
export type Source = {
  chunk_id: string;
  document: string;
  page: number | null;
  excerpt: string;
  similarity_score: number;
};
