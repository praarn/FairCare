"use client";

import { createContext, useContext, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Lang, t as translate, TranslationKey, hospitalTypeLabel } from "./i18n";

const COOKIE_NAME = "sahaj_lang";

type LanguageContextValue = {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: (key: TranslationKey) => string;
  hospitalTypeLabel: (type: string) => string;
};

const LanguageContext = createContext<LanguageContextValue | null>(null);

export function LanguageProvider({
  initialLang,
  children,
}: {
  initialLang: Lang;
  children: React.ReactNode;
}) {
  const [lang, setLangState] = useState<Lang>(initialLang);
  const router = useRouter();

  const setLang = useCallback(
    (next: Lang) => {
      setLangState(next);
      document.cookie = `${COOKIE_NAME}=${next}; path=/; max-age=31536000`;
      // Server components (results/hospitals pages) read the cookie directly,
      // so nudge them to re-render with the new language.
      router.refresh();
    },
    [router]
  );

  return (
    <LanguageContext.Provider
      value={{
        lang,
        setLang,
        t: (key: TranslationKey) => translate(lang, key),
        hospitalTypeLabel: (type: string) => hospitalTypeLabel(lang, type),
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within LanguageProvider");
  return ctx;
}
