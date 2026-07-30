import Link from "next/link";
import { ReactNode } from "react";

const ACCENT_STYLES: Record<string, string> = {
  primary: "bg-primary-light text-primary-dark",
  seal: "bg-seal-light text-seal",
  alert: "bg-alert-light text-alert",
};

export default function FeatureCard({
  href,
  title,
  description,
  icon,
  accent,
}: {
  href: string;
  title: string;
  description: string;
  icon: ReactNode;
  accent: "primary" | "seal" | "alert";
}) {
  return (
    <Link
      href={href}
      className="group rounded-card border border-line bg-surface p-4 shadow-card flex flex-col gap-3 hover:border-primary/40 hover:-translate-y-0.5 hover:shadow-lg transition-all duration-200"
    >
      <span
        className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${ACCENT_STYLES[accent]}`}
      >
        {icon}
      </span>
      <div>
        <h3 className="font-display text-base font-semibold text-ink group-hover:text-primary transition-colors">
          {title}
        </h3>
        <p className="text-xs text-ink-soft mt-0.5 leading-relaxed">{description}</p>
      </div>
    </Link>
  );
}