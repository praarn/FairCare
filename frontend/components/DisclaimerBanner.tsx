"use client";

import { useLanguage } from "@/lib/language-context";

export default function DisclaimerBanner({ text }: { text?: string }) {
  const { t } = useLanguage();
  return (
    <div
      role="note"
      className="rounded-card border border-seal/40 bg-seal-light px-4 py-3 flex gap-3 items-start"
    >
      <span aria-hidden className="text-seal font-display text-lg leading-none mt-0.5">
        !
      </span>
      <p className="text-sm text-ink leading-relaxed">
        {text ?? t("disclaimer.default")}
      </p>
    </div>
  );
}
