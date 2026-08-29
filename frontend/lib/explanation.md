# `frontend/lib/` — shared client/server helpers

| File | Role |
|---|---|
| `api.ts` | The single backend client. Every `fetch` to FastAPI goes through here. Resolves the API base per environment (browser → `NEXT_PUBLIC_API_BASE_URL`; SSR → `API_INTERNAL_BASE_URL`) — see `../explanation.md`. `handle<T>()` turns non-2xx into thrown `Error(detail)`, with a special hint when the backend returns `{"detail":"Not Found"}` (usually a stale backend missing a newer route). |
| `types.ts` | TypeScript mirrors of the backend Pydantic response models (`Treatment`, `PredictCostResponse`, `HospitalOut`, `SchemeResult`, `User`, `Contribution`, `SavedEstimate`, `EpisodeResult`, multimodal types, …). |
| `i18n.ts` | `Lang` union + `LANGUAGES` + autonym `LANGUAGE_LABELS`, the translation tables, `t(lang, key)`, `parseLang`, `hospitalTypeLabel`. |
| `format.ts` | `formatINR` (Intl `en-IN` currency) and other display formatters. |
| `history.ts` | `HistoryEntry` type + `localStorage` read/write for recently-viewed estimates (client-only). |
| `token.ts` | Reads the `sahaj_auth_token` cookie client-side. Kept standalone so small client islands (Save button, admin page) can authenticate their own fetches without importing the whole auth context. |
| `auth-context.tsx` | `"use client"` React context: current user, `login`/`logout`/`signup`, writes the `sahaj_auth_token` cookie. |
| `language-context.tsx` | `"use client"` context: current `Lang`, `t()` bound to it, writes the `sahaj_lang` cookie and refreshes the route on change. |
| `preferences-context.tsx` | `"use client"` context: data-saver toggle and other UI preferences. |
| `useServerTranscription.ts` | `"use client"` hook: `MediaRecorder` → `POST /api/multimodal/transcribe` (Groq Whisper), used as the voice fallback when the browser has no Web Speech API. |

The three context files are composed in `components/Providers.tsx`, mounted once
in `app/layout.tsx`. `layout.tsx` reads both cookies server-side so the first
paint already has the right language and user.
