import { useI18n } from "../i18n/context";
import { LANGS } from "../i18n/translations";
import styles from "./LanguageSwitcher.module.css";

export function LanguageSwitcher() {
  const { lang, setLang, t } = useI18n();

  return (
    <div className={styles.group} role="group" aria-label={t("lang.groupLabel")}>
      {LANGS.map((entry) => {
        const active = entry.id === lang;
        return (
          <button
            key={entry.id}
            type="button"
            className={`${styles.btn} ${active ? styles.active : ""}`}
            aria-pressed={active}
            aria-label={t("lang.switchTo", { label: entry.label })}
            onClick={() => setLang(entry.id)}
          >
            {entry.label}
          </button>
        );
      })}
    </div>
  );
}
