import { useState, type FormEvent, type KeyboardEvent } from "react";
import type { SearchMode } from "../types/paper";
import { ModeSelector } from "./ModeSelector";
import styles from "./SearchBar.module.css";

interface Props {
  onSubmit: (q: string, mode: SearchMode) => void;
  loading: boolean;
}

export function SearchBar({ onSubmit, loading }: Props) {
  const [q, setQ] = useState("");
  const [mode, setMode] = useState<SearchMode>("hybrid");

  function submit() {
    if (!loading && q.trim().length > 0) {
      onSubmit(q, mode);
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    submit();
  }

  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") submit();
  }

  return (
    <form className={styles.wrapper} onSubmit={handleSubmit} noValidate>
      <div className={styles.row}>
        <input
          className={styles.input}
          type="search"
          placeholder="Ara — örn. transformer attention, graph neural networks…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={handleKeyDown}
          aria-label="Search query"
          autoFocus
        />
        <button
          className={styles.submitBtn}
          type="submit"
          disabled={loading || q.trim().length === 0}
        >
          {loading ? <span className={styles.spinner} aria-hidden="true" /> : null}
          {loading ? "Aranıyor…" : "Ara"}
        </button>
      </div>
      <ModeSelector value={mode} onChange={setMode} />
    </form>
  );
}
