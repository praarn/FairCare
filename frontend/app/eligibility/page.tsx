"use client";

import { useState } from "react";
import { checkSchemeEligibility } from "@/lib/api";
import { STATES, SchemeResult } from "@/lib/types";
import { useLanguage } from "@/lib/language-context";

export default function EligibilityPage() {
  const { t } = useLanguage();
  const [income, setIncome] = useState("");
  const [state, setState] = useState(STATES[0]);
  const [isGovtEmployee, setIsGovtEmployee] = useState(false);
  const [results, setResults] = useState<SchemeResult[] | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await checkSchemeEligibility({
        annual_household_income: income ? Number(income) : undefined,
        state,
        is_govt_employee_or_pensioner: isGovtEmployee,
      });
      setResults(data);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <p className="text-seal font-semibold text-sm uppercase tracking-wide mb-2">
          {t("eligibility.eyebrow")}
        </p>
        <h1 className="font-display text-3xl sm:text-4xl font-semibold text-ink leading-tight">
          {t("eligibility.title")}
        </h1>
        <p className="mt-2 text-ink-soft text-base max-w-xl">{t("eligibility.subtitle")}</p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="rounded-card border border-line bg-surface p-5 sm:p-6 shadow-card flex flex-col gap-5"
      >
        <div>
          <label htmlFor="income-input" className="block text-sm font-medium text-ink mb-1.5">
            {t("eligibility.incomeLabel")}
          </label>
          <input
            id="income-input"
            type="number"
            min={0}
            placeholder={t("eligibility.incomePlaceholder")}
            value={income}
            onChange={(e) => setIncome(e.target.value)}
            className="w-full rounded-card border border-line bg-surface px-4 py-3 text-base text-ink focus:border-primary"
          />
        </div>

        <div>
          <label htmlFor="state-select" className="block text-sm font-medium text-ink mb-1.5">
            {t("eligibility.stateLabel")}
          </label>
          <select
            id="state-select"
            value={state}
            onChange={(e) => setState(e.target.value)}
            className="w-full rounded-card border border-line bg-surface px-4 py-3 text-base text-ink focus:border-primary"
          >
            {STATES.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        <label className="flex items-center gap-2.5 text-sm text-ink">
          <input
            type="checkbox"
            checked={isGovtEmployee}
            onChange={(e) => setIsGovtEmployee(e.target.checked)}
            className="w-4 h-4 accent-primary"
          />
          {t("eligibility.govtEmployeeLabel")}
        </label>

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-card bg-primary hover:bg-primary-dark disabled:opacity-60 text-white font-semibold text-base py-3.5 transition-colors"
        >
          {loading ? t("eligibility.checking") : t("eligibility.submit")}
        </button>
      </form>

      {results && (
        <div className="flex flex-col gap-3">
          {results.map((r) => (
            <div
              key={r.scheme_id}
              className={`rounded-card border bg-surface p-4 sm:p-5 shadow-card flex flex-col gap-2.5 ${
                r.eligible ? "border-primary/40" : "border-line"
              }`}
            >
              <div className="flex items-center justify-between gap-2 flex-wrap">
                <h3 className="font-display text-lg font-semibold text-ink">{r.name}</h3>
                <span
                  className={`text-[11px] font-semibold uppercase tracking-wide px-2.5 py-1 rounded-full ${
                    r.eligible ? "bg-primary-light text-primary-dark" : "bg-line text-ink-soft"
                  }`}
                >
                  {r.eligible ? t("eligibility.eligible") : t("eligibility.notEligible")}
                </span>
              </div>
              <p className="text-sm text-ink-soft">{r.reason}</p>

              <div className="perforated" />

              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-ink-soft mb-1">
                  {t("eligibility.coverage")}
                </p>
                <p className="text-sm text-ink">{r.coverage_details}</p>
              </div>

              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-ink-soft mb-1">
                  {t("eligibility.howToApply")}
                </p>
                <ol className="text-sm text-ink-soft list-decimal list-inside flex flex-col gap-0.5">
                  {r.application_steps.map((step, i) => (
                    <li key={i}>{step}</li>
                  ))}
                </ol>
              </div>

              <a
                href={r.official_link}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-primary font-medium underline underline-offset-2 w-fit"
              >
                {t("eligibility.officialLink")} →
              </a>

              <p className="text-[11px] text-ink-soft italic">{r.note}</p>
            </div>
          ))}
        </div>
      )}

      <div className="rounded-card border border-seal/40 bg-seal-light px-4 py-3 text-sm text-ink">
        {t("eligibility.disclaimer")}
      </div>
    </div>
  );
}
