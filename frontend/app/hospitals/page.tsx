import Link from "next/link";
import { cookies } from "next/headers";
import { fetchHospitals } from "@/lib/api";
import HospitalCard from "@/components/HospitalCard";
import DisclaimerBanner from "@/components/DisclaimerBanner";
import { t, parseLang } from "@/lib/i18n";

export default async function HospitalsPage({
  searchParams,
}: {
  searchParams: Promise<{ treatment_id?: string; city?: string; type?: string; budget_mode?: string }>;
}) {
  const { treatment_id, city, type, budget_mode } = await searchParams;
  const isBudgetMode = budget_mode === "true";
  const cookieStore = await cookies();
  const lang = parseLang(cookieStore.get("faircare_lang")?.value);

  if (!treatment_id) {
    return (
      <div className="rounded-card border border-line bg-surface p-6 text-center">
        <p className="text-ink-soft">{t(lang, "hospitals.missing")}</p>
        <Link href="/" className="text-primary font-medium underline mt-2 inline-block">
          {t(lang, "results.startOver")}
        </Link>
      </div>
    );
  }

  const hospitals = await fetchHospitals({ treatment_id, city, type, budget_mode: isBudgetMode });

  const baseParams = new URLSearchParams();
  baseParams.set("treatment_id", treatment_id);
  if (city) baseParams.set("city", city);
  if (type) baseParams.set("type", type);

  const recommendedParams = new URLSearchParams(baseParams);
  const budgetParams = new URLSearchParams(baseParams);
  budgetParams.set("budget_mode", "true");

  return (
    <div className="flex flex-col gap-5">
      <div>
        <p className="text-seal font-semibold text-sm uppercase tracking-wide mb-1">
          {t(lang, "hospitals.eyebrow")}
        </p>
        <h1 className="font-display text-2xl sm:text-3xl font-semibold text-ink">
          {t(lang, "hospitals.title")} {city ? `· ${city}` : `· ${t(lang, "hospitals.offeringTreatment")}`}
        </h1>
      </div>

      <div className="flex gap-2">
        <Link
          href={`/hospitals?${recommendedParams.toString()}`}
          className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
            !isBudgetMode
              ? "bg-primary text-white border-primary"
              : "border-line text-ink-soft hover:border-primary/50"
          }`}
        >
          {t(lang, "hospitals.recommended")}
        </Link>
        <Link
          href={`/hospitals?${budgetParams.toString()}`}
          className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
            isBudgetMode
              ? "bg-primary text-white border-primary"
              : "border-line text-ink-soft hover:border-primary/50"
          }`}
        >
          {t(lang, "hospitals.budgetMode")}
        </Link>
      </div>

      {hospitals.length === 0 ? (
        <div className="rounded-card border border-line bg-surface p-6 text-center text-ink-soft">
          {t(lang, "hospitals.none")}
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {hospitals.map((h) => (
            <HospitalCard key={h.id} hospital={h} />
          ))}
        </div>
      )}

      <DisclaimerBanner text={t(lang, "hospitals.disclaimer")} />
    </div>
  );
}
