"use client";

import { useEffect, useRef, useState } from "react";
import { formatINR } from "@/lib/format";
import { useLanguage } from "@/lib/language-context";
import { analyzeBill, multimodalStatus, submitContribution } from "@/lib/api";
import { getAuthToken } from "@/lib/token";
import type { BillLineItem } from "@/lib/types";

export default function PriceCheckTool({
  costMin,
  costMax,
  treatmentId,
  city,
}: {
  costMin: number;
  costMax: number;
  treatmentId?: string;
  city?: string;
}) {
  const { t, lang } = useLanguage();
  const [quote, setQuote] = useState("");
  const [checked, setChecked] = useState<number | null>(null);

  // ----- bill photo (multimodal, optional) -----
  const [visionOn, setVisionOn] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [billItems, setBillItems] = useState<BillLineItem[] | null>(null);
  const [billError, setBillError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement | null>(null);

  // ----- optional: contribute this bill's amount back -----
  const [billTotal, setBillTotal] = useState<number | null>(null);
  const [billHospitalName, setBillHospitalName] = useState<string | null>(null);
  const [contributeState, setContributeState] = useState<
    "idle" | "sending" | "done" | "error"
  >("idle");

  useEffect(() => {
    let cancelled = false;
    multimodalStatus()
      .then((s) => !cancelled && setVisionOn(s.vision))
      .catch(() => !cancelled && setVisionOn(false));
    return () => {
      cancelled = true;
    };
  }, []);

  function handleCheck(e: React.FormEvent) {
    e.preventDefault();
    const value = Number(quote);
    if (!quote || Number.isNaN(value)) return;
    setChecked(value);
  }

  async function handleBillFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    e.target.value = ""; // allow re-selecting the same file
    if (!file) return;
    setAnalyzing(true);
    setBillError(null);
    setBillItems(null);
    setBillTotal(null);
    setBillHospitalName(null);
    setContributeState("idle");
    try {
      const res = await analyzeBill(file, { city, treatment_id: treatmentId, lang });
      const total = res.effective_total ?? res.extracted.total_amount;
      setBillItems(res.extracted.line_items ?? []);
      setBillHospitalName(res.extracted.hospital_name ?? null);
      if (total != null) {
        setQuote(String(total));
        setChecked(total);
        setBillTotal(total);
      }
    } catch {
      setBillError(t("priceCheck.uploadFailed"));
    } finally {
      setAnalyzing(false);
    }
  }

  async function handleContribute() {
    if (billTotal == null) return;
    setContributeState("sending");
    try {
      await submitContribution(
        {
          amount: billTotal,
          treatment_id: treatmentId,
          city,
          hospital_name: billHospitalName ?? undefined,
          line_items: billItems ?? undefined,
        },
        getAuthToken() ?? undefined
      );
      setContributeState("done");
    } catch {
      setContributeState("error");
    }
  }

  let verdict: "within" | "below" | "above" | null = null;
  if (checked != null) {
    if (checked < costMin) verdict = "below";
    else if (checked > costMax) verdict = "above";
    else verdict = "within";
  }

  const VERDICT_STYLE: Record<string, string> = {
    within: "border-primary/40 bg-primary-light text-primary-dark",
    below: "border-seal/40 bg-seal-light text-ink",
    above: "border-alert/40 bg-alert-light text-alert",
  };

  return (
    <div className="rounded-card border border-line bg-surface p-5 sm:p-6 shadow-card flex flex-col gap-4">
      <div>
        <h3 className="font-display text-lg font-semibold text-ink">{t("priceCheck.title")}</h3>
        <p className="text-xs text-ink-soft mt-1">{t("priceCheck.subtitle")}</p>
      </div>

      <form onSubmit={handleCheck} className="flex gap-2">
        <input
          type="number"
          min={0}
          placeholder={t("priceCheck.placeholder")}
          value={quote}
          onChange={(e) => {
            setQuote(e.target.value);
            setChecked(null);
          }}
          className="flex-1 rounded-card border border-line bg-surface px-4 py-2.5 text-base text-ink focus:border-primary"
        />
        <button
          type="submit"
          className="shrink-0 rounded-card bg-primary hover:bg-primary-dark text-white font-semibold px-5 py-2.5 transition-colors"
        >
          {t("priceCheck.check")}
        </button>
      </form>

      {visionOn && (
        <div>
          <input
            ref={fileRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            capture="environment"
            onChange={handleBillFile}
            className="hidden"
          />
          <button
            type="button"
            onClick={() => fileRef.current?.click()}
            disabled={analyzing}
            className="w-full rounded-card border border-line hover:border-primary/50 text-sm font-medium text-ink-soft hover:text-primary py-2.5 transition-colors disabled:opacity-60"
          >
            {analyzing ? t("priceCheck.analyzing") : `📷 ${t("priceCheck.uploadBill")}`}
          </button>
          {billError && <p className="text-xs text-alert font-medium mt-1.5">{billError}</p>}
        </div>
      )}

      {billItems && billItems.length > 0 && (
        <div className="rounded-card border border-line px-4 py-3">
          <p className="text-[11px] uppercase tracking-wide text-ink-soft font-semibold mb-2">
            {t("priceCheck.extractedItems")}
          </p>
          <ul className="flex flex-col gap-1">
            {billItems.map((it, i) => (
              <li key={i} className="flex justify-between gap-3 text-xs text-ink-soft">
                <span className="truncate">{it.description || "—"}</span>
                <span className="font-mono shrink-0 text-ink">
                  {it.amount != null ? formatINR(it.amount) : "—"}
                </span>
              </li>
            ))}
          </ul>
          <p className="text-[11px] text-ink-soft mt-2 leading-relaxed">{t("priceCheck.llmNote")}</p>
        </div>
      )}

      {billTotal != null && (
        <div className="rounded-card border border-seal/40 bg-seal-light px-4 py-3">
          {contributeState === "done" ? (
            <p className="text-xs text-ink font-medium">{t("contribute.done")}</p>
          ) : (
            <>
              <p className="text-sm font-medium text-ink">{t("contribute.prompt")}</p>
              <p className="text-[11px] text-ink-soft mt-1 leading-relaxed">
                {t("contribute.explainer")}
              </p>
              {contributeState === "error" && (
                <p className="text-xs text-alert font-medium mt-1.5">{t("contribute.failed")}</p>
              )}
              <button
                type="button"
                onClick={handleContribute}
                disabled={contributeState === "sending"}
                className="mt-2 rounded-card bg-seal hover:bg-seal/90 text-white font-semibold text-xs px-4 py-2 transition-colors disabled:opacity-60"
              >
                {contributeState === "sending"
                  ? t("contribute.sending")
                  : t("contribute.submit")}
              </button>
            </>
          )}
        </div>
      )}

      {verdict && (
        <div className={`rounded-card border px-4 py-3 text-sm ${VERDICT_STYLE[verdict]}`}>
          <p className="font-medium">
            {verdict === "within" && t("priceCheck.withinRange")}
            {verdict === "below" && t("priceCheck.belowRange")}
            {verdict === "above" && t("priceCheck.aboveRange")}
          </p>
          <p className="text-xs mt-1 opacity-90">
            {formatINR(costMin)} – {formatINR(costMax)}
          </p>
          {verdict === "above" && (
            <p className="text-xs mt-1.5">{t("priceCheck.aboveRangeSuggestion")}</p>
          )}
        </div>
      )}
    </div>
  );
}
