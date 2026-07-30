"use client";

import { LanguageProvider } from "@/lib/language-context";
import { AuthProvider } from "@/lib/auth-context";
import { Lang } from "@/lib/i18n";
import { User } from "@/lib/types";

export default function Providers({
  initialLang,
  initialUser,
  children,
}: {
  initialLang: Lang;
  initialUser: User | null;
  children: React.ReactNode;
}) {
  return (
    <LanguageProvider initialLang={initialLang}>
      <AuthProvider initialUser={initialUser}>{children}</AuthProvider>
    </LanguageProvider>
  );
}
