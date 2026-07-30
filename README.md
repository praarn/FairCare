# Healthcare Cost Predictor — Step 1 (MVP)

This is Phase 2 of the build plan: treatment input → rule-based cost lookup →
hospital list → static scheme matching. No ML model and no LLM yet — those
come in a later phase, once the trust/transparency UX here is proven out.

**Important:** all figures in `backend/app/data/*.json` are placeholder
sample data, clearly labeled `"SAMPLE DATA"` in the `source` field. Before any
real use, replace these with sourced CGHS / PM-JAY / state tariff data per
the plan's Section 5 — never fill gaps with invented numbers.

## Running the backend (FastAPI)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Visit http://localhost:8000/docs for interactive API docs.

## Running the frontend (Next.js)

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Visit http://localhost:3000.

## Project flow

1. **Homepage** (`/`) — search a treatment, pick a city, optionally a
   hospital-type preference.
2. **Results** (`/results`) — cost gauge (min/typical/high), a confidence
   badge that's visually distinct per tier (not just a caveat), an
   expandable "why this estimate" panel with factors + raw sources, and a
   persistent disclaimer.
3. **Hospitals** (`/hospitals`) — ranked list, government/empanelled options
   shown first and visually marked with a stamp badge.

## API endpoints

```
GET  /api/treatments/search?q=
POST /api/predict-cost        { treatment_id, city, hospital_type? }
GET  /api/hospitals?treatment_id=&city=&type=&budget_mode=
GET  /api/schemes/eligible?annual_household_income=&state=&is_govt_employee_or_pensioner=
```

## What's deliberately NOT here yet (next steps, per the phased plan)

- **Phase 1 (data foundation)**: swap the JSON files for real CGHS/PM-JAY
  rate lists and empanelled hospital directories, backed by Postgres/Supabase
  per the schema in the plan.
- **Phase 3 (modeling layer)**: train the XGBoost/LightGBM regression model
  once there's enough real `cost_records` volume to justify it; add the
  Claude explanation layer with strict JSON-schema validation so it can
  never introduce or alter a number.
- **Phase 4 (differentiators)**: Budget Mode UI toggle (the backend already
  supports `budget_mode=true` on `/api/hospitals`), map view, multilingual
  support, voice input, EMI/loan info, and a full Treatment Comparison page.
- **Trust hardening**: gate the disclaimer behind an explicit "I understand"
  acknowledgment (currently it's persistent but not acknowledgment-gated),
  and add the post-generation number-drift check once Claude's explanation
  layer is added.

Say what to build next — e.g. "add the comparison page" or "wire up
Postgres" — and we'll keep going step by step.
