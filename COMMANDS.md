# Commands

Every command needed to run, test, and operate this project. Run from the repo root unless noted.

---

## 1. Run with Docker (recommended)

Requires Docker with Compose v2.

```bash
cp .env.example .env          # first time only; optionally add a real GROQ_API_KEY
docker compose up --build -d  # build + start db, backend, frontend
```

The backend container automatically runs `alembic upgrade head` and seeds reference data before starting Uvicorn.

- Frontend  → http://localhost:3000
- API docs  → http://localhost:8000/docs
- Health    → http://localhost:8000/api/health

### Manage the stack

```bash
docker compose ps                  # container status
docker compose logs -f             # tail all logs
docker compose logs -f backend     # tail one service
docker compose restart backend     # restart one service
docker compose down                # stop + remove containers (keeps DB volume)
docker compose down -v             # stop + wipe the pgdata volume
docker compose build --no-cache    # rebuild images from scratch
```

### Database / migrations (inside containers)

```bash
docker compose exec backend alembic upgrade head   # apply migrations
docker compose exec backend alembic current        # show migration state
docker compose exec backend python -m app.seed     # re-seed reference data
docker compose exec backend python -m app.seed --fresh   # wipe + re-seed reference tables
docker compose exec db psql -U faircare -d faircare      # psql shell
```

### Grant a user admin access (contribution review)

`/contribute/review` and the `GET/POST /api/contributions` review endpoints require
`users.is_admin = true`. Sign the account up through the app first, then:

```bash
make admin email=you@example.com
# or directly:
docker compose exec db psql -U faircare -d faircare \
  -c "UPDATE users SET is_admin = true WHERE email = 'you@example.com';"
```

Log out and back in so the fresh session carries the flag.

---

## 2. Run without Docker (bare metal)

Needs local PostgreSQL 16 and Node 22.

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate                 # Windows  (source venv/bin/activate on macOS/Linux)
pip install -r requirements-dev.txt
cp .env.example .env                  # set DATABASE_URL to your local Postgres
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev                           # dev server on http://localhost:3000
```

---

## 3. Tests, lint, type-checks

Dev dependencies (pytest, ruff) are **not** in the Docker image — run these against the bare-metal `backend/venv`.

### Backend

```bash
cd backend
venv/Scripts/python.exe -m pytest -q          # test suite  (venv/bin/python on macOS/Linux)
venv/Scripts/python.exe -m ruff check .        # lint
venv/Scripts/python.exe -m ruff check --fix .  # lint + autofix
```

### Frontend

```bash
cd frontend
npx tsc --noEmit      # type-check  (also: npm run typecheck)
npm run build         # production build
```

---

## 4. Regenerate / expand seed data

```bash
cd backend
python -m scripts.generate_seed_costs   # rewrites app/data/seed/cost_records.json
python -m app.seed                       # upsert fixtures into the DB (idempotent)
```

Edit the base-rate table / multipliers in `backend/scripts/generate_seed_costs.py`, then re-run.

---

## 5. Create a new migration

```bash
cd backend
venv/Scripts/python.exe -m alembic revision --autogenerate -m "describe the change"
venv/Scripts/python.exe -m alembic upgrade head
```

---

## 6. Makefile shortcuts

`make` wraps the common tasks (may not be on PATH on Windows — use the raw commands above if so).

```bash
make help              # list all targets
make up                # docker compose up --build -d
make down               # docker compose down
make logs               # tail logs
make ps                 # container status
make psql               # psql shell in the db container
make migrate            # alembic upgrade head (in container)
make seed               # re-run the seed loader (in container)
make backend-install    # create backend/venv + install dev deps
make backend-test       # pytest
make lint               # ruff check
make fmt                # ruff check --fix
make dev-backend        # uvicorn with reload (needs local Postgres)
make dev-frontend       # next dev
make frontend-install   # npm ci in frontend/
```

---

## 7. Smoke-test the running API

```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/health/ready
curl http://localhost:8000/api/multimodal/status
curl "http://localhost:8000/api/treatments/search?q=dialysis"
curl -X POST http://localhost:8000/api/predict-cost \
  -H "Content-Type: application/json" \
  -d '{"treatment_id":"t_dialysis","city":"Mumbai","hospital_type":"private"}'
curl "http://localhost:8000/api/hospitals?treatment_id=t_dialysis&city=Mumbai"
curl "http://localhost:8000/api/schemes/eligible?annual_household_income=300000&state=Maharashtra&is_govt_employee_or_pensioner=false"
curl "http://localhost:8000/api/treatments/search-symptoms?q=chest%20pain%20and%20shortness%20of%20breath"
```

### New feature endpoints

```bash
# Multi-treatment "episode" estimate (no auth)
curl -X POST http://localhost:8000/api/estimate-episode \
  -H "Content-Type: application/json" \
  -d '{"items":[{"treatment_id":"t_dialysis","quantity":12},{"treatment_id":"t_knee_replacement","quantity":1}],"city":"Mumbai"}'

# Crowd-sourced contribution (anonymous submit)
curl -X POST http://localhost:8000/api/contributions \
  -H "Content-Type: application/json" \
  -d '{"treatment_id":"t_dialysis","city":"Mumbai","amount":42000}'

# Admin review (needs a bearer token for an is_admin account)
TOK=... ; CID=...
curl "http://localhost:8000/api/contributions?status=pending" -H "Authorization: Bearer $TOK"
curl -X POST "http://localhost:8000/api/contributions/$CID/approve" \
  -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
  -d '{"treatment_id":"t_dialysis","city":"Mumbai","state":"Maharashtra","hospital_type":"private_mid"}'

# Saved estimates (needs any logged-in bearer token)
curl -X POST http://localhost:8000/api/saved-estimates \
  -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
  -d '{"treatment_id":"t_knee_replacement","city":"Mumbai","label":"Mrs. Rao"}'
curl http://localhost:8000/api/saved-estimates -H "Authorization: Bearer $TOK"

# AI estimate explainer (needs GROQ_API_KEY set)
curl -X POST http://localhost:8000/api/multimodal/explain-estimate \
  -H "Content-Type: application/json" \
  -d '{"treatment_id":"t_knee_replacement","city":"Mumbai"}'
```
