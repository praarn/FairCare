"use client";

import { useLanguage } from "@/lib/language-context";
import { LANGUAGES, LANGUAGE_LABELS, Lang } from "@/lib/i18n";

export default function LanguageDropdown() {
  const { lang, setLang } = useLanguage();

  return (
    <select
      value={lang}
      onChange={(e) => setLang(e.target.value as Lang)}
      aria-label="Select language"
      className="shrink-0 rounded-full border border-line bg-surface text-ink-soft text-sm font-medium pl-3 pr-7 py-1.5 hover:border-primary/50 focus:border-primary cursor-pointer print:hidden"
    >
      {LANGUAGES.map((code) => (
        <option key={code} value={code}>
          {LANGUAGE_LABELS[code]}
        </option>
      ))}
    </select>
  );
}
