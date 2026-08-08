import { useI18n } from "../i18n/context";
import styles from "./LoadMoreButton.module.css";

interface Props {
  onClick: () => void;
  loading: boolean;
  hasMore: boolean;
  hasAny: boolean;
}

export function LoadMoreButton({ onClick, loading, hasMore, hasAny }: Props) {
  const { t } = useI18n();

  if (!hasMore && hasAny) {
    return (
      <div className={styles.wrapper}>
        <p className={styles.exhausted}>{t("loadMore.exhausted")}</p>
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
        {loading ? t("loadMore.loading") : t("loadMore.button")}
      </button>
    </div>
  );
}
