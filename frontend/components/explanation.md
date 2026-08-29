# `frontend/components/` — UI components

Mix of presentational components and `"use client"` interactive islands mounted
inside otherwise server-rendered pages. All copy goes through `lib/i18n.ts`
(`t(lang, key)`); nothing here hard-codes user-facing English.

## Interactive islands

| Component | Role |
|---|---|
| `PriceCheckTool.tsx` | Main estimate flow on the landing page. Also carries the optional "upload a bill photo" path into `POST /api/multimodal/analyze-bill`, folding the OCR result into the verdict card. |
| `TreatmentAutocomplete.tsx` | Treatment name/alias search box; falls back to server transcription (`lib/useServerTranscription.ts`) for voice when the browser lacks Web Speech. |
| `InsuranceCoverageEstimator.tsx` | Client-side coverage what-if on top of an estimate. |
| `PaymentPlanEstimator.tsx` | EMI / instalment breakdown of an estimate. |
| `SaveEstimateButton.tsx` | Persists an estimate for the logged-in user via `POST /api/saved-estimates` (auth token from `lib/token.ts`). |
| `ShareEstimate.tsx` / `ReadAloudButton.tsx` | Share link + speech-synthesis readout. |
| `RecordHistory.tsx` | Renders locally-stored recently-viewed estimates (`lib/history.ts`). |
| `SettingsMenu.tsx` / `LanguageDropdown.tsx` / `LanguageToggle.tsx` | Language + preferences (data-saver) controls, backed by the contexts in `lib/`. |

## Presentational

`CostGauge.tsx`, `ConfidenceBadge.tsx`, `CostOfCareBreakdown.tsx`,
`HospitalCard.tsx`, `FeatureCard.tsx`, `DisclaimerBanner.tsx`, `StampBadge.tsx`,
`EstimateExplainer.tsx` (renders the AI explanation from
`POST /api/multimodal/explain-estimate`), `Header.tsx`.

## Wiring

`Providers.tsx` composes the client context providers (auth, language,
preferences) and is mounted once in `app/layout.tsx`.
