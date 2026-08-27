import {
  Treatment,
  PredictCostResponse,
  HospitalOut,
  SchemeResult,
  User,
  MultimodalStatus,
  TranscriptionResult,
  BillAnalysisResult,
} from "./types";

// This file's fetch() calls run both in the browser AND server-side (e.g.
// app/layout.tsx calls fetchMe() during SSR on every request).
//
//  * Browser  -> NEXT_PUBLIC_API_BASE_URL (baked at build; the host-published
//    backend port). Defaults to the explicit IPv4 loopback, not "localhost":
//    on Windows, Node resolves "localhost" to IPv6 (::1) first while uvicorn
//    binds IPv4 only, which otherwise causes multi-second SSR timeouts.
//  * Server (SSR) -> API_INTERNAL_BASE_URL when set (runtime, server-only).
//    Inside docker-compose this is "http://backend:8000" — "localhost" there
//    would point at the frontend container itself, not the API.
const API_BASE =
  (typeof window === "undefined" ? process.env.API_INTERNAL_BASE_URL : undefined) ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://127.0.0.1:8000";

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    // FastAPI's own default body for an unmatched route is {"detail":"Not Found"} —
    // that specific combination almost always means the backend hasn't been
    // updated/restarted with a newer route yet, not a real data problem.
    if (res.status === 404 && body.detail === "Not Found") {
      throw new Error(
        `This backend endpoint (${res.url}) doesn't exist yet — the running backend is likely out of date. Update the backend files and restart uvicorn.`
      );
    }
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function searchTreatments(query: string): Promise<Treatment[]> {
  const res = await fetch(`${API_BASE}/api/treatments/search?q=${encodeURIComponent(query)}`, {
    cache: "no-store",
  });
  return handle<Treatment[]>(res);
}

export async function searchTreatmentsBySymptom(query: string): Promise<Treatment[]> {
  const res = await fetch(`${API_BASE}/api/treatments/search-symptoms?q=${encodeURIComponent(query)}`, {
    cache: "no-store",
  });
  return handle<Treatment[]>(res);
}

export async function predictCost(params: {
  treatment_id: string;
  city?: string;
  state?: string;
  hospital_type?: string;
  lang?: string;
}): Promise<PredictCostResponse> {
  const res = await fetch(`${API_BASE}/api/predict-cost`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
    cache: "no-store",
  });
  return handle<PredictCostResponse>(res);
}

export async function fetchHospitals(params: {
  treatment_id: string;
  city?: string;
  type?: string;
  budget_mode?: boolean;
}): Promise<HospitalOut[]> {
  const search = new URLSearchParams();
  search.set("treatment_id", params.treatment_id);
  if (params.city) search.set("city", params.city);
  if (params.type) search.set("type", params.type);
  if (params.budget_mode) search.set("budget_mode", "true");

  const res = await fetch(`${API_BASE}/api/hospitals?${search.toString()}`, {
    cache: "no-store",
  });
  return handle<HospitalOut[]>(res);
}

export async function checkSchemeEligibility(params: {
  annual_household_income?: number;
  state?: string;
  is_govt_employee_or_pensioner?: boolean;
}): Promise<SchemeResult[]> {
  const search = new URLSearchParams();
  if (params.annual_household_income != null) {
    search.set("annual_household_income", String(params.annual_household_income));
  }
  if (params.state) search.set("state", params.state);
  if (params.is_govt_employee_or_pensioner) {
    search.set("is_govt_employee_or_pensioner", "true");
  }

  const res = await fetch(`${API_BASE}/api/schemes/eligible?${search.toString()}`, {
    cache: "no-store",
  });
  return handle<SchemeResult[]>(res);
}

export async function fetchHospitalById(id: string): Promise<HospitalOut> {
  const res = await fetch(`${API_BASE}/api/hospitals/${encodeURIComponent(id)}`, {
    cache: "no-store",
  });
  return handle<HospitalOut>(res);
}

// ---------- Auth ----------

export interface AuthResponse {
  token: string;
  user: User;
}

export async function signup(params: { name: string; email: string; password: string }): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/api/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  return handle<AuthResponse>(res);
}

export async function login(params: { email: string; password: string }): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  return handle<AuthResponse>(res);
}

export async function logout(token: string): Promise<void> {
  await fetch(`${API_BASE}/api/auth/logout`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function fetchMe(token: string): Promise<User> {
  const res = await fetch(`${API_BASE}/api/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  return handle<User>(res);
}

export async function forgotPassword(email: string): Promise<{ message: string; reset_token: string | null; note: string }> {
  const res = await fetch(`${API_BASE}/api/auth/forgot-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  return handle(res);
}

export async function resetPassword(token: string, new_password: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/auth/reset-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, new_password }),
  });
  await handle(res);
}

// ---------- Multimodal ----------

export async function multimodalStatus(): Promise<MultimodalStatus> {
  const res = await fetch(`${API_BASE}/api/multimodal/status`, { cache: "no-store" });
  return handle<MultimodalStatus>(res);
}

export async function analyzeBill(
  file: Blob,
  opts: { city?: string; treatment_id?: string; lang?: string } = {}
): Promise<BillAnalysisResult> {
  const form = new FormData();
  form.append("file", file, "bill.jpg");
  if (opts.city) form.append("city", opts.city);
  if (opts.treatment_id) form.append("treatment_id", opts.treatment_id);
  form.append("lang", opts.lang || "en");

  const res = await fetch(`${API_BASE}/api/multimodal/analyze-bill`, {
    method: "POST",
    body: form,
    cache: "no-store",
  });
  return handle<BillAnalysisResult>(res);
}

export async function transcribeAudio(
  blob: Blob,
  lang: string = "en"
): Promise<TranscriptionResult> {
  const form = new FormData();
  const ext = blob.type.includes("ogg") ? "ogg" : blob.type.includes("wav") ? "wav" : "webm";
  form.append("file", blob, `clip.${ext}`);
  form.append("lang", lang);

  const res = await fetch(`${API_BASE}/api/multimodal/transcribe`, {
    method: "POST",
    body: form,
    cache: "no-store",
  });
  return handle<TranscriptionResult>(res);
}