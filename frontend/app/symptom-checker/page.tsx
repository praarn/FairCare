"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { searchTreatmentsBySymptom } from "@/lib/api";
import { Treatment, CITIES } from "@/lib/types";
import { useLanguage } from "@/lib/language-context";
import { useServerTranscription } from "@/lib/useServerTranscription";

// Minimal ambient shape for the Web Speech API - not in the default TS lib.
interface SpeechRecognitionLike {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  onresult: ((event: any) => void) | null;
  onerror: (() => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
}

export default function SymptomCheckerPage() {
  const { t, lang } = useLanguage();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Treatment[] | null>(null);
  const [loading, setLoading] = useState(false);
  // Every "Get estimate" link needs a city to pass to /results (which
  // requires city or state). This used to be hardcoded to "Delhi" for
  // every user regardless of where they actually are — that silently gave
  // everyone a Delhi-priced estimate. Ask for it instead, same as the
  // home and compare pages already do.
  const [city, setCity] = useState<string>(CITIES[0]);

  // Voice input: browser Web Speech API first, Groq transcription as fallback.
  const [webSpeech, setWebSpeech] = useState(false);
  const [webListening, setWebListening] = useState(false);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const serverTx = useServerTranscription(lang);

  const micAvailable = webSpeech || serverTx.available;
  const listening = webListening || serverTx.recording;

  useEffect(() => {
    const Ctor = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    setWebSpeech(!!Ctor);
  }, []);

  function appendTranscript(text: string) {
    setQuery((prev) => (prev ? `${prev} ${text}` : text));
  }

  function startWebSpeech() {
    const Ctor = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!Ctor) return;
    const recognition: SpeechRecognitionLike = new Ctor();
    recognition.lang = lang === "hi" ? "hi-IN" : "en-IN";
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.onresult = (event: any) => {
      const transcript = event.results?.[0]?.[0]?.transcript ?? "";
      if (transcript) appendTranscript(transcript);
    };
    recognition.onerror = () => setWebListening(false);
    recognition.onend = () => setWebListening(false);
    recognitionRef.current = recognition;
    setWebListening(true);
    recognition.start();
  }

  function handleMicClick() {
    if (webSpeech) {
      if (webListening) {
        recognitionRef.current?.stop();
        setWebListening(false);
      } else {
        startWebSpeech();
      }
      return;
    }
    if (serverTx.recording) serverTx.stop();
    else void serverTx.start(appendTranscript);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    try {
      const data = await searchTreatmentsBySymptom(query);
      setResults(data);
    } finally {
      setLoading(false);
    }
  }

  function treatmentLabel(treatment: Treatment) {
    return lang === "hi" && treatment.name_hi ? treatment.name_hi : treatment.name;
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <p className="text-seal font-semibold text-sm uppercase tracking-wide mb-2">
          {t("symptom.eyebrow")}
        </p>
        <h1 className="font-display text-3xl sm:text-4xl font-semibold text-ink leading-tight">
          {t("symptom.title")}
        </h1>
        <p className="mt-2 text-ink-soft text-base max-w-xl">{t("symptom.subtitle")}</p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="rounded-card border border-line bg-surface p-5 sm:p-6 shadow-card flex flex-col gap-4"
      >
        <div className="relative">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t("symptom.placeholder")}
            rows={3}
            className="w-full rounded-card border border-line bg-surface px-4 py-3 pr-12 text-base text-ink placeholder:text-ink-soft/60 focus:border-primary resize-none"
          />
          {micAvailable && (
            <button
              type="button"
              onClick={handleMicClick}
              disabled={serverTx.busy}
              aria-label={listening ? t("voice.recording") : t("search.voiceHint")}
              title={t("search.voiceHint")}
              className={`absolute right-2 top-2 w-8 h-8 rounded-full flex items-center justify-center transition-colors disabled:opacity-60 ${
                listening ? "bg-alert text-white" : "bg-primary-light text-primary hover:bg-primary/20"
              }`}
            >
              {listening ? (
                <span aria-hidden className="w-2.5 h-2.5 rounded-full bg-white animate-pulse" />
              ) : (
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" aria-hidden>
                  <path
                    d="M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3Z"
                    stroke="currentColor"
                    strokeWidth="2"
                  />
                  <path
                    d="M19 11a7 7 0 0 1-14 0M12 18v3"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                  />
                </svg>
              )}
            </button>
          )}
        </div>
        {listening && (
          <p className="text-xs text-alert font-medium -mt-1">{t("voice.recording")}</p>
        )}
        {serverTx.busy && (
          <p className="text-xs text-ink-soft font-medium -mt-1">{t("voice.transcribing")}</p>
        )}
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-card bg-primary hover:bg-primary-dark disabled:opacity-60 text-white font-semibold text-base py-3.5 transition-colors"
        >
          {t("symptom.submit")}
        </button>
      </form>

      {results && (
        <div className="flex flex-col gap-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-ink-soft">
            {t("symptom.resultsTitle")}
          </p>
          {results.length > 0 && (
            <div className="flex items-center gap-2">
              <label htmlFor="symptom-city-select" className="text-sm text-ink-soft shrink-0">
                {t("home.cityLabel")}
              </label>
              <select
                id="symptom-city-select"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="flex-1 rounded-card border border-line bg-surface px-3 py-2 text-sm text-ink focus:border-primary"
              >
                {CITIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          )}
          {results.length === 0 ? (
            <div className="rounded-card border border-line bg-surface p-6 text-center text-ink-soft">
              {t("symptom.noResults")}
            </div>
          ) : (
            results.map((tr) => (
              <div
                key={tr.id}
                className="rounded-card border border-line bg-surface p-4 shadow-card flex items-center justify-between gap-3"
              >
                <div>
                  <div className="font-medium text-ink">{treatmentLabel(tr)}</div>
                  <div className="text-xs text-ink-soft">{tr.category}</div>
                </div>
                <Link
                  href={`/results?treatment_id=${tr.id}&city=${encodeURIComponent(city)}`}
                  className="shrink-0 text-sm text-primary font-medium underline underline-offset-2"
                >
                  {t("symptom.getEstimate")} →
                </Link>
              </div>
            ))
          )}
        </div>
      )}

      <div className="rounded-card border border-alert/40 bg-alert-light px-4 py-3 text-sm text-alert">
        {t("symptom.disclaimer")}
      </div>
    </div>
  );
}
