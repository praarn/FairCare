"use client";

import { useState } from "react";
import Link from "next/link";
import TreatmentAutocomplete from "@/components/TreatmentAutocomplete";
import DisclaimerBanner from "@/components/DisclaimerBanner";
import { CITIES, STATES, Treatment } from "@/lib/types";
import type { EpisodeResult } from "@/lib/types";
import { estimateEpisode } from "@/lib/api";
import { formatINR } from "@/lib/format";
import { useLanguage } from "@/lib/language-context";

const OTHER_CITY = "__OTHER__";

type Row = { key: number; treatment: Treatment | null; quantity: number };

let nextKey = 1;

export default function EpisodePage() {
  const { t, lang, hospitalTypeLabel } = useLanguage();

  const [rows, setRows] = useState<Row[]>([{ key: 0, treatment: null, quantity: 1 }]);
  const [city, setCity] = useState<string>(CITIES[0]);
  const [state, setState] = useState<string>("Delhi");
  const [hospitalType, setHospitalType] = useState("");
  const [income, setIncome] = useState("");
  const [govtEmployee, setGovtEmployee] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<EpisodeResult | null>(null);

  const cityNotListed = city === OTHER_CITY;

  function updateRow(key: number, patch: Partial<Row>) {
    setRows((rs) => rs.map((r) => (r.key === key ? { ...r, ...patch } : r)));
  }
  function addRow() {
    setRows((rs) => [...rs, { key: nextKey++, treatment: null, quantity: 1 }]);
  }
  function removeRow(key: number) {
    setRows((rs) => (rs.length === 1 ? rs : rs.filter((r) => r.key !== key)));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const items = rows
      .filter((r) => r.treatment)
      .map((r) => ({ treatment_id: r.treatment!.id, quantity: r.quantity }));
    if (items.length === 0) {
      setError(t("episode.pickAtLeastOne"));
      return;
    }
    setError(null);
    setLoading(true);
    setResult(null);
    try {
      const res = await estimateEpisode({
        items,
        city: cityNotListed ? undefined : city,
        state: cityNotListed ? state : undefined,
        hospital_type: hospitalType || undefined,
        lang,
        annual_household_income: income ? Number(income) : undefined,
        is_govt_employee_or_pensioner: govtEmployee || undefined,
      });
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <section>
        <p className="text-seal font-semibold text-sm uppercase tracking-wide mb-2">
          {t("episode.eyebrow")}
        </p>
        <h1 className="font-display text-2xl sm:text-3xl font-semibold text-ink">
          {t("episode.title")}
        </h1>
        <p className="mt-2 text-ink-soft text-sm leading-relaxed max-w-xl">
          {t("episode.subtitle")}
        </p>
      </section>

      <form
        onSubmit={handleSubmit}
        className="rounded-card border border-line bg-surface p-5 sm:p-6 shadow-card flex flex-col gap-5 print:hidden"
      >
        {rows.map((row) => (
          <div key={row.key} className="flex flex-col gap-2 border-b border-line pb-4 last:border-0 last:pb-0">
            <TreatmentAutocomplete onSelect={(tr) => updateRow(row.key, { treatment: tr })} />
            <div className="flex items-end gap-3">
              <div className="flex-1">
                <label className="block text-xs font-medium text-ink-soft mb-1">
                  {t("episode.quantity")}
                </label>
                <input
                  type="number"
                  min={1}
                  max={50}
                  value={row.quantity}
                  onChange={(e) =>
                    updateRow(row.key, {
                      quantity: Math.max(1, Math.min(50, Number(e.target.value) || 1)),
                    })
                  }
                  className="w-24 rounded-card border border-line bg-surface px-3 py-2 text-base text-ink focus:border-primary"
                />
              </div>
              {rows.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeRow(row.key)}
                  className="text-sm text-ink-soft hover:text-alert underline underline-offset-2 pb-2"
                >
                  {t("episode.removeRow")}
                </button>
              )}
            </div>
          </div>
        ))}

        <button
          type="button"
          onClick={addRow}
          className="self-start text-sm text-primary font-medium underline underline-offset-2"
        >
          + {t("episode.addTreatment")}
        </button>

        <div>
          <label htmlFor="ep-city" className="block text-sm font-medium text-ink mb-1.5">
            {t("home.cityLabel")}
          </label>
          <select
            id="ep-city"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            className="w-full rounded-card border border-line bg-surface px-4 py-3 text-base text-ink focus:border-primary"
          >
            {CITIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
            <option value={OTHER_CITY}>{t("home.cityNotListed")}</option>
          </select>
          {cityNotListed && (
            <select
              value={state}
              onChange={(e) => setState(e.target.value)}
              className="mt-3 w-full rounded-card border border-line bg-surface px-4 py-3 text-base text-ink focus:border-primary"
            >
              {STATES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          )}
        </div>

        <div>
          <label htmlFor="ep-type" className="block text-sm font-medium text-ink mb-1.5">
            {t("home.hospitalTypeLabel")}{" "}
            <span className="text-ink-soft font-normal">{t("home.optional")}</span>
          </label>
          <select
            id="ep-type"
            value={hospitalType}
            onChange={(e) => setHospitalType(e.target.value)}
            className="w-full rounded-card border border-line bg-surface px-4 py-3 text-base text-ink focus:border-primary"
          >
            <option value="">{t("home.anyRange")}</option>
            {["govt", "private_low", "private_mid", "private_high"].map((v) => (
              <option key={v} value={v}>
                {hospitalTypeLabel(v)}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="ep-income" className="block text-sm font-medium text-ink mb-1.5">
            {t("episode.incomeLabel")}
          </label>
          <input
            id="ep-income"
            type="number"
            min={0}
            value={income}
            onChange={(e) => setIncome(e.target.value)}
            className="w-full rounded-card border border-line bg-surface px-4 py-3 text-base text-ink focus:border-primary"
          />
          <label className="mt-2 flex items-center gap-2 text-sm text-ink-soft">
            <input
              type="checkbox"
              checked={govtEmployee}
              onChange={(e) => setGovtEmployee(e.target.checked)}
            />
            {t("episode.govtEmployee")}
          </label>
        </div>

        {error && <p className="text-sm text-alert font-medium">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-card bg-primary hover:bg-primary-dark text-white font-semibold text-base py-3.5 transition-colors disabled:opacity-60"
        >
          {loading ? t("episode.calculating") : t("episode.submit")}
        </button>
      </form>

      {result && (
        <div className="flex flex-col gap-5">
          <div className="flex items-center justify-between gap-3 print:hidden">
            <h2 className="font-display text-lg font-semibold text-ink">
              {t("episode.combinedTotal")}
            </h2>
            <button
              type="button"
              onClick={() => window.print()}
              className="text-sm text-primary font-medium underline underline-offset-2"
            >
              {t("episode.print")}
            </button>
          </div>

          {result.lines.length === 0 ? (
            <div className="rounded-card border border-line bg-surface p-5 text-center text-ink-soft text-sm">
              {t("episode.noLines")}
            </div>
          ) : (
            <>
              <div className="rounded-card border border-line bg-surface shadow-card overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-ink-soft border-b border-line">
                      <th className="px-4 py-2 font-medium">{t("episode.rowTreatment")}</th>
                      <th className="px-4 py-2 font-medium text-right">×</th>
                      <th className="px-4 py-2 font-medium text-right">{t("episode.typical")}</th>
                      <th className="px-4 py-2 font-medium text-right">{t("episode.range")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.lines.map((ln, i) => (
                      <tr key={i} className="border-b border-line last:border-0">
                        <td className="px-4 py-2.5 text-ink">
                          {lang === "hi" && ln.treatment.name_hi
                            ? ln.treatment.name_hi
                            : ln.treatment.name}
                        </td>
                        <td className="px-4 py-2.5 text-right text-ink-soft">{ln.quantity}</td>
                        <td className="px-4 py-2.5 text-right font-medium text-ink">
                          {formatINR(ln.line_avg)}
                        </td>
                        <td className="px-4 py-2.5 text-right text-ink-soft">
                          {formatINR(ln.line_min)}–{formatINR(ln.line_max)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr className="bg-primary-light/40 font-semibold text-ink">
                      <td className="px-4 py-3" colSpan={2}>
                        {t("episode.combinedTotal")}
                      </td>
                      <td className="px-4 py-3 text-right">{formatINR(result.totals.cost_avg)}</td>
                      <td className="px-4 py-3 text-right">
                        {formatINR(result.totals.cost_min)}–{formatINR(result.totals.cost_max)}
                      </td>
                    </tr>
                  </tfoot>
                </table>
              </div>
              <p className="text-[11px] text-ink-soft">{t("episode.confidenceNote")}</p>
            </>
          )}

          {result.skipped.length > 0 && (
            <div className="rounded-card border border-seal/40 bg-seal-light px-4 py-3 text-sm text-ink">
              <p className="font-medium">{t("episode.skippedTitle")}</p>
              <p className="text-xs mt-1">{t("episode.skippedNote")}</p>
              <ul className="list-disc pl-5 mt-1 text-xs">
                {result.skipped.map((s, i) => (
                  <li key={i}>
                    {s.treatment_id} × {s.quantity} — {s.reason}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.eligible_schemes.length > 0 && (
            <div className="rounded-card border border-line bg-surface p-5">
              <p className="font-display text-base font-semibold text-ink mb-1">
                {t("episode.schemesTitle")}
              </p>
              <p className="text-xs text-ink-soft mb-3">{t("episode.schemesNote")}</p>
              <ul className="flex flex-col gap-2">
                {result.eligible_schemes.map((s) => (
                  <li key={s.scheme_id} className="text-sm border border-line rounded-lg px-3 py-2">
                    <span className="font-medium text-ink">{s.name}</span>
                    <span className="text-ink-soft"> — {s.coverage_details}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <DisclaimerBanner text={result.disclaimer} />
        </div>
      )}

      <Link
        href="/"
        className="text-center text-sm text-primary font-medium underline underline-offset-2 print:hidden"
      >
        {t("results.startOver")}
      </Link>
    </div>
  );
}
