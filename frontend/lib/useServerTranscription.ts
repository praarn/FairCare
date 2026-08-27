"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { multimodalStatus, transcribeAudio } from "./api";

/**
 * MediaRecorder -> POST /api/multimodal/transcribe (Groq Whisper).
 *
 * This is the *fallback* path for voice input: components try the browser's
 * built-in Web Speech API first and only reach for this when that isn't
 * available (Firefox, some Android webviews) — or never, if the backend has
 * no GROQ_API_KEY, in which case `available` stays false and the caller
 * simply doesn't offer server transcription.
 */
export function useServerTranscription(lang: string) {
  const [available, setAvailable] = useState(false);
  const [recording, setRecording] = useState(false);
  const [busy, setBusy] = useState(false);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    let cancelled = false;
    const hasRecorder =
      typeof window !== "undefined" &&
      typeof window.MediaRecorder !== "undefined" &&
      !!navigator.mediaDevices?.getUserMedia;
    if (!hasRecorder) return;
    multimodalStatus()
      .then((s) => {
        if (!cancelled) setAvailable(s.transcription);
      })
      .catch(() => {
        if (!cancelled) setAvailable(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const cleanup = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    recorderRef.current = null;
    chunksRef.current = [];
  }, []);

  useEffect(() => cleanup, [cleanup]);

  const start = useCallback(
    async (onTranscript: (text: string) => void, onError?: (key: string) => void) => {
      if (recording || busy) return;
      let stream: MediaStream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      } catch {
        onError?.("voice.micDenied");
        return;
      }
      streamRef.current = stream;
      chunksRef.current = [];
      const recorder = new MediaRecorder(stream);
      recorderRef.current = recorder;

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.onstop = async () => {
        setRecording(false);
        const blob = new Blob(chunksRef.current, {
          type: recorder.mimeType || "audio/webm",
        });
        cleanup();
        if (blob.size === 0) return;
        setBusy(true);
        try {
          const { text } = await transcribeAudio(blob, lang);
          if (text) onTranscript(text);
        } catch {
          onError?.("priceCheck.uploadFailed");
        } finally {
          setBusy(false);
        }
      };

      recorder.start();
      setRecording(true);
    },
    [recording, busy, lang, cleanup]
  );

  const stop = useCallback(() => {
    if (recorderRef.current && recorderRef.current.state !== "inactive") {
      recorderRef.current.stop();
    }
  }, []);

  return { available, recording, busy, start, stop };
}
