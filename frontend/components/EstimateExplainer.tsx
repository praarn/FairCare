"use client";

import { useEffect, useState } from "react";
import { useLanguage } from "@/lib/language-context";
import { explainEstimate, multimodalStatus } from "@/lib/api";
import type { EstimateExplanation } from "@/lib/types";

export default function EstimateExplainer({
  treatmentId,
  city,
  state,
  hospitalType,
}: {
  treatmentId: string;
  city?: string;
  state?: string;
  hospitalType?: string;
}) {
  const { t, lang } = useLanguage();
  const [available, setAvailable] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [result, setResult] = useState<EstimateExplanation | null>(null);

  useEffect(() => {
    let cancelled = false;
    multimodalStatus()
      .then((s) => !cancelled && setAvailable(s.text))
      .catch(() => !cancelled && setAvailable(false));
    return () => {
      cancelled = true;
    };
  }, []);

  if (!available) return null;

  async function handleExplain() {
    setLoading(true);
    setError(false);
    try {
      const res = await explainEstimate({
        treatment_id: treatmentId,
        city,
        state,
        hospital_type: hospitalType,
        lang,
      });
      setResult(res);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-card border border-line bg-surface p-5 sm:p-6 flex flex-col gap-4">
      {!result && (
        <button
          type="button"
          onClick={handleExplain}
          disabled={loading}
          className="self-start rounded-card border border-primary/40 text-primary hover:bg-primary-light font-medium text-sm px-5 py-2.5 transition-colors disabled:opacity-60"
        >
          {loading ? t("explain.loading") : `✨ ${t("explain.button")}`}
        </button>
      )}

      {error && <p className="text-sm text-alert font-medium">{t("explain.failed")}</p>}

      {result && (
        <div className="flex flex-col gap-4">
          <p className="text-sm text-ink leading-relaxed">{result.summary}</p>

          {result.line_item_notes.length > 0 && (
            <ul className="flex flex-col gap-1.5">
              {result.line_item_notes.map((n, i) => (
                <li key={i} className="text-sm text-ink-soft">
                  <span className="font-medium text-ink">{n.item}: </span>
                  {n.note}
                </li>
              ))}
            </ul>
          )}

          {result.questions_to_ask.length > 0 && (
            <div>
              <p className="text-xs uppercase tracking-wide text-ink-soft font-semibold mb-2">
                {t("explain.questionsTitle")}
              </p>
              <ul className="flex flex-col gap-1.5 list-disc pl-5">
                {result.questions_to_ask.map((q, i) => (
                  <li key={i} className="text-sm text-ink-soft">
                    {q}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.scheme_hint && (
            <div className="rounded-card border border-seal/40 bg-seal-light px-4 py-3 text-sm text-ink">
              <span className="font-medium">{t("explain.schemeHintTitle")}: </span>
              {result.scheme_hint}
            </div>
          )}
        </div>
      )}

      <p className="text-[11px] text-ink-soft leading-relaxed">{t("explain.aiNote")}</p>
    </div>
  );
}
