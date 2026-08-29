import Link from "next/link";
import { cookies } from "next/headers";
import { fetchHospitalById } from "@/lib/api";
import { t, hospitalTypeLabel, parseLang } from "@/lib/i18n";
import StampBadge from "@/components/StampBadge";

export default async function HospitalDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const cookieStore = await cookies();
  const lang = parseLang(cookieStore.get("faircare_lang")?.value);

  let hospital;
  try {
    hospital = await fetchHospitalById(id);
  } catch {
    return (
      <div className="rounded-card border border-line bg-surface p-6 text-center">
        <p className="text-ink-soft">{t(lang, "hospitals.missing")}</p>
        <Link href="/" className="text-primary font-medium underline mt-2 inline-block">
          {t(lang, "results.startOver")}
        </Link>
      </div>
    );
  }

  const isGovt = hospital.type === "govt";
  const delta = 0.02;
  const bbox = [
    hospital.lng - delta,
    hospital.lat - delta,
    hospital.lng + delta,
    hospital.lat + delta,
  ].join(",");
  const mapSrc = `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&marker=${hospital.lat},${hospital.lng}&layer=mapnik`;

  return (
    <div className="flex flex-col gap-5">
      <Link href="/" className="text-sm text-primary font-medium underline underline-offset-2 w-fit">
        {t(lang, "hospitalDetail.back")}
      </Link>

      <div>
        <div className="flex items-start justify-between gap-2 flex-wrap">
          <h1 className="font-display text-2xl sm:text-3xl font-semibold text-ink">
            {hospital.name}
          </h1>
          {isGovt && <StampBadge label={t(lang, "hospitals.govtBadge")} />}
        </div>
        <p className="text-ink-soft text-sm mt-1">
          {hospitalTypeLabel(lang, hospital.type)} · {hospital.city}, {hospital.state}
        </p>
      </div>

      <div className="rounded-card border border-line overflow-hidden shadow-card">
        <iframe
          title="Hospital location map"
          src={mapSrc}
          className="w-full h-64 sm:h-80 border-0"
          loading="lazy"
        />
      </div>
      <p className="text-[11px] text-ink-soft -mt-3">{t(lang, "hospitalDetail.mapNote")}</p>

      <div className="rounded-card border border-line bg-surface p-5 shadow-card flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-ink-soft">{t(lang, "hospitalDetail.contact")}</span>
          <span className="font-mono text-sm text-ink">{hospital.contact}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm text-ink-soft">{t(lang, "hospitalDetail.rating")}</span>
          <span className="text-sm text-ink">★ {hospital.basic_rating.toFixed(1)}</span>
        </div>

        <div className="perforated" />

        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-ink-soft mb-2">
            {t(lang, "hospitalDetail.schemesTitle")}
          </p>
          {hospital.empanelled_schemes.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {hospital.empanelled_schemes.map((s) => (
                <span
                  key={s}
                  className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-primary-light text-primary-dark"
                >
                  {s}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-sm text-ink-soft italic">{t(lang, "hospitalDetail.noSchemes")}</p>
          )}
        </div>
      </div>
    </div>
  );
}
