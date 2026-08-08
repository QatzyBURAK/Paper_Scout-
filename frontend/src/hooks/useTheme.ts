import { useCallback, useEffect, useState } from "react";
import type { MessageKey } from "../i18n/translations";

export const THEME_STORAGE_KEY = "paper-scout-theme";

export type ThemeId =
  | "system"
  | "ink"
  | "dark"
  | "yacht"
  | "cappuccino"
  | "noir"
  | "emerald"
  | "blossom"
  | "lavender"
  | "eveningrose"
  | "spaceberry";

export interface ThemeOption {
  id: ThemeId;
  /** Tema adının çeviri anahtarı. */
  labelKey: MessageKey;
  /** Açık/koyu rozetinin çeviri anahtarı. */
  toneKey: MessageKey;
  /** Menüdeki küçük önizleme noktası: [yüzey rengi, aksan rengi] */
  swatch: [string, string];
}

const LIGHT = "tone.light" as const;
const DARK = "tone.dark" as const;

/**
 * tokens.css içindeki [data-theme="..."] blokları ile birebir eşleşmeli.
 * Paletler Figma Color Combinations kütüphanesinden uyarlanmıştır.
 */
export const THEMES: ThemeOption[] = [
  { id: "system", labelKey: "theme.name.system", toneKey: "tone.auto", swatch: ["#f7f6f2", "#0f172a"] },
  { id: "ink", labelKey: "theme.name.ink", toneKey: LIGHT, swatch: ["#f7f6f2", "#1e3a8a"] },
  { id: "yacht", labelKey: "theme.name.yacht", toneKey: LIGHT, swatch: ["#f4f6f8", "#14507d"] },
  { id: "cappuccino", labelKey: "theme.name.cappuccino", toneKey: LIGHT, swatch: ["#f6f0e8", "#8a4b1e"] },
  { id: "blossom", labelKey: "theme.name.blossom", toneKey: LIGHT, swatch: ["#fdf3f5", "#c02a56"] },
  { id: "lavender", labelKey: "theme.name.lavender", toneKey: LIGHT, swatch: ["#f6f4fc", "#6d3fc4"] },
  { id: "dark", labelKey: "theme.name.dark", toneKey: DARK, swatch: ["#1e293b", "#38bdf8"] },
  { id: "noir", labelKey: "theme.name.noir", toneKey: DARK, swatch: ["#121419", "#22d3ee"] },
  { id: "emerald", labelKey: "theme.name.emerald", toneKey: DARK, swatch: ["#0b241c", "#34d399"] },
  { id: "eveningrose", labelKey: "theme.name.eveningrose", toneKey: DARK, swatch: ["#2a1720", "#f9a8d4"] },
  { id: "spaceberry", labelKey: "theme.name.spaceberry", toneKey: DARK, swatch: ["#1c1440", "#a78bfa"] },
];

/** Tema id → THEMES içindeki sıra. Menüde ok tuşu gezinmesi için kullanılır. */
export const THEME_INDEX: ReadonlyMap<ThemeId, number> = new Map(
  THEMES.map((t, i) => [t.id, i] as const),
);

function isThemeId(value: string | null): value is ThemeId {
  return value !== null && THEME_INDEX.has(value as ThemeId);
}

/**
 * Kayıtlı tercihi okur. localStorage erişimi (private mode, kısıtlı iframe)
 * hata fırlatabildiği için try/catch ile sarmalanmıştır.
 */
export function readStoredTheme(): ThemeId {
  try {
    const raw = localStorage.getItem(THEME_STORAGE_KEY);
    return isThemeId(raw) ? raw : "system";
  } catch {
    return "system";
  }
}

/** <html> üzerindeki data-theme'i günceller. "system" → attribute kaldırılır. */
export function applyTheme(theme: ThemeId): void {
  const root = document.documentElement;
  if (theme === "system") {
    root.removeAttribute("data-theme");
  } else {
    root.setAttribute("data-theme", theme);
  }
}

export function useTheme(): {
  theme: ThemeId;
  setTheme: (next: ThemeId) => void;
} {
  const [theme, setThemeState] = useState<ThemeId>(readStoredTheme);

  useEffect(() => {
    applyTheme(theme);
    try {
      localStorage.setItem(THEME_STORAGE_KEY, theme);
    } catch {
      // Tercih kaydedilemezse tema yine de bu oturum boyunca geçerli kalır.
    }
  }, [theme]);

  const setTheme = useCallback((next: ThemeId) => {
    setThemeState(next);
  }, []);

  return { theme, setTheme };
}
