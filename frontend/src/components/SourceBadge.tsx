import styles from "./SourceBadge.module.css";
import type { Paper } from "../types/paper";

interface Props {
  source: Paper["source"];
}

export function SourceBadge({ source }: Props) {
  if (source === "arxiv") {
    return <span className={`${styles.badge} ${styles.arxiv}`}>arXiv</span>;
  }
  return <span className={`${styles.badge} ${styles.ss}`}>Semantic Scholar</span>;
}
