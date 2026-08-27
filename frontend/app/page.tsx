"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import TreatmentAutocomplete from "@/components/TreatmentAutocomplete";
import DisclaimerBanner from "@/components/DisclaimerBanner";
import FeatureCard from "@/components/FeatureCard";
import { Treatment, CITIES, STATES } from "@/lib/types";
import { useLanguage } from "@/lib/language-context";

const ICON_PROPS = { width: 18, height: 18, viewBox: "0 0 24 24", fill: "none" as const };

const OTHER_CITY = "__OTHER__";

export default function HomePage() {
  const router = useRouter();
  const { t, hospitalTypeLabel } = useLanguage();
  const [treatment, setTreatment] = useState<Treatment | null>(null);
  const [city, setCity] = useState<string>(CITIES[0]);
  const [state, setState] = useState<string>("Delhi");
  const [hospitalType, setHospitalType] = useState("");
  const [error, setError] = useState<string | null>(null);

  const cityNotListed = city === OTHER_CITY;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!treatment) {
      setError(t("home.pickTreatmentError"));
      return;
    }
    setError(null);
    const params = new URLSearchParams({ treatment_id: treatment.id });
    if (cityNotListed) {
      params.set("state", state);
    } else {
      params.set("city", city);
    }
    if (hospitalType) params.set("hospital_type", hospitalType);
    router.push(`/results?${params.toString()}`);
  }

  return (
    <div className="flex flex-col gap-10">
      <section className="relative overflow-hidden">
        {/* Subtle decorative flourish behind the hero text — kept low-key
            to match the rate-card aesthetic rather than looking like a
            generic gradient hero. */}
        <div
          aria-hidden
          className="absolute -top-24 -right-24 w-72 h-72 rounded-full bg-primary/10 blur-3xl -z-10"
        />
        <div
          aria-hidden
          className="absolute top-10 -left-16 w-56 h-56 rounded-full bg-seal/10 blur-3xl -z-10"
        />

        <p className="text-seal font-semibold text-sm uppercase tracking-wide mb-2">
          {t("home.eyebrow")}
        </p>
        <h1 className="font-display text-3xl sm:text-4xl font-semibold text-ink leading-tight">
          {t("home.title")}
        </h1>
        <p className="mt-3 text-ink-soft text-base leading-relaxed max-w-xl">
          {t("home.subtitle")}
        </p>
      </section>

      <form
        onSubmit={handleSubmit}
        className="rounded-card border border-line bg-surface p-5 sm:p-6 shadow-card flex flex-col gap-5"
      >
        <TreatmentAutocomplete onSelect={setTreatment} />

        <div>
          <label htmlFor="city-select" className="block text-sm font-medium text-ink mb-1.5">
            {t("home.cityLabel")}
          </label>
          <select
            id="city-select"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            className="w-full rounded-card border border-line bg-surface px-4 py-3 text-base text-ink focus:border-primary"
          >
            {CITIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
            <option value={OTHER_CITY}>{t("home.cityNotListed")}</option>
          </select>

          {cityNotListed && (
            <div className="mt-3">
              <label htmlFor="state-select" className="block text-sm font-medium text-ink mb-1.5">
                {t("home.stateLabel")}
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
              <p className="text-xs text-ink-soft mt-1.5">{t("home.stateHint")}</p>
            </div>
          )}
        </div>

        <div>
          <label htmlFor="type-select" className="block text-sm font-medium text-ink mb-1.5">
            {t("home.hospitalTypeLabel")} <span className="text-ink-soft font-normal">{t("home.optional")}</span>
          </label>
          <select
            id="type-select"
            value={hospitalType}
            onChange={(e) => setHospitalType(e.target.value)}
            className="w-full rounded-card border border-line bg-surface px-4 py-3 text-base text-ink focus:border-primary"
          >
            <option value="">{t("home.anyRange")}</option>
            {["govt", "private_low", "private_mid", "private_high"].map((value) => (
              <option key={value} value={value}>{hospitalTypeLabel(value)}</option>
            ))}
          </select>
        </div>

        {error && <p className="text-sm text-alert font-medium">{error}</p>}

        <button
          type="submit"
          className="w-full rounded-card bg-primary hover:bg-primary-dark text-white font-semibold text-base py-3.5 transition-colors"
        >
          {t("home.submit")}
        </button>
      </form>

      <DisclaimerBanner />

      <section>
        <h2 className="font-display text-lg font-semibold text-ink mb-3">{t("home.moreTools")}</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <FeatureCard
            href="/compare"
            accent="primary"
            title={t("nav.compare")}
            description={t("home.cardCompareDesc")}
            icon={
              <svg {...ICON_PROPS} aria-hidden>
                <path d="M7 20V10M12 20V4M17 20v-7" stroke="currentColor" strokeWidth={2} strokeLinecap="round" />
              </svg>
            }
          />
          <FeatureCard
            href="/eligibility"
            accent="seal"
            title={t("nav.eligibility")}
            description={t("home.cardEligibilityDesc")}
            icon={
              <svg {...ICON_PROPS} aria-hidden>
                <path
                  d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6l7-3Z"
                  stroke="currentColor"
                  strokeWidth={2}
                  strokeLinejoin="round"
                />
                <path d="M9 12l2 2 4-4" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            }
          />
          <FeatureCard
            href="/symptom-checker"
            accent="alert"
            title={t("nav.symptomChecker")}
            description={t("home.cardSymptomDesc")}
            icon={
              <svg {...ICON_PROPS} aria-hidden>
                <path
                  d="M4 12h3l2 5 4-10 2 5h5"
                  stroke="currentColor"
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            }
          />
          <FeatureCard
            href="/history"
            accent="primary"
            title={t("nav.history")}
            description={t("home.cardHistoryDesc")}
            icon={
              <svg {...ICON_PROPS} aria-hidden>
                <circle cx="12" cy="12" r="8" stroke="currentColor" strokeWidth={2} />
                <path d="M12 8v4l3 2" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            }
          />
          <FeatureCard
            href="/episode"
            accent="seal"
            title={t("nav.episode")}
            description={t("home.cardEpisodeDesc")}
            icon={
              <svg {...ICON_PROPS} aria-hidden>
                <path d="M4 7h16M4 12h16M4 17h10" stroke="currentColor" strokeWidth={2} strokeLinecap="round" />
              </svg>
            }
          />
          <FeatureCard
            href="/methodology"
            accent="seal"
            title={t("nav.methodology")}
            description={t("home.cardMethodologyDesc")}
            icon={
              <svg {...ICON_PROPS} aria-hidden>
                <path d="M6 3h9l3 3v15H6V3Z" stroke="currentColor" strokeWidth={2} strokeLinejoin="round" />
                <path d="M9 12h6M9 16h6M9 8h3" stroke="currentColor" strokeWidth={2} strokeLinecap="round" />
              </svg>
            }
          />
        </div>
      </section>
    </div>
  );
}
