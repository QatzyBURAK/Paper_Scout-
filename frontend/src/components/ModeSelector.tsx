import type { SearchMode } from "../types/paper";
import { useI18n } from "../i18n/context";
import styles from "./ModeSelector.module.css";

// Mod adları teknik terim — her iki dilde de İngilizce kalıyor.
const MODES: { value: SearchMode; label: string }[] = [
  { value: "keyword", label: "Keyword" },
  { value: "semantic", label: "Semantic" },
  { value: "hybrid", label: "Hybrid" },
];

interface Props {
  value: SearchMode;
  onChange: (mode: SearchMode) => void;
}

export function ModeSelector({ value, onChange }: Props) {
  const { t } = useI18n();

  return (
    <div className={styles.group} role="group" aria-label={t("mode.groupLabel")}>
      {MODES.map(({ value: mode, label }) => (
        <button
          key={mode}
          type="button"
          className={`${styles.btn} ${value === mode ? styles.active : ""}`}
          aria-pressed={value === mode}
          onClick={() => onChange(mode)}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
