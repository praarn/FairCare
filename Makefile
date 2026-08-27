# Healthcare Cost Predictor — common tasks.
# `make help` lists everything.

COMPOSE ?= docker compose
PY ?= python

.DEFAULT_GOAL := help
.PHONY: help up down logs build rebuild ps psql migrate revision seed \
        backend-install backend-test lint fmt dev-backend dev-frontend frontend-install

help: ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

## ---------- docker-compose ----------
up: ## Build (if needed) and start db + backend + frontend
	$(COMPOSE) up --build -d
	@echo "backend  -> http://localhost:8000/docs"
	@echo "frontend -> http://localhost:3000"

down: ## Stop and remove containers (keeps the pgdata volume)
	$(COMPOSE) down

logs: ## Tail logs from all services
	$(COMPOSE) logs -f

rebuild: ## Rebuild images from scratch
	$(COMPOSE) build --no-cache

ps: ## Show container status
	$(COMPOSE) ps

psql: ## Open a psql shell in the db container
	$(COMPOSE) exec db psql -U $${POSTGRES_USER:-sahaj} -d $${POSTGRES_DB:-sahaj}

migrate: ## Run alembic migrations inside the backend container
	$(COMPOSE) exec backend alembic upgrade head

seed: ## Re-run the seed loader inside the backend container
	$(COMPOSE) exec backend $(PY) -m app.seed

## ---------- backend (bare metal) ----------
backend-install: ## Install backend + dev deps into backend/venv
	cd backend && $(PY) -m venv venv && \
		venv/Scripts/pip install -r requirements-dev.txt || \
		venv/bin/pip install -r requirements-dev.txt

backend-test: ## Run the backend test suite
	cd backend && (venv/Scripts/python -m pytest || venv/bin/python -m pytest)

lint: ## Ruff lint the backend
	cd backend && (venv/Scripts/python -m ruff check . || venv/bin/python -m ruff check .)

fmt: ## Ruff auto-fix the backend
	cd backend && (venv/Scripts/python -m ruff check --fix . || venv/bin/python -m ruff check --fix .)

revision: ## Create a new alembic revision:  make revision m="add table x"
	cd backend && (venv/Scripts/python -m alembic revision --autogenerate -m "$(m)" || \
		venv/bin/python -m alembic revision --autogenerate -m "$(m)")

dev-backend: ## Run uvicorn with reload (needs a local Postgres + backend/.env)
	cd backend && (venv/Scripts/python -m uvicorn app.main:app --reload --port 8000 || \
		venv/bin/python -m uvicorn app.main:app --reload --port 8000)

## ---------- frontend (bare metal) ----------
frontend-install: ## npm ci in frontend/
	cd frontend && npm ci

dev-frontend: ## Run the Next.js dev server
	cd frontend && npm run dev
