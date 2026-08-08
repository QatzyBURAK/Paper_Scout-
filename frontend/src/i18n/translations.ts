export type Lang = "tr" | "en";

export const LANGS: { id: Lang; label: string; htmlLang: string; locale: string }[] = [
  { id: "tr", label: "TR", htmlLang: "tr", locale: "tr-TR" },
  { id: "en", label: "EN", htmlLang: "en", locale: "en-GB" },
];

/** Türkçe sözlük aynı zamanda anahtar listesinin kaynağıdır. */
const tr = {
  "nav.search": "Ara",
  "nav.browse": "Gözat",

  "home.heading": "Araştırma Makalesi Keşfi",
  "home.sub": "arXiv ve Semantic Scholar'dan keyword, semantic ve hybrid arama ile makale bul.",
  "home.resultsLabel": "Arama sonuçları",

  "browse.heading": "Tüm Makaleler",
  "browse.sub": "Veritabanındaki tüm makaleler — yeniden aramak için ana sayfayı kullan.",
  "browse.listLabel": "Makale listesi",

  "search.placeholder": "Ara — örn. transformer attention, graph neural networks…",
  "search.ariaLabel": "Arama sorgusu",
  "search.submit": "Ara",
  "search.submitting": "Aranıyor…",
  "mode.groupLabel": "Arama modu",

  "empty.idle": "Bir konu ara — örn. \"transformer attention\" ya da \"graph neural networks\".",
  "empty.empty": "Sonuç bulunamadı. Farklı bir sorgu ya da arama modu dene.",
  "empty.error": "Arama başarısız oldu.",
  "empty.retry": "Tekrar dene",

  "ingest.toggle": "↓ Yeni makale çek",
  "ingest.placeholder": "Konu — örn. vision language model",
  "ingest.periodLabel": "Dönem",
  "ingest.period.all": "Tümü",
  "ingest.period.month": "Son 1 ay",
  "ingest.period.week": "Son 1 hafta",
  "ingest.sourceLabel": "Kaynak",
  "ingest.limitLabel": "Kaynak başına makale sayısı",
  "ingest.fetch": "Çek",
  "ingest.fetching": "Çekiliyor…",
  "ingest.noSource": "En az bir kaynak seçilmeli",
  "ingest.result": "{fetched} çekildi · {saved} eklendi · {merged} güncellendi",

  "results.count": "{count} sonuç",

  "loadMore.exhausted": "— TÜM SONUÇLAR GÖSTERİLDİ —",
  "loadMore.loading": "Yükleniyor…",
  "loadMore.button": "Daha fazla yükle",

  "card.openDetails": "{title} detaylarını aç",
  "card.moreAuthors": "+{count} yazar daha",
  "card.citations": "{count} atıf",

  "modal.close": "Kapat",
  "modal.openArxiv": "arXiv'de Aç",
  "modal.openSs": "Semantic Scholar'da Aç",

  "error.networkSearch": "Sunucuya bağlanılamadı — backend çalışıyor mu? (127.0.0.1:8001)",
  "error.network": "Sunucuya bağlanılamadı.",
  "error.unexpected": "Beklenmeyen bir hata oluştu.",

  "theme.trigger": "Tema: {name}. Değiştirmek için aç.",
  "theme.menuLabel": "Tema seçimi",
  "theme.name.system": "Sistem tercihi",
  "theme.name.ink": "Kağıt & Mürekkep",
  "theme.name.dark": "Slate Terminal",
  "theme.name.yacht": "Yacht Club",
  "theme.name.cappuccino": "Cappuccino",
  "theme.name.noir": "Neon Noir",
  "theme.name.emerald": "Emerald Odyssey",
  "theme.name.blossom": "Cherry Blossom",
  "theme.name.lavender": "Lavender Fields",
  "theme.name.eveningrose": "Evening Rose",
  "theme.name.spaceberry": "Space Berries",
  "tone.auto": "Oto",
  "tone.light": "Açık",
  "tone.dark": "Koyu",

  "lang.groupLabel": "Dil",
  "lang.switchTo": "Dili {label} yap",
} as const;

export type MessageKey = keyof typeof tr;

const en: Record<MessageKey, string> = {
  "nav.search": "Search",
  "nav.browse": "Browse",

  "home.heading": "Research Paper Discovery",
  "home.sub": "Find papers from arXiv and Semantic Scholar using keyword, semantic and hybrid search.",
  "home.resultsLabel": "Search results",

  "browse.heading": "All Papers",
  "browse.sub": "Every paper in the database — use the home page to run a new search.",
  "browse.listLabel": "Paper list",

  "search.placeholder": "Search — e.g. transformer attention, graph neural networks…",
  "search.ariaLabel": "Search query",
  "search.submit": "Search",
  "search.submitting": "Searching…",
  "mode.groupLabel": "Search mode",

  "empty.idle": "Search for a topic — e.g. \"transformer attention\" or \"graph neural networks\".",
  "empty.empty": "No results found. Try a different query or search mode.",
  "empty.error": "Search failed.",
  "empty.retry": "Try again",

  "ingest.toggle": "↓ Fetch new papers",
  "ingest.placeholder": "Topic — e.g. vision language model",
  "ingest.periodLabel": "Period",
  "ingest.period.all": "All",
  "ingest.period.month": "Last month",
  "ingest.period.week": "Last week",
  "ingest.sourceLabel": "Source",
  "ingest.limitLabel": "Papers per source",
  "ingest.fetch": "Fetch",
  "ingest.fetching": "Fetching…",
  "ingest.noSource": "Select at least one source",
  "ingest.result": "{fetched} fetched · {saved} added · {merged} updated",

  "results.count": "{count} results",

  "loadMore.exhausted": "— ALL RESULTS SHOWN —",
  "loadMore.loading": "Loading…",
  "loadMore.button": "Load more",

  "card.openDetails": "Open details for {title}",
  "card.moreAuthors": "+{count} more",
  "card.citations": "{count} citations",

  "modal.close": "Close",
  "modal.openArxiv": "Open on arXiv",
  "modal.openSs": "Open on Semantic Scholar",

  "error.networkSearch": "Could not reach the server — is the backend running? (127.0.0.1:8001)",
  "error.network": "Could not reach the server.",
  "error.unexpected": "Something went wrong.",

  "theme.trigger": "Theme: {name}. Open to change.",
  "theme.menuLabel": "Theme selection",
  "theme.name.system": "System preference",
  "theme.name.ink": "Ink & Paper",
  "theme.name.dark": "Slate Terminal",
  "theme.name.yacht": "Yacht Club",
  "theme.name.cappuccino": "Cappuccino",
  "theme.name.noir": "Neon Noir",
  "theme.name.emerald": "Emerald Odyssey",
  "theme.name.blossom": "Cherry Blossom",
  "theme.name.lavender": "Lavender Fields",
  "theme.name.eveningrose": "Evening Rose",
  "theme.name.spaceberry": "Space Berries",
  "tone.auto": "Auto",
  "tone.light": "Light",
  "tone.dark": "Dark",

  "lang.groupLabel": "Language",
  "lang.switchTo": "Switch language to {label}",
};

export const MESSAGES: Record<Lang, Record<MessageKey, string>> = { tr, en };

export type TranslateParams = Record<string, string | number>;

/** "{name}" biçimindeki yer tutucuları doldurur. */
export function translate(
  lang: Lang,
  key: MessageKey,
  params?: TranslateParams,
): string {
  const template = MESSAGES[lang][key];
  if (!params) return template;
  return template.replace(/\{(\w+)\}/g, (match, name: string) =>
    name in params ? String(params[name]) : match,
  );
}
