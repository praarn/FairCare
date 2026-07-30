import Link from "next/link";
import { cookies } from "next/headers";
import { predictCost } from "@/lib/api";
import { formatINR } from "@/lib/format";
import CostGauge from "@/components/CostGauge";
import ConfidenceBadge from "@/components/ConfidenceBadge";
import DisclaimerBanner from "@/components/DisclaimerBanner";
import PaymentPlanEstimator from "@/components/PaymentPlanEstimator";
import CostOfCareBreakdown from "@/components/CostOfCareBreakdown";
import PriceCheckTool from "@/components/PriceCheckTool";
import InsuranceCoverageEstimator from "@/components/InsuranceCoverageEstimator";
import RecordHistory from "@/components/RecordHistory";
import ShareEstimate from "@/components/ShareEstimate";
import ReadAloudButton from "@/components/ReadAloudButton";
import { t, hospitalTypeLabel, parseLang } from "@/lib/i18n";

export default async function ResultsPage({
  searchParams,
}: {
  searchParams: Promise<{ treatment_id?: string; city?: string; state?: string; hospital_type?: string }>;
}) {
  const { treatment_id, city, state, hospital_type } = await searchParams;
  const cookieStore = await cookies();
  const lang = parseLang(cookieStore.get("sahaj_lang")?.value);

  if (!treatment_id || (!city && !state)) {
    return (
      <div className="rounded-card border border-line bg-surface p-6 text-center">
        <p className="text-ink-soft">{t(lang, "results.missing")}</p>
        <Link href="/" className="text-primary font-medium underline mt-2 inline-block">
          {t(lang, "results.startOver")}
        </Link>
      </div>
    );
  }

  let data;
  let notFound = false;
  try {
    data = await predictCost({ treatment_id, city, state, hospital_type: hospital_type || undefined, lang });
  } catch {
    notFound = true;
  }

  if (notFound || !data) {
    return (
      <div className="rounded-card border border-line bg-surface p-6 text-center flex flex-col gap-3">
        <p className="text-ink font-medium">{t(lang, "results.notEnough")}</p>
        <p className="text-ink-soft text-sm">{t(lang, "results.notEnoughSub")}</p>
        <Link href="/" className="text-primary font-medium underline">
          {t(lang, "results.backToSearch")}
        </Link>
      </div>
    );
  }

  const locationLabel = data.city || data.state || "";

  const hospitalParams = new URLSearchParams({ treatment_id });
  if (city) hospitalParams.set("city", city);
  if (hospital_type) hospitalParams.set("type", hospital_type);

  const treatmentName = lang === "hi" && data.treatment.name_hi ? data.treatment.name_hi : data.treatment.name;
  const treatmentCategory =
    lang === "hi" && data.treatment.category_hi ? data.treatment.category_hi : data.treatment.category;

  const confidenceKey =
    data.estimate.confidence_label === "high"
      ? "confidence.high"
      : data.estimate.confidence_label === "medium"
      ? "confidence.medium"
      : "confidence.low";

  const whatsappText = [
    `${t(lang, "share.whatsappTextIntro")} ${treatmentName}${locationLabel ? ` (${locationLabel})` : ""}`,
    `${t(lang, "share.whatsappTextTypical")}: ${formatINR(data.estimate.cost_avg)}`,
    `${t(lang, "share.whatsappTextRange")}: ${formatINR(data.estimate.cost_min)} - ${formatINR(data.estimate.cost_max)}`,
    t(lang, "share.whatsappTextVia"),
  ].join("\n");

  const readAloudText = [
    `${treatmentName}${locationLabel ? `, ${locationLabel}` : ""}.`,
    `${t(lang, "readAloud.typicalCostIs")} ${formatINR(data.estimate.cost_avg)},`,
    `${t(lang, "readAloud.rangeIs")} ${formatINR(data.estimate.cost_min)} ${t(lang, "readAloud.to")} ${formatINR(data.estimate.cost_max)}.`,
    `${t(lang, "readAloud.confidenceIs")} ${t(lang, confidenceKey)}.`,
  ].join(" ");

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <p className="text-seal font-semibold text-sm uppercase tracking-wide mb-1">
            {treatmentCategory}
          </p>
          <h1 className="font-display text-2xl sm:text-3xl font-semibold text-ink">
            {treatmentName}{locationLabel ? ` · ${locationLabel}` : ""}
          </h1>
          <p className="text-ink-soft text-sm mt-1">
            {hospital_type ? hospitalTypeLabel(lang, hospital_type) : t(lang, "results.allTypes")} ·{" "}
            {data.treatment.typical_duration}
          </p>
        </div>
        <div className="print:hidden">
          <ReadAloudButton text={readAloudText} />
        </div>
      </div>

      {data.estimate.is_fallback && (
        <div className="rounded-card border border-seal/40 bg-seal-light px-4 py-3 text-sm text-ink">
          {data.estimate.fallback_reason}
        </div>
      )}

      <div className="rounded-card border border-line bg-surface p-5 sm:p-6 shadow-card flex flex-col items-center gap-4">
        <ConfidenceBadge estimate={data.estimate} />
        <CostGauge estimate={data.estimate} />
      </div>

      <details className="rounded-card border border-line bg-surface p-5 group">
        <summary className="cursor-pointer font-display text-lg font-semibold text-ink list-none flex items-center justify-between">
          {t(lang, "results.whyThisEstimate")}
          <span className="text-primary text-sm group-open:rotate-180 transition-transform">▾</span>
        </summary>
        <ul className="mt-4 flex flex-col gap-3">
          {data.factors.map((f, i) => (
            <li key={i} className="text-sm text-ink-soft">
              <span className="font-medium text-ink">{f.label}: </span>
              {f.detail}
            </li>
          ))}
        </ul>

        <div className="perforated" />

        <p className="text-xs uppercase tracking-wide text-ink-soft font-semibold mb-2">
          {t(lang, "results.dataSources")}
        </p>
        <ul className="flex flex-col gap-2">
          {data.sources.map((s) => (
            <li key={s.id} className="text-xs text-ink-soft border border-line rounded-lg px-3 py-2">
              {s.city && <span className="font-mono">{s.city}</span>}
              {s.city && " · "}
              {hospitalTypeLabel(lang, s.hospital_type)} ·{" "}
              {s.sample_size} records ({s.data_year}) — {s.source}
            </li>
          ))}
        </ul>
      </details>

      <DisclaimerBanner text={data.disclaimer} />

      <ShareEstimate whatsappText={whatsappText} />

      <div className="print:hidden flex flex-col gap-6">
        <PaymentPlanEstimator amount={data.estimate.cost_avg} />

        <CostOfCareBreakdown procedureCost={data.estimate.cost_avg} />

        <InsuranceCoverageEstimator procedureCost={data.estimate.cost_avg} />

        <PriceCheckTool costMin={data.estimate.cost_min} costMax={data.estimate.cost_max} />

        {city && (
          <Link
            href={`/hospitals?${hospitalParams.toString()}`}
            className="w-full text-center rounded-card bg-primary hover:bg-primary-dark text-white font-semibold text-base py-3.5 transition-colors"
          >
            {t(lang, "results.seeHospitals")}
          </Link>
        )}

        <Link
          href="/compare"
          className="text-center text-sm text-primary font-medium underline underline-offset-2"
        >
          {t(lang, "results.compareLink")}
        </Link>
      </div>

      <RecordHistory
        treatmentId={treatment_id}
        treatmentName={treatmentName}
        city={locationLabel}
        hospitalType={hospital_type}
      />
    </div>
  );
}
