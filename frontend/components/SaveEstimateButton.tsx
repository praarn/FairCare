"use client";

import { useState } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/language-context";
import { useAuth } from "@/lib/auth-context";
import { getAuthToken } from "@/lib/token";
import { saveEstimate } from "@/lib/api";

export default function SaveEstimateButton({
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
  const { user } = useAuth();
  const [label, setLabel] = useState("");
  const [note, setNote] = useState("");
  const [status, setStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");

  if (!user) {
    return (
      <div className="rounded-card border border-line bg-surface p-4 text-sm text-ink-soft flex items-center justify-between gap-3 flex-wrap">
        <span>{t("save.signInPrompt")}</span>
        <Link href="/login" className="text-primary font-medium underline underline-offset-2">
          {t("auth.loginSubmit")}
        </Link>
      </div>
    );
  }

  if (status === "saved") {
    return (
      <div className="rounded-card border border-primary/40 bg-primary-light px-4 py-3 text-sm text-primary-dark font-medium">
        {t("save.saved")}
      </div>
    );
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setStatus("saving");
    try {
      const token = getAuthToken();
      if (!token) throw new Error("no token");
      await saveEstimate(token, {
        treatment_id: treatmentId,
        city,
        state,
        hospital_type: hospitalType,
        label: label.trim() || undefined,
        note: note.trim() || undefined,
        lang,
      });
      setStatus("saved");
    } catch {
      setStatus("error");
    }
  }

  return (
    <form
      onSubmit={handleSave}
      className="rounded-card border border-line bg-surface p-4 sm:p-5 flex flex-col gap-3"
    >
      <h3 className="font-display text-base font-semibold text-ink">{t("save.title")}</h3>
      <input
        type="text"
        value={label}
        onChange={(e) => setLabel(e.target.value)}
        placeholder={t("save.labelPlaceholder")}
        maxLength={200}
        className="w-full rounded-card border border-line bg-surface px-4 py-2.5 text-sm text-ink focus:border-primary"
      />
      <textarea
        value={note}
        onChange={(e) => setNote(e.target.value)}
        placeholder={t("save.notePlaceholder")}
        rows={2}
        className="w-full rounded-card border border-line bg-surface px-4 py-2.5 text-sm text-ink focus:border-primary resize-none"
      />
      {status === "error" && (
        <p className="text-xs text-alert font-medium">{t("save.failed")}</p>
      )}
      <button
        type="submit"
        disabled={status === "saving"}
        className="self-start rounded-card bg-primary hover:bg-primary-dark text-white font-semibold text-sm px-5 py-2.5 transition-colors disabled:opacity-60"
      >
        {status === "saving" ? t("save.saving") : t("save.button")}
      </button>
    </form>
  );
}
