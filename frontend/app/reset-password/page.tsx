"use client";

import { useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { resetPassword } from "@/lib/api";
import { useLanguage } from "@/lib/language-context";

function ResetPasswordForm() {
  const { t } = useLanguage();
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (password.length < 8) {
      setError(t("auth.passwordTooShort"));
      return;
    }
    if (password !== confirmPassword) {
      setError(t("auth.passwordMismatch"));
      return;
    }
    if (!token) {
      setError(t("auth.invalidResetLink"));
      return;
    }

    setLoading(true);
    try {
      await resetPassword(token, password);
      setSuccess(true);
      setTimeout(() => router.push("/login"), 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Reset failed.");
    } finally {
      setLoading(false);
    }
  }

  if (!token) {
    return (
      <div className="flex flex-col gap-4 max-w-sm mx-auto text-center">
        <p className="text-ink-soft">{t("auth.invalidResetLink")}</p>
        <Link href="/forgot-password" className="text-primary font-medium underline underline-offset-2">
          {t("auth.forgotTitle")}
        </Link>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 max-w-sm mx-auto">
      <h1 className="font-display text-2xl font-semibold text-ink text-center">
        {t("auth.resetTitle")}
      </h1>

      {success ? (
        <div className="rounded-card border border-primary/40 bg-primary-light px-4 py-3 text-sm text-primary-dark text-center">
          {t("auth.resetSuccess")}
        </div>
      ) : (
        <form
          onSubmit={handleSubmit}
          className="rounded-card border border-line bg-surface p-5 sm:p-6 shadow-card flex flex-col gap-4"
        >
          <div>
            <label htmlFor="new-password" className="block text-sm font-medium text-ink mb-1.5">
              {t("auth.newPasswordLabel")}
            </label>
            <input
              id="new-password"
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-card border border-line bg-surface px-4 py-3 text-base text-ink focus:border-primary"
            />
          </div>

          <div>
            <label htmlFor="confirm-password" className="block text-sm font-medium text-ink mb-1.5">
              {t("auth.confirmPasswordLabel")}
            </label>
            <input
              id="confirm-password"
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full rounded-card border border-line bg-surface px-4 py-3 text-base text-ink focus:border-primary"
            />
          </div>

          {error && <p className="text-sm text-alert font-medium">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-card bg-primary hover:bg-primary-dark disabled:opacity-60 text-white font-semibold text-base py-3.5 transition-colors"
          >
            {t("auth.resetSubmit")}
          </button>
        </form>
      )}

      <Link href="/login" className="text-center text-sm text-primary underline underline-offset-2">
        {t("auth.backToLogin")}
      </Link>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={null}>
      <ResetPasswordForm />
    </Suspense>
  );
}
