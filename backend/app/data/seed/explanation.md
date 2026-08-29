# `backend/app/data/seed/` — reference fixtures

Git-tracked JSON that `python -m app.seed` upserts into Postgres (idempotent —
match on primary key, insert or update). Only the five **reference** tables are
seeded; user / session / contribution / saved-estimate tables are never touched.

| File | Table | Rows | Notes |
|---|---|---|---|
| `treatments.json` | `treatments` | 27 | id, EN/HI name + category, aliases, symptom list, typical duration, description. |
| `cost_records.json` | `cost_records` | 526 | Per city × hospital-type cost rows across 7 cities. **Generated**, not hand-written — see below. Every row's `source` string says so explicitly. |
| `national_reference.json` | `national_references` | 10 | Genuinely-sourced national rate references (CGHS / PM-JAY style). Used as the last tier in `cost_service`'s fallback. |
| `hospitals.json` | `hospitals` | 38 | Name, type, city/state, coordinates, treatments offered, empanelled schemes, basic rating. |
| `schemes.json` | `schemes` | 9 | PM-JAY, CGHS + 7 state schemes. Eligibility rules + qualitative coverage text (no per-procedure rupee caps). |

## Regenerating `cost_records.json`

```
cd backend
python -m scripts.generate_seed_costs   # rewrites app/data/seed/cost_records.json
python -m app.seed                       # upsert into the DB
```

`scripts/generate_seed_costs.py` holds a deterministic base-rate table plus
city / hospital-type multipliers. Edit those and re-run. The output is labelled
sample data on purpose: it is **not** real invoice data and must be replaced with
CGHS / PM-JAY / state-tariff data before any production use.

## `--fresh`

`python -m app.seed --fresh` deletes the reference tables first, then reloads —
use it when you've *removed* rows from a fixture (plain `seed` only adds/updates).
