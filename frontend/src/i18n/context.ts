import { createContext, useContext } from "react";
import type { Lang, MessageKey, TranslateParams } from "./translations";

export const LANG_STORAGE_KEY = "paper-scout-lang";

export interface I18nValue {
  lang: Lang;
  setLang: (next: Lang) => void;
  /** Çeviriyi getirir; {placeholder} varsa params ile doldurur. */
  t: (key: MessageKey, params?: TranslateParams) => string;
  /** Intl için dil etiketi — tarih ve sayı biçimlemede kullanılır. */
  locale: string;
}

export const I18nContext = createContext<I18nValue | null>(null);

export function useI18n(): I18nValue {
  const ctx = useContext(I18nContext);
  if (ctx === null) {
    throw new Error("useI18n, LanguageProvider içinde çağrılmalı.");
  }
  return ctx;
}
