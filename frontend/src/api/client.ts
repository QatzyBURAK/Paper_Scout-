import type { Paper, PaperListResponse, IngestRequest, IngestResponse, ApiError } from "../types/paper";

const API_BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://localhost:8000";

export class ApiRequestError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!res.ok) {
    const body = (await res.json().catch(() => ({ detail: res.statusText }))) as ApiError;
    const message = Array.isArray(body.detail)
      ? body.detail[0]?.msg ?? "Validation error"
      : body.detail;
    throw new ApiRequestError(res.status, message);
  }

  return res.json() as Promise<T>;
}

export function health(): Promise<{ status: string }> {
  return request("/health");
}

export function listPapers(params: { limit?: number; offset?: number } = {}): Promise<PaperListResponse> {
  const q = new URLSearchParams();
  if (params.limit !== undefined) q.set("limit", String(params.limit));
  if (params.offset !== undefined) q.set("offset", String(params.offset));
  return request(`/papers?${q.toString()}`);
}

export function getPaper(externalId: string): Promise<Paper> {
  return request(`/papers/${encodeURIComponent(externalId)}`);
}

export function searchPapers(
  mode: "keyword" | "semantic" | "hybrid",
  q: string,
  limit = 100,
): Promise<Paper[]> {
  const params = new URLSearchParams({ q, limit: String(limit) });
  return request(`/search/${mode}?${params.toString()}`);
}

export function fetchPapers(body: IngestRequest): Promise<IngestResponse> {
  return request("/ingest", {
    method: "POST",
    body: JSON.stringify(body),
  });
}
