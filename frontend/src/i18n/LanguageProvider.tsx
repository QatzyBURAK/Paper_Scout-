import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { I18nContext, LANG_STORAGE_KEY, type I18nValue } from "./context";
import { LANGS, translate, type Lang, type MessageKey, type TranslateParams } from "./translations";

function isLang(value: string | null): value is Lang {
  return value === "tr" || value === "en";
}

/** Kayıtlı tercih → tarayıcı dili → tr. */
function initialLang(): Lang {
  try {
    const stored = localStorage.getItem(LANG_STORAGE_KEY);
    if (isLang(stored)) return stored;
  } catch {
    // localStorage kapalı — tarayıcı diline düş.
  }
  return navigator.language?.toLowerCase().startsWith("en") ? "en" : "tr";
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(initialLang);

  useEffect(() => {
    const entry = LANGS.find((l) => l.id === lang) ?? LANGS[0];
    document.documentElement.setAttribute("lang", entry.htmlLang);
    try {
      localStorage.setItem(LANG_STORAGE_KEY, lang);
    } catch {
      // Tercih kaydedilemezse dil bu oturum boyunca geçerli kalır.
    }
  }, [lang]);

  const setLang = useCallback((next: Lang) => {
    setLangState(next);
  }, []);

  const value = useMemo<I18nValue>(() => {
    const entry = LANGS.find((l) => l.id === lang) ?? LANGS[0];
    return {
      lang,
      setLang,
      t: (key: MessageKey, params?: TranslateParams) => translate(lang, key, params),
      locale: entry.locale,
    };
  }, [lang, setLang]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}
