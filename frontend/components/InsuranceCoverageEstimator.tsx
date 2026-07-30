"use client";

import { useState } from "react";
import { formatINR } from "@/lib/format";
import { useLanguage } from "@/lib/language-context";

export default function InsuranceCoverageEstimator({ procedureCost }: { procedureCost: number }) {
  const { t } = useLanguage();
  const [sumInsured, setSumInsured] = useState("");
  const [alreadyUsed, setAlreadyUsed] = useState("");
  const [copayPct, setCopayPct] = useState("10");
  const [result, setResult] = useState<{ covered: number; outOfPocket: number } | null>(null);

  function handleCalculate(e: React.FormEvent) {
    e.preventDefault();
    const sum = Number(sumInsured) || 0;
    const used = Number(alreadyUsed) || 0;
    const copay = Number(copayPct) || 0;

    const remainingSumInsured = Math.max(sum - used, 0);
    const copayAmount = procedureCost * (copay / 100);
    const payableBeforeCap = Math.max(procedureCost - copayAmount, 0);
    const covered = Math.min(payableBeforeCap, remainingSumInsured);
    const outOfPocket = procedureCost - covered;

    setResult({ covered, outOfPocket });
  }

  return (
    <div className="rounded-card border border-line bg-surface p-5 sm:p-6 shadow-card flex flex-col gap-4">
      <div>
        <h3 className="font-display text-lg font-semibold text-ink">{t("insurance.title")}</h3>
        <p className="text-xs text-ink-soft mt-1">{t("insurance.subtitle")}</p>
      </div>

      <form onSubmit={handleCalculate} className="flex flex-col gap-3">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-ink mb-1">
              {t("insurance.sumInsuredLabel")}
            </label>
            <input
              type="number"
              min={0}
              value={sumInsured}
              onChange={(e) => setSumInsured(e.target.value)}
              className="w-full rounded-card border border-line bg-surface px-3 py-2 text-sm text-ink focus:border-primary"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-ink mb-1">
              {t("insurance.usedLabel")}
            </label>
            <input
              type="number"
              min={0}
              value={alreadyUsed}
              onChange={(e) => setAlreadyUsed(e.target.value)}
              className="w-full rounded-card border border-line bg-surface px-3 py-2 text-sm text-ink focus:border-primary"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-ink mb-1">
            {t("insurance.copayLabel")}
          </label>
          <input
            type="number"
            min={0}
            max={100}
            value={copayPct}
            onChange={(e) => setCopayPct(e.target.value)}
            className="w-full rounded-card border border-line bg-surface px-3 py-2 text-sm text-ink focus:border-primary"
          />
        </div>

        <button
          type="submit"
          className="w-full rounded-card bg-primary hover:bg-primary-dark text-white font-semibold text-sm py-2.5 transition-colors"
        >
          {t("insurance.calculate")}
        </button>
      </form>

      {result && (
        <div className="grid grid-cols-2 gap-3 pt-1">
          <div className="rounded-card bg-primary-light px-3 py-2.5 text-center">
            <div className="text-[11px] uppercase tracking-wide text-primary-dark">
              {t("insurance.covered")}
            </div>
            <div className="font-mono text-lg font-bold text-primary-dark">
              {formatINR(result.covered)}
            </div>
          </div>
          <div className="rounded-card bg-alert-light px-3 py-2.5 text-center">
            <div className="text-[11px] uppercase tracking-wide text-alert">
              {t("insurance.outOfPocket")}
            </div>
            <div className="font-mono text-lg font-bold text-alert">
              {formatINR(result.outOfPocket)}
            </div>
          </div>
        </div>
      )}

      <p className="text-[11px] text-ink-soft leading-relaxed">{t("insurance.disclaimer")}</p>
    </div>
  );
}
