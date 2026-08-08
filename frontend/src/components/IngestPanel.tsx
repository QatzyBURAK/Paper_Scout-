import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { fetchPapers, ApiRequestError } from "../api/client";
import type { IngestResponse } from "../types/paper";
import { useI18n } from "../i18n/context";
import type { MessageKey } from "../i18n/translations";
import styles from "./IngestPanel.module.css";

type Period = "all" | "month" | "week";
type Source = "arxiv" | "semantic_scholar";

const PERIODS: { value: Period; labelKey: MessageKey }[] = [
  { value: "all", labelKey: "ingest.period.all" },
  { value: "month", labelKey: "ingest.period.month" },
  { value: "week", labelKey: "ingest.period.week" },
];

// Kaynak adları marka — her iki dilde de aynı kalıyor.
const SOURCES: { value: Source; label: string }[] = [
  { value: "arxiv", label: "arXiv" },
  { value: "semantic_scholar", label: "Semantic Scholar" },
];

export function IngestPanel() {
  const { t } = useI18n();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [period, setPeriod] = useState<Period>("all");
  const [sources, setSources] = useState<Set<Source>>(new Set(["arxiv", "semantic_scholar"]));
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<IngestResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  function toggleSource(src: Source) {
    setSources((prev) => {
      const next = new Set(prev);
      if (next.has(src)) {
        next.delete(src);
      } else {
        next.add(src);
      }
      return next;
    });
  }

  const noSourceSelected = sources.size === 0;

  async function handleFetch() {
    if (!query.trim() || loading || noSourceSelected) return;
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const sourcesParam =
        sources.size === 2 ? undefined : (Array.from(sources) as Source[]);
      const res = await fetchPapers({
        query: query.trim(),
        limit_per_source: 25,
        ...(period !== "all" ? { period } : {}),
        ...(sourcesParam ? { sources: sourcesParam } : {}),
      });
      setResult(res);
    } catch (err) {
      const isNetworkError = err instanceof TypeError && err.message === "Failed to fetch";
      setError(
        err instanceof ApiRequestError
          ? err.message
          : isNetworkError
            ? t("error.network")
            : t("error.unexpected"),
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.panel}>
      <button
        type="button"
        className={styles.toggle}
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
      >
        <span className={styles.toggleLabel}>{t("ingest.toggle")}</span>
        <span className={`${styles.chevron} ${open ? styles.chevronOpen : ""}`}>▾</span>
      </button>

      <AnimatePresence initial={false}>
      {open && (
        <motion.div
          className={styles.body}
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.2, ease: [0.25, 0.1, 0.25, 1] }}
          style={{ overflow: "hidden" }}
        >
          <div className={styles.row}>
            <input
              className={styles.input}
              type="text"
              placeholder={t("ingest.placeholder")}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") void handleFetch(); }}
            />
            <div className={styles.periodGroup} role="group" aria-label={t("ingest.periodLabel")}>
              {PERIODS.map(({ value, labelKey }) => (
                <button
                  key={value}
                  type="button"
                  className={`${styles.periodBtn} ${period === value ? styles.periodActive : ""}`}
                  aria-pressed={period === value}
                  onClick={() => setPeriod(value)}
                >
                  {t(labelKey)}
                </button>
              ))}
            </div>
            <button
              type="button"
              className={styles.fetchBtn}
              disabled={loading || query.trim().length === 0 || noSourceSelected}
              onClick={() => void handleFetch()}
            >
              {loading && <span className={styles.spinner} aria-hidden="true" />}
              {loading ? t("ingest.fetching") : t("ingest.fetch")}
            </button>
          </div>

          <div className={styles.sourceRow}>
            <div className={styles.sourceGroup} role="group" aria-label={t("ingest.sourceLabel")}>
              {SOURCES.map(({ value, label }) => {
                const active = sources.has(value);
                const activeClass =
                  value === "arxiv" ? styles.sourceActiveArxiv : styles.sourceActiveSs;
                return (
                  <button
                    key={value}
                    type="button"
                    className={`${styles.sourceBtn} ${active ? activeClass : ""}`}
                    aria-pressed={active}
                    onClick={() => toggleSource(value)}
                  >
                    {label}
                  </button>
                );
              })}
            </div>
            {noSourceSelected && (
              <span className={styles.sourceWarning}>{t("ingest.noSource")}</span>
            )}
          </div>

          {result && (
            <p className={styles.result}>
              {t("ingest.result", {
                fetched: result.fetched,
                saved: result.saved,
                merged: result.merged,
              })}
            </p>
          )}
          {error && (
            <p className={`${styles.result} ${styles.resultError}`}>{error}</p>
          )}
        </motion.div>
      )}
      </AnimatePresence>
    </div>
  );
}
