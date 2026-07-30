"use client";

import { useState } from "react";
import { useLanguage } from "@/lib/language-context";
import { usePreferences } from "@/lib/preferences-context";

export default function SettingsMenu() {
  const { lang, setLang, t } = useLanguage();
  const { dataSaver, setDataSaver, largeText, setLargeText } = usePreferences();
  const [open, setOpen] = useState(false);

  return (
    <div className="relative print:hidden">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-label={t("settings.label")}
        aria-expanded={open}
        className="w-9 h-9 shrink-0 rounded-full border border-line flex items-center justify-center text-ink-soft hover:border-primary/50 hover:text-primary transition-colors"
      >
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" aria-hidden>
          <path
            d="M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z"
            stroke="currentColor"
            strokeWidth="1.6"
          />
          <path
            d="M19.4 13a7.4 7.4 0 0 0 .1-2l1.9-1.5-2-3.4-2.2.9a7.6 7.6 0 0 0-1.7-1L15 3.5h-4l-.3 2.5a7.6 7.6 0 0 0-1.7 1l-2.2-.9-2 3.4L6.5 11a7.4 7.4 0 0 0 0 2l-1.9 1.5 2 3.4 2.2-.9c.5.4 1.1.7 1.7 1l.3 2.5h4l.3-2.5a7.6 7.6 0 0 0 1.7-1l2.2.9 2-3.4-1.9-1.5Z"
            stroke="currentColor"
            strokeWidth="1.2"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {open && (
        <>
          <button
            type="button"
            aria-label="Close settings"
            onClick={() => setOpen(false)}
            className="fixed inset-0 z-10 cursor-default"
          />
          <div className="absolute right-0 mt-2 w-64 rounded-card border border-line bg-surface shadow-card p-4 flex flex-col gap-3 z-20">
            <button
              type="button"
              onClick={() => setLang(lang === "en" ? "hi" : "en")}
              className="flex items-center justify-between text-sm text-ink"
            >
              <span>{t("settings.language")}</span>
              <span className="font-medium text-primary">{lang === "en" ? "हिंदी" : "English"}</span>
            </button>

            <label className="flex items-center justify-between text-sm text-ink cursor-pointer">
              <span>{t("settings.dataSaver")}</span>
              <input
                type="checkbox"
                checked={dataSaver}
                onChange={(e) => setDataSaver(e.target.checked)}
                className="w-4 h-4 accent-primary"
              />
            </label>

            <label className="flex items-center justify-between text-sm text-ink cursor-pointer">
              <span>{t("settings.largeText")}</span>
              <input
                type="checkbox"
                checked={largeText}
                onChange={(e) => setLargeText(e.target.checked)}
                className="w-4 h-4 accent-primary"
              />
            </label>
          </div>
        </>
      )}
    </div>
  );
}
