import styles from "./EmptyState.module.css";

interface Props {
  kind: "idle" | "empty" | "error";
  message?: string;
  onRetry?: () => void;
}

const DEFAULTS: Record<Props["kind"], string> = {
  idle: "Bir konu ara — örn. \"transformer attention\" ya da \"graph neural networks\".",
  empty: "Sonuç bulunamadı. Farklı bir sorgu ya da arama modu dene.",
  error: "Arama başarısız oldu.",
};

function StateIcon({ kind }: { kind: Props["kind"] }) {
  if (kind === "idle") {
    return (
      <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <circle cx="11" cy="11" r="8"/>
        <path d="m21 21-4.35-4.35"/>
      </svg>
    );
  }
  if (kind === "empty") {
    return (
      <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <circle cx="11" cy="11" r="8"/>
        <path d="m21 21-4.35-4.35"/>
        <line x1="8" y1="11" x2="14" y2="11"/>
      </svg>
    );
  }
  return (
    <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
      <line x1="12" y1="9" x2="12" y2="13"/>
      <line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>
  );
}

export function EmptyState({ kind, message, onRetry }: Props) {
  const text = message ?? DEFAULTS[kind];
  const kindClass = styles[kind] as string;
  return (
    <div className={styles.wrapper}>
      <span className={`${styles.icon} ${kindClass}`}>
        <StateIcon kind={kind} />
      </span>
      <p className={`${styles.message} ${kindClass}`}>{text}</p>
      {kind === "error" && onRetry && (
        <button type="button" className={styles.retryBtn} onClick={onRetry}>
          Tekrar dene
        </button>
      )}
    </div>
  );
}
