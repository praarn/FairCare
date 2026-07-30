"use client";

import { useLanguage } from "@/lib/language-context";

export default function LanguageToggle() {
  const { lang, setLang } = useLanguage();

  return (
    <button
      type="button"
      onClick={() => setLang(lang === "en" ? "hi" : "en")}
      className="shrink-0 px-3 py-1.5 rounded-full text-sm font-medium border border-line text-ink-soft hover:border-primary/50 hover:text-primary transition-colors"
      aria-label="Toggle language between English and Hindi"
    >
      {lang === "en" ? "हिंदी" : "English"}
    </button>
  );
}
