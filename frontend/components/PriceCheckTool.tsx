"use client";

import { useState } from "react";
import { formatINR } from "@/lib/format";
import { useLanguage } from "@/lib/language-context";

export default function PriceCheckTool({
  costMin,
  costMax,
}: {
  costMin: number;
  costMax: number;
}) {
  const { t } = useLanguage();
  const [quote, setQuote] = useState("");
  const [checked, setChecked] = useState<number | null>(null);

  function handleCheck(e: React.FormEvent) {
    e.preventDefault();
    const value = Number(quote);
    if (!quote || Number.isNaN(value)) return;
    setChecked(value);
  }

  let verdict: "within" | "below" | "above" | null = null;
  if (checked != null) {
    if (checked < costMin) verdict = "below";
    else if (checked > costMax) verdict = "above";
    else verdict = "within";
  }

  const VERDICT_STYLE: Record<string, string> = {
    within: "border-primary/40 bg-primary-light text-primary-dark",
    below: "border-seal/40 bg-seal-light text-ink",
    above: "border-alert/40 bg-alert-light text-alert",
  };

  return (
    <div className="rounded-card border border-line bg-surface p-5 sm:p-6 shadow-card flex flex-col gap-4">
      <div>
        <h3 className="font-display text-lg font-semibold text-ink">{t("priceCheck.title")}</h3>
        <p className="text-xs text-ink-soft mt-1">{t("priceCheck.subtitle")}</p>
      </div>

      <form onSubmit={handleCheck} className="flex gap-2">
        <input
          type="number"
          min={0}
          placeholder={t("priceCheck.placeholder")}
          value={quote}
          onChange={(e) => {
            setQuote(e.target.value);
            setChecked(null);
          }}
          className="flex-1 rounded-card border border-line bg-surface px-4 py-2.5 text-base text-ink focus:border-primary"
        />
        <button
          type="submit"
          className="shrink-0 rounded-card bg-primary hover:bg-primary-dark text-white font-semibold px-5 py-2.5 transition-colors"
        >
          {t("priceCheck.check")}
        </button>
      </form>

      {verdict && (
        <div className={`rounded-card border px-4 py-3 text-sm ${VERDICT_STYLE[verdict]}`}>
          <p className="font-medium">
            {verdict === "within" && t("priceCheck.withinRange")}
            {verdict === "below" && t("priceCheck.belowRange")}
            {verdict === "above" && t("priceCheck.aboveRange")}
          </p>
          <p className="text-xs mt-1 opacity-90">
            {formatINR(costMin)} – {formatINR(costMax)}
          </p>
          {verdict === "above" && (
            <p className="text-xs mt-1.5">{t("priceCheck.aboveRangeSuggestion")}</p>
          )}
        </div>
      )}
    </div>
  );
}
