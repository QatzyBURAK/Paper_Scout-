import { useCallback, useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { THEMES, THEME_INDEX, useTheme, type ThemeId } from "../hooks/useTheme";
import { useI18n } from "../i18n/context";
import styles from "./ThemeSwitcher.module.css";

export function ThemeSwitcher() {
  const { theme, setTheme } = useTheme();
  const { t } = useI18n();
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);

  const buttonRef = useRef<HTMLButtonElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const itemRefs = useRef<(HTMLButtonElement | null)[]>([]);

  const current = THEMES.find((x) => x.id === theme) ?? THEMES[0];

  const openMenu = useCallback(() => {
    setActiveIndex(THEME_INDEX.get(theme) ?? 0);
    setOpen(true);
  }, [theme]);

  const close = useCallback((focusButton: boolean) => {
    setOpen(false);
    if (focusButton) buttonRef.current?.focus();
  }, []);

  // Odak daima activeIndex'i takip eder — menü açıkken tek yetkili kaynak burası.
  useEffect(() => {
    if (!open) return;
    itemRefs.current[activeIndex]?.focus();
  }, [open, activeIndex]);

  // Dışarı tıklayınca kapat.
  useEffect(() => {
    if (!open) return;
    function onPointerDown(e: PointerEvent) {
      const target = e.target as Node;
      if (menuRef.current?.contains(target)) return;
      if (buttonRef.current?.contains(target)) return;
      setOpen(false);
    }
    document.addEventListener("pointerdown", onPointerDown);
    return () => document.removeEventListener("pointerdown", onPointerDown);
  }, [open]);

  function moveFocus(index: number) {
    setActiveIndex((index + THEMES.length) % THEMES.length);
  }

  function select(id: ThemeId) {
    setTheme(id);
    close(true);
  }

  function onButtonKeyDown(e: React.KeyboardEvent<HTMLButtonElement>) {
    if (e.key === "ArrowDown" || e.key === "ArrowUp" || e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      openMenu();
    }
  }

  function onMenuKeyDown(e: React.KeyboardEvent<HTMLDivElement>) {
    switch (e.key) {
      case "Escape":
        e.preventDefault();
        close(true);
        break;
      case "ArrowDown":
        e.preventDefault();
        moveFocus(activeIndex + 1);
        break;
      case "ArrowUp":
        e.preventDefault();
        moveFocus(activeIndex - 1);
        break;
      case "Home":
        e.preventDefault();
        moveFocus(0);
        break;
      case "End":
        e.preventDefault();
        moveFocus(THEMES.length - 1);
        break;
      case "Tab":
        // Odak menüden çıkıyor — kapat ama Tab'ın doğal akışını bozma.
        setOpen(false);
        break;
      default:
        break;
    }
  }

  return (
    <div className={styles.wrap}>
      <button
        ref={buttonRef}
        type="button"
        className={styles.trigger}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label={t("theme.trigger", { name: t(current.labelKey) })}
        onClick={() => (open ? close(false) : openMenu())}
        onKeyDown={onButtonKeyDown}
      >
        <span
          className={styles.dot}
          style={{ background: current.swatch[0], borderColor: current.swatch[1] }}
          aria-hidden="true"
        />
        <span className={styles.triggerLabel}>{t(current.labelKey)}</span>
        <svg
          className={`${styles.chevron} ${open ? styles.chevronOpen : ""}`}
          width="10"
          height="10"
          viewBox="0 0 10 10"
          aria-hidden="true"
        >
          <path
            d="M1.5 3.5 L5 7 L8.5 3.5"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            // AnimatePresence çocuklarını key ile eşler; tek çocukta da stabil
            // bir key vermek çıkış animasyonunun güvenilir tamamlanmasını sağlar.
            key="theme-menu"
            ref={menuRef}
            className={styles.menu}
            role="menu"
            aria-label={t("theme.menuLabel")}
            initial={{ opacity: 0, y: -4, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -4, scale: 0.98 }}
            transition={{ duration: 0.14, ease: [0.25, 0.1, 0.25, 1] }}
            onKeyDown={onMenuKeyDown}
          >
            {THEMES.map((option, index) => {
              const selected = option.id === theme;
              return (
                <button
                  key={option.id}
                  ref={(el) => {
                    itemRefs.current[index] = el;
                  }}
                  type="button"
                  role="menuitemradio"
                  aria-checked={selected}
                  tabIndex={index === activeIndex ? 0 : -1}
                  className={`${styles.item} ${selected ? styles.itemSelected : ""}`}
                  onClick={() => select(option.id)}
                >
                  <span
                    className={styles.dot}
                    style={{ background: option.swatch[0], borderColor: option.swatch[1] }}
                    aria-hidden="true"
                  />
                  <span className={styles.itemLabel}>{t(option.labelKey)}</span>
                  <span className={styles.tone}>{t(option.toneKey)}</span>
                  {selected && (
                    <span className={styles.check} aria-hidden="true">
                      ✓
                    </span>
                  )}
                </button>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
