"use client";

import { useState } from "react";
import { formatINR } from "@/lib/format";
import { useLanguage } from "@/lib/language-context";

const TENURES = [3, 6, 12, 24];

export default function PaymentPlanEstimator({ amount }: { amount: number }) {
  const { t } = useLanguage();
  const [months, setMonths] = useState(6);
  const perMonth = amount / months;

  return (
    <div className="rounded-card border border-line bg-surface p-5 sm:p-6 shadow-card flex flex-col gap-4">
      <div>
        <h3 className="font-display text-lg font-semibold text-ink">{t("payment.title")}</h3>
        <p className="text-xs text-ink-soft mt-1">{t("payment.note")}</p>
      </div>

      <div className="flex gap-2 flex-wrap">
        {TENURES.map((m) => (
          <button
            key={m}
            type="button"
            onClick={() => setMonths(m)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
              months === m
                ? "bg-primary text-white border-primary"
                : "border-line text-ink-soft hover:border-primary/50"
            }`}
          >
            {m} {t("payment.monthsSuffix")}
          </button>
        ))}
      </div>

      <div className="flex items-baseline gap-2">
        <span className="font-mono text-2xl font-bold text-primary-dark">
          {formatINR(perMonth)}
        </span>
        <span className="text-sm text-ink-soft">
          {t("payment.perMonthFor")} {months} {t("payment.monthsSuffix")}
        </span>
      </div>

      <p className="text-[11px] text-ink-soft leading-relaxed">
        {t("payment.footnotePrefix")} {formatINR(amount)}
        {t("payment.footnoteSuffix")}
      </p>
    </div>
  );
}
