# `backend/app/services/` — business logic

Everything with a decision in it. Each function takes a SQLAlchemy `Session` as
its first argument and reads data through `app/db/repositories.py` (which returns
plain dicts), so the scoring logic never touches ORM objects directly. This is
the seam that let the datastore move from flat JSON to Postgres without the
scoring code changing.

## Files

| File | What it does |
|---|---|
| `treatment_service.py` | Treatment lookup by id; name/alias search; symptom search using an F1-style token match against each treatment's `symptoms` list. |
| `cost_service.py` | The core estimator. Pools matching `cost_records` rows weighted by `sample_size`, scores confidence from **sample size (0.6)** + **recency (0.4)**, labels it high/medium/low. Walks a **tier fallback**: exact city+type → city → state → national reference. A national-reference hit is a synthetic single record built from a genuinely-sourced rate, flagged so the response can say so. Returns `estimate=None` when even that fails. |
| `hospital_service.py` | Hospital list/detail; filters by treatment offered and city; "budget mode" ordering that favours government / scheme-empanelled hospitals. |
| `scheme_service.py` | `check_eligibility` — rule-based pass over the 9 seeded schemes using annual household income, state/UT, and the govt-employee/pensioner flag. Coverage stays **qualitative** (schemes carry no per-procedure rupee caps in the seed data). |
| `episode_service.py` | Multi-treatment episode: calls `cost_service.estimate_cost` per line × quantity, sums the ranges, takes the **weakest** line's confidence, and (given household details) reuses `scheme_service` to list schemes that *may* apply. Arithmetic stops at the pre-scheme total — no invented "covered amount". |
| `auth_service.py` | DB-backed users / `auth_sessions` / `password_reset_tokens`. PBKDF2 password hashing. `get_user_by_session` is what the router `_deps` call. |
| `saved_estimate_service.py` | Create/list/delete per-user saved estimates. On read, recomputes the estimate server-side and reports drift vs the stored snapshot. |
| `contribution_service.py` | Anonymous crowd-sourced bill submissions into `cost_contributions`; admin approve promotes a row into `cost_records` (`sample_size=1`, source labelled self-reported); reject just marks it. |
| `multimodal/` | Groq API helpers — OCR, transcription, estimate explainer. See `multimodal/explanation.md`. |

## Data-honesty rule (why the code looks conservative)

Every rupee figure the API returns must trace back to sourced sample data or a
genuine national reference rate. Services never fabricate numbers, and the LLM
helpers are handed pre-computed figures with a strict "invent nothing" prompt —
they explain, they don't calculate.
