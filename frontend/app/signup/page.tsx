"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { useLanguage } from "@/lib/language-context";

export default function SignupPage() {
  const { t } = useLanguage();
  const { signup } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

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

    setLoading(true);
    try {
      await signup(name, email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Signup failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-6 max-w-sm mx-auto">
      <h1 className="font-display text-2xl font-semibold text-ink text-center">
        {t("auth.signupTitle")}
      </h1>

      <form
        onSubmit={handleSubmit}
        className="rounded-card border border-line bg-surface p-5 sm:p-6 shadow-card flex flex-col gap-4"
      >
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-ink mb-1.5">
            {t("auth.nameLabel")}
          </label>
          <input
            id="name"
            type="text"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full rounded-card border border-line bg-surface px-4 py-3 text-base text-ink focus:border-primary"
          />
        </div>

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

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-ink mb-1.5">
            {t("auth.passwordLabel")}
          </label>
          <input
            id="password"
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
          {t("auth.signupSubmit")}
        </button>
      </form>

      <p className="text-center text-sm text-ink-soft">
        {t("auth.haveAccount")}{" "}
        <Link href="/login" className="text-primary font-medium underline underline-offset-2">
          {t("auth.loginLink")}
        </Link>
      </p>
    </div>
  );
}