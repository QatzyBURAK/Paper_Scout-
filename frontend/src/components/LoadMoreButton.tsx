import styles from "./LoadMoreButton.module.css";

interface Props {
  onClick: () => void;
  loading: boolean;
  hasMore: boolean;
  hasAny: boolean;
}

export function LoadMoreButton({ onClick, loading, hasMore, hasAny }: Props) {
  if (!hasMore && hasAny) {
    return (
      <div className={styles.wrapper}>
        <p className={styles.exhausted}>— TÜM SONUÇLAR GÖSTERİLDİ —</p>
      </div>
    );
  }

  if (!hasMore) return null;

  return (
    <div className={styles.wrapper}>
      <button
        type="button"
        className={styles.btn}
        onClick={onClick}
        disabled={loading}
      >
        {loading && <span className={styles.spinner} aria-hidden="true" />}
        {loading ? "Yükleniyor…" : "Daha fazla yükle"}
      </button>
    </div>
  );
}
