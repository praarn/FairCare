"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useLanguage } from "@/lib/language-context";
import { useAuth } from "@/lib/auth-context";
import LanguageDropdown from "./LanguageDropdown";

const AUTH_ROUTES = ["/login", "/signup", "/forgot-password", "/reset-password"];

export default function Header() {
  const { t } = useLanguage();
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const isAuthRoute = AUTH_ROUTES.some((route) => pathname?.startsWith(route));

  return (
    <header className="border-b border-line bg-surface">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between gap-4">
        <Link href={isAuthRoute ? "/login" : "/"} className="flex items-center gap-2.5 shrink-0">
          <span
            aria-hidden
            className="w-9 h-9 rounded-full bg-primary text-white flex items-center justify-center font-display text-lg"
          >
            F
          </span>
          <span className="font-display text-xl font-semibold text-ink hidden sm:inline">
            FairCare
          </span>
        </Link>

        {/* All the tool links now live as cards on the homepage — the
            header just carries the essentials: language + account. */}
        {!isAuthRoute && (
          <div className="flex items-center gap-3">
            {user?.is_admin && (
              <Link
                href="/contribute/review"
                className="text-sm font-medium text-primary hover:text-primary-dark underline underline-offset-2 hidden sm:inline"
              >
                {t("nav.adminReview")}
              </Link>
            )}
            <LanguageDropdown />
            {user && (
              <div className="flex items-center gap-2 text-sm font-medium">
                <span className="text-ink-soft hidden sm:inline">{user.name}</span>
                <button
                  type="button"
                  onClick={() => logout()}
                  className="text-ink-soft hover:text-alert underline underline-offset-2"
                >
                  {t("nav.logout")}
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );
}