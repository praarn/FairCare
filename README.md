# Running the Project

Two servers must run at the same time, in **two separate terminals**:
- Backend (FastAPI) → `http://localhost:8000` (or `http://127.0.0.1:8000`)
- Frontend (Next.js) → `http://localhost:3000`

Start the backend first, then the frontend, in the exact order below for your OS.

---

## Windows (PowerShell / CMD)

**Terminal 1 — Backend**
```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend**
```
cd frontend
copy .env.local.example .env.local
npm install
npm run dev
```

---

## macOS

**Terminal 1 — Backend**
```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend**
```
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

---

## Linux

**Terminal 1 — Backend**
```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend**
```
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

---

## After both are running

1. Backend docs: http://localhost:8000/docs
2. Frontend app: http://localhost:3000

## Stopping the servers

Press `Ctrl + C` in each terminal. On Windows, deactivate the virtual environment afterward with:
```
deactivate
```
(same command on macOS/Linux)

## Re-running later (venv/node_modules already set up)

**Windows**
```
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```
```
cd frontend
npm run dev
```

**macOS / Linux**
```
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```
```
cd frontend
npm run dev
```
