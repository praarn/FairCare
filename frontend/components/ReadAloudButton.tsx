"use client";

import { useEffect, useState } from "react";
import { useLanguage } from "@/lib/language-context";

export default function ReadAloudButton({ text }: { text: string }) {
  const { lang, t } = useLanguage();
  const [supported, setSupported] = useState(false);
  const [speaking, setSpeaking] = useState(false);

  useEffect(() => {
    setSupported(typeof window !== "undefined" && "speechSynthesis" in window);
  }, []);

  useEffect(() => {
    // Stop any speech in progress if the component unmounts (navigating away).
    return () => {
      if (typeof window !== "undefined" && window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  function handleClick() {
    if (!supported) return;
    if (speaking) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
      return;
    }
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang === "hi" ? "hi-IN" : "en-IN";
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);
    window.speechSynthesis.speak(utterance);
    setSpeaking(true);
  }

  if (!supported) return null;

  return (
    <button
      type="button"
      onClick={handleClick}
      className={`inline-flex items-center gap-2 rounded-full border px-3.5 py-2 text-sm font-medium transition-colors ${
        speaking
          ? "bg-alert text-white border-alert"
          : "border-line text-ink-soft hover:border-primary/50 hover:text-primary"
      }`}
    >
      <span aria-hidden>{speaking ? "■" : "🔊"}</span>
      {speaking ? t("readAloud.stop") : t("readAloud.play")}
    </button>
  );
}
