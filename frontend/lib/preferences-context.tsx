"use client";

import { createContext, useContext, useState, useCallback } from "react";
import { useRouter } from "next/navigation";

type PreferencesContextValue = {
  dataSaver: boolean;
  setDataSaver: (v: boolean) => void;
  largeText: boolean;
  setLargeText: (v: boolean) => void;
};

const PreferencesContext = createContext<PreferencesContextValue | null>(null);

export function PreferencesProvider({
  initialDataSaver,
  initialLargeText,
  children,
}: {
  initialDataSaver: boolean;
  initialLargeText: boolean;
  children: React.ReactNode;
}) {
  const [dataSaver, setDataSaverState] = useState(initialDataSaver);
  const [largeText, setLargeTextState] = useState(initialLargeText);
  const router = useRouter();

  const setDataSaver = useCallback(
    (v: boolean) => {
      setDataSaverState(v);
      document.cookie = `sahaj_datasaver=${v ? "1" : "0"}; path=/; max-age=31536000`;
      router.refresh();
    },
    [router]
  );

  const setLargeText = useCallback(
    (v: boolean) => {
      setLargeTextState(v);
      document.cookie = `sahaj_textsize=${v ? "large" : "normal"}; path=/; max-age=31536000`;
      router.refresh();
    },
    [router]
  );

  return (
    <PreferencesContext.Provider value={{ dataSaver, setDataSaver, largeText, setLargeText }}>
      {children}
    </PreferencesContext.Provider>
  );
}

export function usePreferences() {
  const ctx = useContext(PreferencesContext);
  if (!ctx) throw new Error("usePreferences must be used within PreferencesProvider");
  return ctx;
}
