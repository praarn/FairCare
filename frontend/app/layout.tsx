import type { Metadata } from "next";
import { cookies } from "next/headers";
import "./globals.css";
import Header from "@/components/Header";
import Providers from "@/components/Providers";
import { t, parseLang } from "@/lib/i18n";
import { fetchMe } from "@/lib/api";
import { User } from "@/lib/types";

export const metadata: Metadata = {
  title: "FairCare — Healthcare Cost Estimate",
  description:
    "Estimate treatment costs from verified data and find affordable, legitimate care options nearby.",
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const cookieStore = await cookies();
  const initialLang = parseLang(cookieStore.get("faircare_lang")?.value);

  const token = cookieStore.get("faircare_auth_token")?.value;
  let initialUser: User | null = null;
  if (token) {
    try {
      initialUser = await fetchMe(token);
    } catch {
      initialUser = null; // expired/invalid token — treated as logged out
    }
  }

  return (
    <html lang={initialLang}>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Newsreader:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="font-body min-h-screen flex flex-col">
        <Providers initialLang={initialLang} initialUser={initialUser}>
          <div className="print:hidden">
            <Header />
          </div>
          <main className="flex-1 w-full max-w-3xl mx-auto px-4 sm:px-6 py-8">{children}</main>
          <footer className="text-center text-xs text-ink-soft py-8 px-4 print:hidden">
            {t(initialLang, "footer.note")}
          </footer>
        </Providers>
      </body>
    </html>
  );
}
