import { motion } from "framer-motion";
import type { Variants } from "framer-motion";
import type { Paper } from "../types/paper";
import { PaperCard } from "./PaperCard";
import styles from "./ResultsList.module.css";

const container: Variants = {
  initial: {},
  animate: { transition: { staggerChildren: 0.04 } },
};

const item: Variants = {
  initial: { opacity: 0, y: 6 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.18, ease: [0.25, 0.1, 0.25, 1] } },
};

interface Props {
  papers: Paper[];
  total?: number | null;
  onSelect?: (paper: Paper) => void;
}

export function ResultsList({ papers, total, onSelect }: Props) {
  const displayCount = total ?? papers.length;
  return (
    <div>
      <p className={styles.count}>{displayCount} sonuç</p>
      <motion.div
        className={styles.list}
        variants={container}
        initial="initial"
        animate="animate"
      >
        {papers.map((paper) => (
          <motion.div key={paper.external_id} variants={item} layout>
            <PaperCard paper={paper} onSelect={onSelect} />
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
