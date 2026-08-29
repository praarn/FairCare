# `backend/app/routers/` — the HTTP surface

One module per resource. Routers are **thin**: parse the request, resolve
`lang` (`en`/`hi`), call exactly one service function, and map the result onto a
Pydantic response model from `app/schemas.py`. No scoring, no DB queries beyond
`Depends(get_db)`, no branching business rules — those live in `app/services/`.

## Auth model

- `_deps.py` holds the shared FastAPI dependencies:
  - `current_user` — requires a valid `Authorization: Bearer <token>` session, returns the public user dict (includes `is_admin`).
  - `current_admin` — `current_user` + `is_admin` check, else `403`.
  - `optional_user` — returns `None` instead of raising when no/invalid token, for routes that personalise but don't require login.
- Tokens are opaque session ids validated by `auth_service.get_user_by_session`.

## Endpoints

| Module | Prefix | Routes |
|---|---|---|
| `treatments.py` | `/api/treatments` | `GET /search` (name/alias), `GET /search-symptoms` (F1 symptom match) |
| `predict.py` | `/api/predict-cost` | `POST ""` — single-treatment estimate. Needs a `city` or `state`. `404` if no data even after national-reference fallback. Bundles a standard EN/HI disclaimer. |
| `episode.py` | `/api/estimate-episode` | `POST ""` — multi-treatment "care episode": per-line estimate × quantity, summed, weakest-line confidence, qualitative eligible-scheme context. No auth. |
| `hospitals.py` | `/api/hospitals` | `GET ""` (filter by `treatment_id`, `city`, budget ordering), `GET /{id}` |
| `schemes.py` | `/api/schemes` | `GET /eligible` — rule-based eligibility from income / state / govt-employee flag |
| `auth.py` | `/api/auth` | `signup`, `login`, `logout`, `GET /me`, `forgot-password`, `reset-password`. PBKDF2 hashing; `is_admin` threaded through `/me` + login + signup. |
| `saved.py` | `/api/saved-estimates` | `POST` / `GET` / `DELETE /{id}` — per-user saved estimates, snapshot recomputed server-side, drift-vs-snapshot on read. Requires `current_user`. |
| `contributions.py` | `/api/contributions` | `POST ""` anonymous crowd-sourced bill submit; `GET ""` + `POST /{id}/approve` + `POST /{id}/reject` are `current_admin`-only. Approve promotes the row into a real `cost_records` entry (`sample_size=1`, self-reported label). |
| `multimodal.py` | `/api/multimodal` | `GET /status`, `POST /analyze-bill`, `POST /explain-estimate`, `POST /transcribe`. All POSTs return `503` when `settings.groq_enabled` is false. |

## Registration

Every router is imported and `app.include_router`-ed in `app/main.py`. Adding a
resource = new module here + one line in `main.py`.
