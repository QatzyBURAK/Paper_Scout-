import type { Paper } from "../types/paper";
import { SourceBadge } from "./SourceBadge";
import { formatDate } from "../lib/formatDate";
import { useI18n } from "../i18n/context";
import styles from "./PaperCard.module.css";

const MAX_AUTHORS = 3;

interface Props {
  paper: Paper;
  onSelect?: (paper: Paper) => void;
}

export function PaperCard({ paper, onSelect }: Props) {
  const { t, locale } = useI18n();
  const date = formatDate(paper.published_date, locale);
  const visibleAuthors = paper.authors.slice(0, MAX_AUTHORS).join(", ");
  const extraAuthors = paper.authors.length - MAX_AUTHORS;
  const citations = paper.citation_count.toLocaleString(locale);

  return (
    <article className={styles.card}>
      {onSelect && (
        <button
          type="button"
          className={styles.overlayBtn}
          onClick={() => onSelect(paper)}
          aria-label={t("card.openDetails", { title: paper.title })}
        />
      )}

      <p className={styles.title}>{paper.title}</p>

      {paper.authors.length > 0 && (
        <p className={styles.authors}>
          {visibleAuthors}
          {extraAuthors > 0 && (
            <span className={styles.moreAuthors}>
              {" "}
              {t("card.moreAuthors", { count: extraAuthors })}
            </span>
          )}
        </p>
      )}

      {paper.abstract && (
        <p className={styles.abstract}>{paper.abstract}</p>
      )}

      <div className={styles.meta}>
        <SourceBadge source={paper.source} />
        {date && <span className={styles.metaText}>{date}</span>}
        <span className={styles.metaText}>{t("card.citations", { count: citations })}</span>
      </div>
    </article>
  );
}
