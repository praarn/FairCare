"use client";

import { useState } from "react";
import TreatmentAutocomplete from "@/components/TreatmentAutocomplete";
import ConfidenceBadge from "@/components/ConfidenceBadge";
import DisclaimerBanner from "@/components/DisclaimerBanner";
import { predictCost } from "@/lib/api";
import { Treatment, CITIES, PredictCostResponse } from "@/lib/types";
import { formatINR } from "@/lib/format";
import { useLanguage } from "@/lib/language-context";

type Row = {
  city: string;
  data: PredictCostResponse | null;
};

const HOSPITAL_TYPES = ["govt", "private_low", "private_mid", "private_high"];

export default function ComparePage() {
  const { t, lang, hospitalTypeLabel } = useLanguage();
  const [treatment, setTreatment] = useState<Treatment | null>(null);
  const [selectedCities, setSelectedCities] = useState<string[]>(CITIES.slice(0, 4));
  const [hospitalType, setHospitalType] = useState("");
  const [rows, setRows] = useState<Row[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function toggleCity(city: string) {
    setSelectedCities((prev) =>
      prev.includes(city) ? prev.filter((c) => c !== city) : [...prev, city]
    );
  }

  async function handleCompare(e: React.FormEvent) {
    e.preventDefault();
    if (!treatment) {
      setError(t("compare.pickTreatment"));
      return;
    }
    if (selectedCities.length < 2) {
      setError(t("compare.pickTwoCities"));
      return;
    }
    setError(null);
    setLoading(true);
    setRows(null);

    const results = await Promise.all(
      selectedCities.map(async (city): Promise<Row> => {
        try {
          const data = await predictCost({
            treatment_id: treatment.id,
            city,
            hospital_type: hospitalType || undefined,
            lang,
          });
          return { city, data };
        } catch {
          return { city, data: null };
        }
      })
    );

    results.sort((a, b) => {
      if (!a.data && !b.data) return 0;
      if (!a.data) return 1;
      if (!b.data) return -1;
      return a.data.estimate.cost_avg - b.data.estimate.cost_avg;
    });

    setRows(results);
    setLoading(false);
  }

  const cheapestCity = rows?.find((r) => r.data)?.city;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <p className="text-seal font-semibold text-sm uppercase tracking-wide mb-2">
          {t("compare.eyebrow")}
        </p>
        <h1 className="font-display text-3xl sm:text-4xl font-semibold text-ink leading-tight">
          {t("compare.title")}
        </h1>
        <p className="mt-2 text-ink-soft text-base max-w-xl">{t("compare.subtitle")}</p>
      </div>

      <form
        onSubmit={handleCompare}
        className="rounded-card border border-line bg-surface p-5 sm:p-6 shadow-card flex flex-col gap-5"
      >
        <TreatmentAutocomplete onSelect={setTreatment} />

        <div>
          <label htmlFor="compare-type-select" className="block text-sm font-medium text-ink mb-1.5">
            {t("compare.hospitalTypeLabel")} <span className="text-ink-soft font-normal">{t("home.optional")}</span>
          </label>
          <select
            id="compare-type-select"
            value={hospitalType}
            onChange={(e) => setHospitalType(e.target.value)}
            className="w-full rounded-card border border-line bg-surface px-4 py-3 text-base text-ink focus:border-primary"
          >
            <option value="">{t("home.anyRange")}</option>
            {HOSPITAL_TYPES.map((value) => (
              <option key={value} value={value}>{hospitalTypeLabel(value)}</option>
            ))}
          </select>
        </div>

        <div>
          <p className="text-sm font-medium text-ink mb-2">{t("compare.citiesLabel")}</p>
          <div className="flex flex-wrap gap-2">
            {CITIES.map((c) => (
              <button
                type="button"
                key={c}
                onClick={() => toggleCity(c)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
                  selectedCities.includes(c)
                    ? "bg-primary text-white border-primary"
                    : "border-line text-ink-soft hover:border-primary/50"
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        {error && <p className="text-sm text-alert font-medium">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-card bg-primary hover:bg-primary-dark disabled:opacity-60 text-white font-semibold text-base py-3.5 transition-colors"
        >
          {loading ? t("compare.comparing") : t("compare.submit")}
        </button>
      </form>

      {rows && (
        <div className="flex flex-col gap-3">
          {rows.map((row) => (
            <div
              key={row.city}
              className={`rounded-card border bg-surface p-4 shadow-card flex items-center justify-between gap-3 ${
                row.city === cheapestCity ? "border-primary" : "border-line"
              }`}
            >
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <h3 className="font-display text-lg font-semibold text-ink">{row.city}</h3>
                  {row.city === cheapestCity && (
                    <span className="text-[11px] font-semibold uppercase tracking-wide text-primary bg-primary-light px-2 py-0.5 rounded-full">
                      {t("compare.lowestCost")}
                    </span>
                  )}
                </div>
                {row.data ? (
                  <>
                    {row.data.estimate.is_fallback && (
                      <p className="text-xs text-seal mt-0.5">{row.data.estimate.fallback_reason}</p>
                    )}
                    <div className="mt-1.5">
                      <ConfidenceBadge estimate={row.data.estimate} />
                    </div>
                  </>
                ) : (
                  <p className="text-sm text-ink-soft italic mt-1">{t("compare.noDataCity")}</p>
                )}
              </div>
              {row.data && (
                <div className="text-right shrink-0">
                  <div className="font-mono text-xl font-bold text-ink">
                    {formatINR(row.data.estimate.cost_avg)}
                  </div>
                  <div className="text-xs text-ink-soft">
                    {formatINR(row.data.estimate.cost_min)} – {formatINR(row.data.estimate.cost_max)}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <DisclaimerBanner text={t("compare.disclaimer")} />
    </div>
  );
}
