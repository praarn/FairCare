"use client";

import { useEffect, useRef, useState } from "react";
import { searchTreatments } from "@/lib/api";
import { Treatment } from "@/lib/types";
import { useLanguage } from "@/lib/language-context";
import { useServerTranscription } from "@/lib/useServerTranscription";

// Minimal ambient shape for the Web Speech API - not in default TS lib.
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

export default function TreatmentAutocomplete({
  onSelect,
}: {
  onSelect: (treatment: Treatment | null) => void;
}) {
  const { lang, t } = useLanguage();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Treatment[]>([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [voiceSupported, setVoiceSupported] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [voiceMatchNote, setVoiceMatchNote] = useState<string | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const serverTx = useServerTranscription(lang);

  // The mic button appears if EITHER the browser's Web Speech API is available
  // (primary) or the backend offers Groq transcription (fallback for Firefox etc).
  const micAvailable = voiceSupported || serverTx.available;
  const listening = isListening || serverTx.recording;

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await searchTreatments(query);
        setResults(data);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 200);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [query]);

  useEffect(() => {
    const SpeechRecognitionCtor =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    setVoiceSupported(!!SpeechRecognitionCtor);
  }, []);

  function treatmentLabel(treatment: Treatment) {
    return lang === "hi" && treatment.name_hi ? treatment.name_hi : treatment.name;
  }

  function categoryLabel(treatment: Treatment) {
    return lang === "hi" && treatment.category_hi ? treatment.category_hi : treatment.category;
  }

  async function handleVoiceTranscript(transcript: string) {
    setQuery(transcript);
    setVoiceMatchNote(null);
    onSelect(null);

    try {
      const matches = await searchTreatments(transcript);
      setResults(matches);
      if (matches.length > 0) {
        // Voice input is inherently noisy — rather than making the person
        // tap the dropdown themselves, resolve straight to the closest
        // listed treatment and just tell them what we matched it to.
        const best = matches[0];
        setQuery(treatmentLabel(best));
        onSelect(best);
        setOpen(false);
        setVoiceMatchNote(treatmentLabel(best));
      } else {
        setOpen(true);
      }
    } catch {
      setOpen(true);
    }
  }

  function startListening() {
    const SpeechRecognitionCtor =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognitionCtor) return;

    const recognition: SpeechRecognitionLike = new SpeechRecognitionCtor();
    recognition.lang = lang === "hi" ? "hi-IN" : "en-IN";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event: any) => {
      const transcript = event.results?.[0]?.[0]?.transcript ?? "";
      if (transcript) {
        void handleVoiceTranscript(transcript);
      }
    };
    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);

    recognitionRef.current = recognition;
    setIsListening(true);
    setVoiceMatchNote(null);
    recognition.start();
  }

  function stopListening() {
    recognitionRef.current?.stop();
    setIsListening(false);
  }

  function handleMicClick() {
    if (voiceSupported) {
      if (isListening) stopListening();
      else startListening();
      return;
    }
    // Groq fallback (browser has no Web Speech API)
    if (serverTx.recording) {
      serverTx.stop();
    } else {
      setVoiceMatchNote(null);
      void serverTx.start((text) => void handleVoiceTranscript(text));
    }
  }

  return (
    <div className="relative">
      <label htmlFor="treatment-input" className="block text-sm font-medium text-ink mb-1.5">
        {t("search.label")}
      </label>
      <div className="relative">
        <input
          id="treatment-input"
          type="text"
          autoComplete="off"
          suppressHydrationWarning
          placeholder={t("search.placeholder")}
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setVoiceMatchNote(null);
            onSelect(null);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          className="w-full rounded-card border border-line bg-surface pl-4 pr-12 py-3 text-base text-ink placeholder:text-ink-soft/60 focus:border-primary"
        />
        {micAvailable && (
          <button
            type="button"
            onClick={handleMicClick}
            disabled={serverTx.busy}
            aria-label={listening ? t("search.listening") : t("search.voiceHint")}
            title={t("search.voiceHint")}
            className={`absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full flex items-center justify-center transition-colors disabled:opacity-60 ${
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
        <p className="text-xs text-alert font-medium mt-1.5">
          {serverTx.recording ? t("voice.recording") : t("search.listening")}
        </p>
      )}
      {serverTx.busy && (
        <p className="text-xs text-ink-soft font-medium mt-1.5">{t("voice.transcribing")}</p>
      )}
      {!listening && !serverTx.busy && voiceMatchNote && (
        <p className="text-xs text-primary font-medium mt-1.5">
          {t("search.matchedTo")} <span className="font-semibold">{voiceMatchNote}</span>
        </p>
      )}

      {open && query.trim().length > 0 && (
        <ul className="absolute z-10 mt-1.5 w-full rounded-card border border-line bg-surface shadow-card max-h-64 overflow-auto">
          {loading && <li className="px-4 py-3 text-sm text-ink-soft">{t("search.searching")}</li>}
          {!loading && results.length === 0 && (
            <li className="px-4 py-3 text-sm text-ink-soft">{t("search.noMatch")}</li>
          )}
          {!loading &&
            results.map((tr) => (
              <li key={tr.id}>
                <button
                  type="button"
                  onClick={() => {
                    setQuery(treatmentLabel(tr));
                    setVoiceMatchNote(null);
                    onSelect(tr);
                    setOpen(false);
                  }}
                  className="w-full text-left px-4 py-3 hover:bg-primary-light focus-visible:bg-primary-light"
                >
                  <div className="font-medium text-ink">{treatmentLabel(tr)}</div>
                  <div className="text-xs text-ink-soft">{categoryLabel(tr)}</div>
                </button>
              </li>
            ))}
        </ul>
      )}
    </div>
  );
}