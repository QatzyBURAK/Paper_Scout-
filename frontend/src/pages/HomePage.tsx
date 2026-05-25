import { useState } from "react";
import { usePaperSearch } from "../hooks/usePaperSearch";
import { SearchBar } from "../components/SearchBar";
import { ResultsList } from "../components/ResultsList";
import { SkeletonCard } from "../components/SkeletonCard";
import { EmptyState } from "../components/EmptyState";
import { IngestPanel } from "../components/IngestPanel";
import { PaperDetailModal } from "../components/PaperDetailModal";
import type { Paper } from "../types/paper";
import styles from "./HomePage.module.css";

export function HomePage() {
  const { data, loading, error, search, retry } = usePaperSearch();
  const [selected, setSelected] = useState<Paper | null>(null);

  return (
    <div className={styles.page}>
      <section className={styles.searchSection}>
        <h1 className={styles.heading}>Araştırma Makalesi Keşfi</h1>
        <p className={styles.sub}>
          arXiv ve Semantic Scholar'dan keyword, semantic ve hybrid arama ile makale bul.
        </p>
        <SearchBar onSubmit={search} loading={loading} />
        <IngestPanel />
      </section>

      <section aria-live="polite" aria-label="Search results">
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
