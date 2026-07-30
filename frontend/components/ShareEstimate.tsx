"use client";

import { useLanguage } from "@/lib/language-context";

export default function ShareEstimate({ whatsappText }: { whatsappText: string }) {
  const { t } = useLanguage();
  const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(whatsappText)}`;

  return (
    <div className="rounded-card border border-line bg-surface p-5 shadow-card flex flex-col gap-3 print:hidden">
      <h3 className="font-display text-base font-semibold text-ink">{t("share.title")}</h3>
      <div className="flex flex-wrap gap-2">
        <a
          href={whatsappUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 rounded-full bg-primary hover:bg-primary-dark text-white text-sm font-medium px-4 py-2 transition-colors"
        >
          {t("share.whatsapp")}
        </a>
        <button
          type="button"
          onClick={() => window.print()}
          className="inline-flex items-center gap-2 rounded-full border border-line text-ink-soft hover:border-primary/50 hover:text-primary text-sm font-medium px-4 py-2 transition-colors"
        >
          {t("share.print")}
        </button>
      </div>
    </div>
  );
}
