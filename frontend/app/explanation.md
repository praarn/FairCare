# `frontend/app/` — routes (App Router)

One folder per route segment. `page.tsx` is the route; `layout.tsx` (this
folder's root) wraps every page with `<Header>`, the context `<Providers>`, and
does the SSR `fetchMe()` for the logged-in user using the `faircare_auth_token`
cookie. Language comes from the `faircare_lang` cookie via `parseLang`.

Most pages are React Server Components that fetch from the backend during SSR and
mount a small client island for interactivity.

| Route | Page |
|---|---|
| `/` (`page.tsx`) | Landing — treatment search / price-check entry point. |
| `/results` | Single-treatment estimate: cost gauge, confidence badge, factors, sources, disclaimer. Reads `POST /api/predict-cost`. |
| `/episode` | Multi-treatment "care episode" builder → `POST /api/estimate-episode`. Printable. |
| `/hospitals` + `/hospitals/[id]` | Hospital list (filter by treatment/city, budget ordering) and detail. |
| `/eligibility` | Government-scheme eligibility form → `GET /api/schemes/eligible`. |
| `/compare` | Side-by-side comparison view. |
| `/symptom-checker` | Symptom → treatment search (`GET /api/treatments/search-symptoms`), with voice input fallback. |
| `/methodology` | Static explainer of how estimates and confidence are computed. |
| `/history` | Locally-stored recently-viewed estimates + server-side saved estimates for logged-in users. |
| `/login`, `/signup` | Auth forms (`/api/auth/*`). |
| `/forgot-password`, `/reset-password` | Password-reset flow. |
| `/contribute/review` | Admin-only queue for crowd-sourced bill contributions (`GET/POST /api/contributions`, gated by `is_admin`). |

Adding a page = new folder with a `page.tsx`; it inherits `layout.tsx`
automatically.
