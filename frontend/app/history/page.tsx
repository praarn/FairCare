"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { getHistory, clearHistory, HistoryEntry } from "@/lib/history";
import { useLanguage } from "@/lib/language-context";
import { useAuth } from "@/lib/auth-context";
import { getAuthToken } from "@/lib/token";
import { fetchSavedEstimates, deleteSavedEstimate } from "@/lib/api";
import { formatINR } from "@/lib/format";
import type { SavedEstimate } from "@/lib/types";

function DriftBadge({ drift }: { drift: SavedEstimate["drift"] }) {
  const { t } = useLanguage();
  if (!drift) return null;
  if (drift.direction === "flat") {
    return <span className="text-[11px] text-ink-soft">{t("history.driftFlat")}</span>;
  }
  const up = drift.direction === "up";
  return (
    <span className={`text-[11px] font-medium ${up ? "text-alert" : "text-primary-dark"}`}>
      {up ? "+" : ""}
      {drift.delta_pct}% · {up ? t("history.driftUp") : t("history.driftDown")}
    </span>
  );
}

export default function HistoryPage() {
  const { t } = useLanguage();
  const { user } = useAuth();
  const [entries, setEntries] = useState<HistoryEntry[]>([]);
  const [loaded, setLoaded] = useState(false);

  const [saved, setSaved] = useState<SavedEstimate[]>([]);
  const [savedLoaded, setSavedLoaded] = useState(false);

  const loadSaved = useCallback(async () => {
    const token = getAuthToken();
    if (!token) {
      setSavedLoaded(true);
      return;
    }
    try {
      setSaved(await fetchSavedEstimates(token));
    } catch {
      setSaved([]);
    } finally {
      setSavedLoaded(true);
    }
  }, []);

  useEffect(() => {
    setEntries(getHistory());
    setLoaded(true);
  }, []);

  useEffect(() => {
    if (user) void loadSaved();
    else setSavedLoaded(true);
  }, [user, loadSaved]);

  function handleClear() {
    clearHistory();
    setEntries([]);
  }

  async function handleDeleteSaved(id: string) {
    const token = getAuthToken();
    if (!token) return;
    setSaved((s) => s.filter((e) => e.id !== id));
    try {
      await deleteSavedEstimate(token, id);
    } catch {
      void loadSaved(); // resync on failure
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <p className="text-seal font-semibold text-sm uppercase tracking-wide mb-1">
            {t("history.eyebrow")}
          </p>
          <h1 className="font-display text-2xl sm:text-3xl font-semibold text-ink">
            {t("history.title")}
          </h1>
        </div>
      </div>

      {/* ---- saved to account ---- */}
      <section className="flex flex-col gap-3">
        <h2 className="font-display text-lg font-semibold text-ink">
          {t("history.savedSection")}
        </h2>

        {!user && <p className="text-sm text-ink-soft">{t("history.signInToSee")}</p>}

        {user && savedLoaded && saved.length === 0 && (
          <div className="rounded-card border border-line bg-surface p-5 text-center text-ink-soft text-sm">
            {t("history.empty")}
          </div>
        )}

        {user &&
          saved.map((e) => {
            const params = new URLSearchParams({ treatment_id: e.treatment_id });
            if (e.city) params.set("city", e.city);
            else if (e.state) params.set("state", e.state);
            if (e.hospital_type) params.set("hospital_type", e.hospital_type);
            return (
              <div
                key={e.id}
                className="rounded-card border border-line bg-surface p-4 shadow-card flex items-start justify-between gap-3"
              >
                <Link href={`/results?${params.toString()}`} className="flex-1">
                  <div className="font-medium text-ink">
                    {e.label || e.treatment_name}
                  </div>
                  <div className="text-xs text-ink-soft">
                    {e.label ? `${e.treatment_name} · ` : ""}
                    {e.city || e.state} · {formatINR(e.cost_avg)}{" "}
                    ({formatINR(e.cost_min)}–{formatINR(e.cost_max)})
                  </div>
                  {e.note && <div className="text-xs text-ink-soft mt-1 italic">{e.note}</div>}
                  <div className="mt-1">
                    <DriftBadge drift={e.drift} />
                  </div>
                </Link>
                <button
                  type="button"
                  onClick={() => handleDeleteSaved(e.id)}
                  className="text-xs text-ink-soft hover:text-alert underline underline-offset-2 shrink-0"
                >
                  {t("history.remove")}
                </button>
              </div>
            );
          })}
      </section>

      {/* ---- recently viewed on this device ---- */}
      <section className="flex flex-col gap-3">
        <div className="flex items-center justify-between gap-3">
          <h2 className="font-display text-lg font-semibold text-ink">
            {t("history.deviceSection")}
          </h2>
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
          <div className="rounded-card border border-line bg-surface p-5 text-center text-ink-soft text-sm">
            {t("history.empty")}
          </div>
        )}

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

        <p className="text-[11px] text-ink-soft">{t("history.storedLocally")}</p>
      </section>
    </div>
  );
}
