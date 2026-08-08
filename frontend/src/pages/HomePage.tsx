import { useState } from "react";
import { usePaperSearch } from "../hooks/usePaperSearch";
import { SearchBar } from "../components/SearchBar";
import { ResultsList } from "../components/ResultsList";
import { SkeletonCard } from "../components/SkeletonCard";
import { EmptyState } from "../components/EmptyState";
import { IngestPanel } from "../components/IngestPanel";
import { PaperDetailModal } from "../components/PaperDetailModal";
import type { Paper } from "../types/paper";
import { useI18n } from "../i18n/context";
import styles from "./HomePage.module.css";

export function HomePage() {
  const { t } = useI18n();
  const { data, loading, error, search, retry } = usePaperSearch();
  const [selected, setSelected] = useState<Paper | null>(null);

  return (
    <div className={styles.page}>
      <section className={styles.searchSection}>
        <h1 className={styles.heading}>{t("home.heading")}</h1>
        <p className={styles.sub}>{t("home.sub")}</p>
        <SearchBar onSubmit={search} loading={loading} />
        <IngestPanel />
      </section>

      <section aria-live="polite" aria-label={t("home.resultsLabel")}>
        {loading && (
          <div className={styles.skeletonList}>
            {Array.from({ length: 4 }).map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        )}
        {!loading && error && (
          <EmptyState kind="error" message={error} onRetry={retry} />
        )}
        {!loading && !error && data === null && (
          <EmptyState kind="idle" />
        )}
        {!loading && !error && data !== null && data.length === 0 && (
          <EmptyState kind="empty" />
        )}
        {!loading && !error && data !== null && data.length > 0 && (
          <ResultsList papers={data} onSelect={setSelected} />
        )}
      </section>

      <PaperDetailModal paper={selected} onClose={() => setSelected(null)} />
    </div>
  );
}
