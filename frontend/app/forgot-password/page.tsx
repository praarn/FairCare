"use client";

import { useState } from "react";
import Link from "next/link";
import { forgotPassword } from "@/lib/api";
import { useLanguage } from "@/lib/language-context";

export default function ForgotPasswordPage() {
  const { t } = useLanguage();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ message: string; reset_token: string | null } | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await forgotPassword(email);
      setResult(res);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-6 max-w-sm mx-auto">
      <h1 className="font-display text-2xl font-semibold text-ink text-center">
        {t("auth.forgotTitle")}
      </h1>
      <p className="text-sm text-ink-soft text-center -mt-4">{t("auth.forgotSubtitle")}</p>

      {!result ? (
        <form
          onSubmit={handleSubmit}
          className="rounded-card border border-line bg-surface p-5 sm:p-6 shadow-card flex flex-col gap-4"
        >
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-ink mb-1.5">
              {t("auth.emailLabel")}
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-card border border-line bg-surface px-4 py-3 text-base text-ink focus:border-primary"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-card bg-primary hover:bg-primary-dark disabled:opacity-60 text-white font-semibold text-base py-3.5 transition-colors"
          >
            {t("auth.forgotSubmit")}
          </button>
        </form>
      ) : (
        <div className="rounded-card border border-line bg-surface p-5 sm:p-6 shadow-card flex flex-col gap-4">
          <p className="text-sm text-ink">{result.message}</p>

          {result.reset_token && (
            <>
              <div className="rounded-card border border-seal/40 bg-seal-light px-4 py-3 text-sm text-ink">
                {t("auth.resetLinkNote")}
              </div>
              <Link
                href={`/reset-password?token=${encodeURIComponent(result.reset_token)}`}
                className="w-full text-center rounded-card bg-primary hover:bg-primary-dark text-white font-semibold text-base py-3.5 transition-colors"
              >
                {t("auth.resetLinkButton")}
              </Link>
            </>
          )}
        </div>
      )}

      <Link href="/login" className="text-center text-sm text-primary underline underline-offset-2">
        {t("auth.backToLogin")}
      </Link>
    </div>
  );
}
