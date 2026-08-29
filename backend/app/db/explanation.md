# `backend/app/db/` — datastore layer

SQLAlchemy 2.0 (sync, `psycopg` v3) + Alembic. The same model metadata builds a
**Postgres** schema in prod and a throwaway **SQLite** schema for the unit tests,
so only *portable* column types are used (`JSON`, never `JSONB`/`ARRAY`).

## Files

| File | Role |
|---|---|
| `base.py` | The declarative `Base`. |
| `models.py` | All ORM tables. Column names deliberately mirror the original seed-JSON keys so services and response schemas needed almost no change when the data moved from files to Postgres. |
| `session.py` | `engine` + `SessionLocal` + the `get_db` FastAPI dependency (request-scoped session, always closed). `pool_pre_ping=True` for Postgres (recycles dropped connections); SQLite gets `check_same_thread=False` instead. |
| `repositories.py` | Read helpers that run `select(...)` and return **plain dicts** in the exact shape the deleted `data_loader.py` used to produce. This keeps the scoring/tier/eligibility services decoupled from the ORM. |

## Tables

Reference data (seeded, idempotent — see `../data/seed/explanation.md`):
`treatments`, `cost_records`, `national_references`, `hospitals`, `schemes`.

Application data (never touched by the seed loader):
`users` (`is_admin` flag), `auth_sessions`, `password_reset_tokens`,
`bill_analyses`, `cost_contributions`, `saved_estimates`.

## Migrations

`backend/alembic/versions/`:

- `0001_initial_schema.py` — baseline (all reference + auth + bill tables).
- `0002_contributions_saved_admin.py` — `cost_contributions`, `saved_estimates`, `users.is_admin`.

CI runs `alembic upgrade head` then `alembic check` (models must match
migrations — regenerate with `make revision m="..."` if `check` fails).
Containers run `alembic upgrade head` on startup via `entrypoint.sh`.
