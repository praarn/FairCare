"use client";

import { formatINR } from "@/lib/format";
import { useLanguage } from "@/lib/language-context";
import { TranslationKey } from "@/lib/i18n";

// Generic, treatment-agnostic industry-typical ranges. Intentionally NOT
// derived from cost_records — these are illustrative add-ons only, and
// the UI must never let them be mistaken for the same verified-data
// standard as the core estimate above them.
const ADD_ONS: { key: TranslationKey; pct: number }[] = [
  { key: "costOfCare.preOp", pct: 0.08 },
  { key: "costOfCare.medicines", pct: 0.06 },
  { key: "costOfCare.followUp", pct: 0.04 },
];

export default function CostOfCareBreakdown({ procedureCost }: { procedureCost: number }) {
  const { t } = useLanguage();
  const totalPct = ADD_ONS.reduce((sum, a) => sum + a.pct, 0);

  return (
    <div className="rounded-card border border-line bg-surface p-5 sm:p-6 shadow-card flex flex-col gap-4">
      <div>
        <h3 className="font-display text-lg font-semibold text-ink">{t("costOfCare.title")}</h3>
        <p className="text-xs text-ink-soft mt-1">{t("costOfCare.subtitle")}</p>
      </div>

      <ul className="flex flex-col gap-2">
        {ADD_ONS.map((addOn) => (
          <li key={addOn.key} className="flex items-center justify-between text-sm">
            <span className="text-ink-soft">{t(addOn.key)}</span>
            <span className="font-mono font-medium text-ink">
              {formatINR(procedureCost * addOn.pct)}
            </span>
          </li>
        ))}
      </ul>

      <div className="perforated" />

      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-ink">{t("costOfCare.totalLabel")}</span>
        <span className="font-mono text-lg font-bold text-primary-dark">
          {formatINR(procedureCost * totalPct)}
        </span>
      </div>

      <p className="text-[11px] text-ink-soft leading-relaxed">{t("costOfCare.disclaimer")}</p>
    </div>
  );
}
