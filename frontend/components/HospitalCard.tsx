"use client";

import Link from "next/link";
import { HospitalOut } from "@/lib/types";
import { formatINR } from "@/lib/format";
import { useLanguage } from "@/lib/language-context";
import StampBadge from "./StampBadge";

export default function HospitalCard({ hospital }: { hospital: HospitalOut }) {
  const { t, hospitalTypeLabel } = useLanguage();
  const isGovt = hospital.type === "govt";

  return (
    <div
      className={`rounded-card border bg-surface p-4 shadow-card flex flex-col gap-2 ${
        isGovt ? "border-primary/40" : "border-line"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="font-display text-lg font-semibold text-ink leading-snug">{hospital.name}</h3>
          <p className="text-xs text-ink-soft mt-0.5">
            {hospitalTypeLabel(hospital.type)} · {hospital.city}, {hospital.state}
          </p>
        </div>
        {isGovt && <StampBadge label={t("hospitals.govtBadge")} />}
      </div>

      {hospital.empanelled_schemes.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {hospital.empanelled_schemes.map((s) => (
            <span
              key={s}
              className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-primary-light text-primary-dark"
            >
              {s} {t("hospitals.empanelled")}
            </span>
          ))}
        </div>
      )}

      <div className="perforated" />

      <div className="flex items-center justify-between">
        <div>
          <div className="text-[11px] uppercase tracking-wide text-ink-soft">
            {t("hospitals.typicalCostHere")}
          </div>
          {hospital.cost_avg != null ? (
            <div className="font-mono text-base font-bold text-ink">{formatINR(hospital.cost_avg)}</div>
          ) : (
            <div className="text-sm text-ink-soft italic">{t("hospitals.noData")}</div>
          )}
        </div>
        <div className="text-right text-xs text-ink-soft">
          <div>★ {hospital.basic_rating.toFixed(1)}</div>
          <div className="mt-1">{hospital.contact}</div>
        </div>
      </div>

      <Link
        href={`/hospitals/${hospital.id}`}
        className="text-sm text-primary font-medium underline underline-offset-2 w-fit"
      >
        {t("hospitalCard.viewDetails")} →
      </Link>
    </div>
  );
}
