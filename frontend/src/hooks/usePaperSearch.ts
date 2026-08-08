import { useState, useCallback } from "react";
import { searchPapers, ApiRequestError } from "../api/client";
import type { Paper, SearchMode } from "../types/paper";
import { useI18n } from "../i18n/context";

interface SearchState {
  data: Paper[] | null;
  loading: boolean;
  error: string | null;
}

interface LastQuery {
  q: string;
  mode: SearchMode;
}

export function usePaperSearch() {
  const { t } = useI18n();
  const [state, setState] = useState<SearchState>({
    data: null,
    loading: false,
    error: null,
  });
  const [lastQuery, setLastQuery] = useState<LastQuery | null>(null);

  const run = useCallback(async (q: string, mode: SearchMode) => {
    if (q.trim().length === 0) {
      setState({ data: null, loading: false, error: null });
      setLastQuery(null);
      return;
    }

    setState({ data: null, loading: true, error: null });
    setLastQuery({ q, mode });

    try {
      const data = await searchPapers(mode, q.trim(), 100);
      setState({ data, loading: false, error: null });
    } catch (err) {
      const isNetworkError = err instanceof TypeError && err.message === "Failed to fetch";
      const message =
        err instanceof ApiRequestError
          ? err.message
          : isNetworkError
            ? t("error.networkSearch")
            : t("error.unexpected");
      setState({ data: null, loading: false, error: message });
    }
  }, [t]);

  const search = useCallback(
    (q: string, mode: SearchMode) => { void run(q, mode); },
    [run],
  );

  const retry = useCallback(() => {
    if (lastQuery) { void run(lastQuery.q, lastQuery.mode); }
  }, [lastQuery, run]);

  return { ...state, search, retry };
}
