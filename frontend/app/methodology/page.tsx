"use client";

import { useLanguage } from "@/lib/language-context";

export default function MethodologyPage() {
  const { t } = useLanguage();

  const steps = [
    { title: t("methodology.step1Title"), body: t("methodology.step1Body") },
    { title: t("methodology.step2Title"), body: t("methodology.step2Body") },
    { title: t("methodology.step3Title"), body: t("methodology.step3Body") },
    { title: t("methodology.step4Title"), body: t("methodology.step4Body") },
  ];

  return (
    <div className="flex flex-col gap-6">
      <div>
        <p className="text-seal font-semibold text-sm uppercase tracking-wide mb-2">
          {t("methodology.eyebrow")}
        </p>
        <h1 className="font-display text-3xl sm:text-4xl font-semibold text-ink leading-tight">
          {t("methodology.title")}
        </h1>
      </div>

      <div className="flex flex-col gap-4">
        {steps.map((step, i) => (
          <div
            key={i}
            className="rounded-card border border-line bg-surface p-5 sm:p-6 shadow-card flex gap-4"
          >
            <span
              aria-hidden
              className="shrink-0 w-9 h-9 rounded-full bg-primary-light text-primary-dark font-display font-semibold flex items-center justify-center"
            >
              {i + 1}
            </span>
            <div>
              <h2 className="font-display text-lg font-semibold text-ink mb-1.5">
                {step.title}
              </h2>
              <p className="text-sm text-ink-soft leading-relaxed">{step.body}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
