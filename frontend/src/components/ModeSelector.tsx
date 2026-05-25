import type { SearchMode } from "../types/paper";
import styles from "./ModeSelector.module.css";

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
  return (
    <div className={styles.group} role="group" aria-label="Search mode">
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
