import { useEffect, useRef } from "react";
import { AnimatePresence, motion } from "framer-motion";
import type { Paper } from "../types/paper";
import { SourceBadge } from "./SourceBadge";
import { formatDate } from "../lib/formatDate";
import styles from "./PaperDetailModal.module.css";

interface Props {
  paper: Paper | null;
  onClose: () => void;
}

const sourceLabel: Record<Paper["source"], string> = {
  arxiv: "arXiv'de Aç",
  semantic_scholar: "Semantic Scholar'da Aç",
};

export function PaperDetailModal({ paper, onClose }: Props) {
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!paper) return;
    document.body.style.overflow = "hidden";
    closeRef.current?.focus();
    return () => { document.body.style.overflow = ""; };
  }, [paper]);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [onClose]);

  const citations = paper?.citation_count.toLocaleString("en-US");
  const date = paper ? formatDate(paper.published_date) : null;
  const titleId = "modal-title";

  return (
    <AnimatePresence>
      {paper && (
        <motion.div
          className={styles.scrim}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
          onClick={onClose}
        >
          <motion.div
            className={styles.panel}
            role="dialog"
            aria-modal="true"
            aria-labelledby={titleId}
            initial={{ opacity: 0, scale: 0.96, y: 8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.98, y: 4 }}
            transition={{ duration: 0.18, ease: [0.25, 0.1, 0.25, 1] }}
            onClick={(e) => e.stopPropagation()}
          >
            <button
              ref={closeRef}
              type="button"
              className={styles.closeX}
              onClick={onClose}
              aria-label="Kapat"
            >
              ×
            </button>

            <div className={styles.meta}>
              <SourceBadge source={paper.source} />
              {date && <span className={styles.metaText}>{date}</span>}
              <span className={styles.metaText}>{citations} citations</span>
            </div>

            <h2 id={titleId} className={styles.title}>{paper.title}</h2>

            {paper.authors.length > 0 && (
              <p className={styles.authors}>{paper.authors.join(", ")}</p>
            )}

            {paper.abstract && (
              <p className={styles.abstract}>{paper.abstract}</p>
            )}

            <div className={styles.actions}>
              <button
                type="button"
                className={styles.closeBtn}
                onClick={onClose}
              >
                Kapat
              </button>
              <a
                className={styles.openBtn}
                href={paper.url}
                target="_blank"
                rel="noopener noreferrer"
              >
                {sourceLabel[paper.source]}
              </a>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
