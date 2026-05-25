import { useState } from "react";
import { useBrowsePapers } from "../hooks/useBrowsePapers";
import { ResultsList } from "../components/ResultsList";
import { SkeletonCard } from "../components/SkeletonCard";
import { EmptyState } from "../components/EmptyState";
import { LoadMoreButton } from "../components/LoadMoreButton";
import { PaperDetailModal } from "../components/PaperDetailModal";
import type { Paper } from "../types/paper";
import styles from "./BrowsePage.module.css";

export function BrowsePage() {
  const { items, total, loading, error, hasMore, loadMore, retry } = useBrowsePapers();
  const [selected, setSelected] = useState<Paper | null>(null);

  return (
    <div className={styles.page}>
      <section className={styles.header}>
        <h1 className={styles.heading}>Tüm Makaleler</h1>
        <p className={styles.sub}>Veritabanındaki tüm makaleler — yeniden aramak için ana sayfayı kullan.</p>
      </section>

      <section aria-live="polite" aria-label="Paper list">
        {loading && items.length === 0 && (
          <div className={styles.skeletonList}>
            {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)}
          </div>
        )}
        {!loading && error && items.length === 0 && (
          <EmptyState kind="error" message={error} onRetry={retry} />
        )}
        {!loading && !error && items.length === 0 && (
          <EmptyState kind="empty" />
        )}
        {items.length > 0 && (
          <ResultsList papers={items} total={total} onSelect={setSelected} />
        )}
        <LoadMoreButton
          onClick={loadMore}
          loading={loading && items.length > 0}
          hasMore={hasMore}
          hasAny={items.length > 0}
        />
      </section>

      <PaperDetailModal paper={selected} onClose={() => setSelected(null)} />
    </div>
  );
}
