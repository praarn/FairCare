"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getHistory, clearHistory, HistoryEntry } from "@/lib/history";
import { useLanguage } from "@/lib/language-context";

export default function HistoryPage() {
  const { t } = useLanguage();
  const [entries, setEntries] = useState<HistoryEntry[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    setEntries(getHistory());
    setLoaded(true);
  }, []);

  function handleClear() {
    clearHistory();
    setEntries([]);
  }

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <p className="text-seal font-semibold text-sm uppercase tracking-wide mb-1">
            {t("history.eyebrow")}
          </p>
          <h1 className="font-display text-2xl sm:text-3xl font-semibold text-ink">
            {t("history.title")}
          </h1>
        </div>
        {entries.length > 0 && (
          <button
            type="button"
            onClick={handleClear}
            className="text-sm text-alert font-medium underline underline-offset-2"
          >
            {t("history.clear")}
          </button>
        )}
      </div>

      {loaded && entries.length === 0 && (
        <div className="rounded-card border border-line bg-surface p-6 text-center text-ink-soft">
          {t("history.empty")}
        </div>
      )}

      {entries.length > 0 && (
        <div className="flex flex-col gap-3">
          {entries.map((e, i) => {
            const params = new URLSearchParams({ treatment_id: e.treatment_id, city: e.city });
            if (e.hospital_type) params.set("hospital_type", e.hospital_type);
            return (
              <Link
                key={i}
                href={`/results?${params.toString()}`}
                className="rounded-card border border-line bg-surface p-4 shadow-card flex items-center justify-between gap-3 hover:border-primary/50 transition-colors"
              >
                <div>
                  <div className="font-medium text-ink">{e.treatment_name}</div>
                  <div className="text-xs text-ink-soft">{e.city}</div>
                </div>
                <div className="text-xs text-ink-soft shrink-0">
                  {new Date(e.viewed_at).toLocaleDateString()}
                </div>
              </Link>
            );
          })}
        </div>
      )}

      <p className="text-[11px] text-ink-soft">{t("history.storedLocally")}</p>
    </div>
  );
}
