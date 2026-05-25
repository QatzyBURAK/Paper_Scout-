import { useState, useEffect, useCallback, useRef } from "react";
import { listPapers, ApiRequestError } from "../api/client";
import type { Paper } from "../types/paper";

const PAGE_SIZE = 20;

interface State {
  items: Paper[];
  total: number | null;
  loading: boolean;
  error: string | null;
  hasMore: boolean;
}

export function useBrowsePapers() {
  const [state, setState] = useState<State>({
    items: [],
    total: null,
    loading: true,
    error: null,
    hasMore: false,
  });
  const offsetRef = useRef(0);
  const fetchingRef = useRef(false);
  const didInitRef = useRef(false);

  const load = useCallback(async (reset: boolean) => {
    if (fetchingRef.current) return;
    fetchingRef.current = true;

    if (reset) {
      setState((s) => ({ ...s, loading: true, error: null }));
      offsetRef.current = 0;
    } else {
      setState((s) => ({ ...s, loading: true }));
    }

    try {
      const response = await listPapers({ limit: PAGE_SIZE, offset: offsetRef.current });
      const items = response.items ?? [];
      const total = response.total ?? 0;
      offsetRef.current += items.length;

      setState((s) => ({
        items: reset ? items : [...s.items, ...items],
        total,
        loading: false,
        error: null,
        hasMore: items.length === PAGE_SIZE,
      }));
    } catch (err) {
      const isNetwork = err instanceof TypeError && err.message === "Failed to fetch";
      setState((s) => ({
        ...s,
        loading: false,
        error:
          err instanceof ApiRequestError
            ? err.message
            : isNetwork
              ? "Sunucuya bağlanılamadı."
              : "Beklenmeyen bir hata oluştu.",
      }));
    } finally {
      fetchingRef.current = false;
    }
  }, []);

  useEffect(() => {
    if (didInitRef.current) return;
    didInitRef.current = true;
    void load(true);
  }, [load]);

  const loadMore = useCallback(() => void load(false), [load]);
  const retry = useCallback(() => void load(true), [load]);

  return { ...state, loadMore, retry };
}
