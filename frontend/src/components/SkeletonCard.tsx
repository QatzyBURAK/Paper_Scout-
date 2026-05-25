import styles from "./SkeletonCard.module.css";

export function SkeletonCard() {
  return (
    <div className={styles.card} aria-hidden="true">
      <div className={`${styles.line} ${styles.title}`} />
      <div className={`${styles.line} ${styles.titleShort}`} />
      <div className={`${styles.line} ${styles.author}`} />
      <div className={`${styles.line} ${styles.abs1}`} />
      <div className={`${styles.line} ${styles.abs2}`} />
      <div className={`${styles.line} ${styles.abs3}`} />
      <div className={`${styles.line} ${styles.meta}`} />
    </div>
  );
}
