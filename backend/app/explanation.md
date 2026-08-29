# `backend/app/` — how the API is put together

FastAPI service that does rule-based healthcare cost estimation, hospital lookup,
and government-scheme eligibility, backed by Postgres (SQLite in tests). Optional
Groq-powered multimodal helpers (bill-photo OCR, voice transcription, estimate
explainer) degrade to `503` when `GROQ_API_KEY` is unset.

For the exhaustive reference (every endpoint, table, and field) see
[`../../IMPLEMENTATION.md`](../../IMPLEMENTATION.md). This file is the orientation
map.

## Request lifecycle

```
HTTP request
  -> RequestIDMiddleware      (middleware.py)      attaches X-Request-ID, structlog binding
  -> CORS middleware          (main.py)            settings.backend_cors_origins
  -> slowapi rate limiter     (rate_limit.py)      tighter buckets on auth + multimodal
  -> router                   (routers/*.py)       thin: validate, call a service, shape response
       -> service             (services/*.py)      all business logic; takes a Session
            -> repositories   (db/repositories.py) SQLAlchemy -> plain dicts
            -> models         (db/models.py)       ORM tables
  -> exception handlers       (main.py)            {detail, request_id}, no stack leaks
```

The rule of thumb the codebase follows: **routers contain no business logic.**
They parse the request, pick `lang`, call one service function, and map the
result onto a Pydantic response model. Anything with a decision in it lives in a
service.

## Files

| File | Role |
|---|---|
| `main.py` | App factory, router registration, lifespan logging, CORS, global exception handlers, `/api/health` + `/live` + `/ready` (the last pings the DB). |
| `config.py` | The **only** place the environment is read. `pydantic-settings` `Settings`, imported everywhere as `settings`. `groq_enabled` is derived here. |
| `schemas.py` | All request/response Pydantic models. |
| `middleware.py` | `RequestIDMiddleware` — request-id generation + structlog context. |
| `logging_config.py` | structlog JSON logging setup (`configure_logging`, `get_logger`). |
| `rate_limit.py` | slowapi `limiter` instance and the shared limit strings. |
| `db/` | Engine, session, ORM models, read repositories. See `db/explanation.md`. |
| `routers/` | HTTP surface, one module per resource. See `routers/explanation.md`. |
| `services/` | Business logic (scoring, tier fallback, eligibility, episodes, auth). See `services/explanation.md`. |
| `data/seed/` | Git-tracked JSON fixtures loaded by `seed.py`. See `data/seed/explanation.md`. |
| `seed.py` | Idempotent `app/data/seed/*.json -> Postgres` upsert. `python -m app.seed [--fresh]`. Only reference tables; never touches user data. |

## Startup (containers)

`entrypoint.sh` runs `alembic upgrade head` then `python -m app.seed` before
Uvicorn, so a fresh container comes up migrated and seeded.
