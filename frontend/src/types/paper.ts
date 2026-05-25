export interface Paper {
  external_id: string;
  source: "arxiv" | "semantic_scholar";
  title: string;
  abstract: string;
  authors: string[];
  published_date: string | null;
  citation_count: number;
  url: string;
}

export type SearchMode = "keyword" | "semantic" | "hybrid";

export interface IngestRequest {
  query: string;
  limit_per_source: number;
  period?: "week" | "month";
  sources?: ("arxiv" | "semantic_scholar")[];
}

export interface IngestResponse {
  fetched: number;
  saved: number;
  merged: number;
}

export interface PaperListResponse {
  items: Paper[];
  total: number;
  limit: number;
  offset: number;
}

export interface ApiError {
  detail: string | ValidationError[];
}

export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}
