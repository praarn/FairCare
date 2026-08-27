"use client";

import { useCallback, useEffect, useState } from "react";
import TreatmentAutocomplete from "@/components/TreatmentAutocomplete";
import { CITIES, STATES, Treatment, Contribution } from "@/lib/types";
import { approveContribution, fetchContributions, rejectContribution } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { getAuthToken } from "@/lib/token";
import { useLanguage } from "@/lib/language-context";
import { formatINR } from "@/lib/format";

const TYPES = ["govt", "private_low", "private_mid", "private_high"];

type Overrides = {
  treatment: Treatment | null;
  city: string;
  state: string;
  hospital_type: string;
  cost_min: string;
  cost_max: string;
};

function blankOverrides(c: Contribution): Overrides {
  return {
    treatment: null,
    city: c.city || "",
    state: c.state || "",
    hospital_type: c.hospital_type || "",
    cost_min: "",
    cost_max: "",
  };
}

export default function ContributionReviewPage() {
  const { t, hospitalTypeLabel } = useLanguage();
  const { user } = useAuth();

  const [rows, setRows] = useState<Contribution[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [overrides, setOverrides] = useState<Record<string, Overrides>>({});
  const [busy, setBusy] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const load = useCallback(async () => {
    const token = getAuthToken();
    if (!token) {
      setLoaded(true);
      return;
    }
    try {
      const data = await fetchContributions(token, "pending");
      setRows(data);
      setOverrides(Object.fromEntries(data.map((c) => [c.id, blankOverrides(c)])));
    } catch {
      setRows([]);
    } finally {
      setLoaded(true);
    }
  }, []);

  useEffect(() => {
    if (user?.is_admin) void load();
    else setLoaded(true);
  }, [user, load]);

  if (user && !user.is_admin) {
    return <p className="text-ink-soft text-center py-10">{t("review.noAccess")}</p>;
  }
  if (!user) {
    return <p className="text-ink-soft text-center py-10">{t("review.noAccess")}</p>;
  }

  function patch(id: string, p: Partial<Overrides>) {
    setOverrides((o) => ({ ...o, [id]: { ...o[id], ...p } }));
  }

  async function doApprove(c: Contribution) {
    const o = overrides[c.id];
    setBusy(c.id);
    setErrors((e) => ({ ...e, [c.id]: "" }));
    try {
      const token = getAuthToken()!;
      await approveContribution(token, c.id, {
        treatment_id: o.treatment?.id || c.treatment_id || undefined,
        city: o.city || undefined,
        state: o.state || undefined,
        hospital_type: o.hospital_type || undefined,
        cost_min: o.cost_min ? Number(o.cost_min) : undefined,
        cost_max: o.cost_max ? Number(o.cost_max) : undefined,
      });
      setRows((r) => r.filter((x) => x.id !== c.id));
    } catch (err) {
      setErrors((e) => ({
        ...e,
        [c.id]: err instanceof Error ? err.message : t("review.actionFailed"),
      }));
    } finally {
      setBusy(null);
    }
  }

  async function doReject(c: Contribution) {
    setBusy(c.id);
    try {
      await rejectContribution(getAuthToken()!, c.id);
      setRows((r) => r.filter((x) => x.id !== c.id));
    } catch (err) {
      setErrors((e) => ({
        ...e,
        [c.id]: err instanceof Error ? err.message : t("review.actionFailed"),
      }));
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="font-display text-2xl sm:text-3xl font-semibold text-ink">
          {t("review.title")}
        </h1>
        <p className="text-ink-soft text-sm mt-1">{t("review.subtitle")}</p>
      </div>

      {loaded && rows.length === 0 && (
        <div className="rounded-card border border-line bg-surface p-6 text-center text-ink-soft">
          {t("review.empty")}
        </div>
      )}

      {rows.map((c) => {
        const o = overrides[c.id];
        if (!o) return null;
        return (
          <div key={c.id} className="rounded-card border border-line bg-surface p-5 shadow-card flex flex-col gap-3">
            <div className="flex items-baseline justify-between gap-3">
              <span className="font-display text-lg font-semibold text-ink">
                {t("review.amount")}: {formatINR(c.amount)}
              </span>
              <span className="text-xs text-ink-soft font-mono">{c.id}</span>
            </div>

            {c.hospital_name && (
              <p className="text-sm text-ink-soft">{c.hospital_name}</p>
            )}
            {c.source_note && (
              <p className="text-sm text-ink-soft">
                <span className="font-medium">{t("review.submittedNote")}: </span>
                {c.source_note}
              </p>
            )}
            {c.line_items.length > 0 && (
              <ul className="text-xs text-ink-soft border border-line rounded-lg px-3 py-2">
                {c.line_items.map((li, i) => (
                  <li key={i} className="flex justify-between gap-3">
                    <span className="truncate">{li.description || "—"}</span>
                    <span className="font-mono">
                      {li.amount != null ? formatINR(li.amount) : "—"}
                    </span>
                  </li>
                ))}
              </ul>
            )}

            <div className="border-t border-line pt-3 flex flex-col gap-3">
              {!c.treatment_id && (
                <div>
                  <label className="block text-xs font-medium text-ink-soft mb-1">
                    {t("review.pickTreatment")}
                  </label>
                  <TreatmentAutocomplete onSelect={(tr) => patch(c.id, { treatment: tr })} />
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <label className="text-xs font-medium text-ink-soft flex flex-col gap-1">
                  {t("review.city")}
                  <select
                    value={o.city}
                    onChange={(e) => patch(c.id, { city: e.target.value })}
                    className="rounded-card border border-line bg-surface px-3 py-2 text-sm text-ink"
                  >
                    <option value="">—</option>
                    {CITIES.map((x) => (
                      <option key={x} value={x}>{x}</option>
                    ))}
                  </select>
                </label>
                <label className="text-xs font-medium text-ink-soft flex flex-col gap-1">
                  {t("review.state")}
                  <select
                    value={o.state}
                    onChange={(e) => patch(c.id, { state: e.target.value })}
                    className="rounded-card border border-line bg-surface px-3 py-2 text-sm text-ink"
                  >
                    <option value="">—</option>
                    {STATES.map((x) => (
                      <option key={x} value={x}>{x}</option>
                    ))}
                  </select>
                </label>
                <label className="text-xs font-medium text-ink-soft flex flex-col gap-1">
                  {t("review.hospitalType")}
                  <select
                    value={o.hospital_type}
                    onChange={(e) => patch(c.id, { hospital_type: e.target.value })}
                    className="rounded-card border border-line bg-surface px-3 py-2 text-sm text-ink"
                  >
                    <option value="">—</option>
                    {TYPES.map((x) => (
                      <option key={x} value={x}>{hospitalTypeLabel(x)}</option>
                    ))}
                  </select>
                </label>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <label className="text-xs font-medium text-ink-soft flex flex-col gap-1">
                  {t("review.costMin")}
                  <input
                    type="number"
                    value={o.cost_min}
                    onChange={(e) => patch(c.id, { cost_min: e.target.value })}
                    className="rounded-card border border-line bg-surface px-3 py-2 text-sm text-ink"
                  />
                </label>
                <label className="text-xs font-medium text-ink-soft flex flex-col gap-1">
                  {t("review.costMax")}
                  <input
                    type="number"
                    value={o.cost_max}
                    onChange={(e) => patch(c.id, { cost_max: e.target.value })}
                    className="rounded-card border border-line bg-surface px-3 py-2 text-sm text-ink"
                  />
                </label>
              </div>

              {errors[c.id] && (
                <p className="text-xs text-alert font-medium">{errors[c.id]}</p>
              )}

              <div className="flex gap-3">
                <button
                  type="button"
                  disabled={busy === c.id}
                  onClick={() => doApprove(c)}
                  className="rounded-card bg-primary hover:bg-primary-dark text-white font-semibold text-sm px-5 py-2 transition-colors disabled:opacity-60"
                >
                  {t("review.approve")}
                </button>
                <button
                  type="button"
                  disabled={busy === c.id}
                  onClick={() => doReject(c)}
                  className="rounded-card border border-alert/50 text-alert hover:bg-alert-light font-semibold text-sm px-5 py-2 transition-colors disabled:opacity-60"
                >
                  {t("review.reject")}
                </button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
