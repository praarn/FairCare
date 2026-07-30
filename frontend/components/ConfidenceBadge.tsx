"use client";

import { Estimate } from "@/lib/types";
import { useLanguage } from "@/lib/language-context";
import { TranslationKey } from "@/lib/i18n";

const CONFIG: Record<Estimate["confidence_label"], { key: TranslationKey; classes: string; dot: string }> = {
  high: {
    key: "confidence.high",
    classes: "bg-primary-light text-primary-dark border-primary/30",
    dot: "bg-primary",
  },
  medium: {
    key: "confidence.medium",
    classes: "bg-seal-light text-seal border-seal/40 border-dashed",
    dot: "bg-seal",
  },
  low: {
    key: "confidence.low",
    classes: "bg-alert-light text-alert border-alert/40 border-dashed",
    dot: "bg-alert",
  },
};

export default function ConfidenceBadge({ estimate }: { estimate: Estimate }) {
  const { t } = useLanguage();
  const cfg = CONFIG[estimate.confidence_label];
  return (
    <div
      className={`inline-flex items-center gap-2 rounded-full border-2 px-3 py-1.5 text-sm font-medium ${cfg.classes}`}
    >
      <span aria-hidden className={`w-2 h-2 rounded-full ${cfg.dot}`} />
      {t(cfg.key)}
      <span className="text-xs opacity-70 font-mono">
        {Math.round(estimate.confidence_score * 100)}%
      </span>
    </div>
  );
}
