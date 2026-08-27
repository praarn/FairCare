export interface User {
  id: string;
  name: string;
  email: string;
  is_admin?: boolean;
}

export interface Treatment {
  id: string;
  name: string;
  name_hi?: string | null;
  category: string;
  category_hi?: string | null;
  aliases: string[];
  typical_duration: string;
  description: string;
}

export interface CostRecordOut {
  id: string;
  treatment_id: string;
  city: string;
  state: string;
  hospital_type: string;
  cost_min: number;
  cost_max: number;
  cost_avg: number;
  sample_size: number;
  source: string;
  data_year: number;
}

export interface Estimate {
  cost_min: number;
  cost_max: number;
  cost_avg: number;
  confidence_score: number;
  confidence_label: "low" | "medium" | "high";
  is_fallback: boolean;
  fallback_reason: string | null;
}

export interface Factor {
  label: string;
  detail: string;
}

export interface PredictCostResponse {
  treatment: Treatment;
  city?: string | null;
  state?: string | null;
  hospital_type: string | null;
  estimate: Estimate;
  factors: Factor[];
  sources: CostRecordOut[];
  disclaimer: string;
}

export interface HospitalOut {
  id: string;
  name: string;
  type: string;
  city: string;
  state: string;
  lat: number;
  lng: number;
  contact: string;
  empanelled_schemes: string[];
  basic_rating: number;
  cost_avg: number | null;
  cost_source: string | null;
  source: string;
}

export const HOSPITAL_TYPE_LABELS: Record<string, string> = {
  govt: "Government",
  private_low: "Private — Low cost",
  private_mid: "Private — Mid range",
  private_high: "Private — Premium",
};

export const CITIES = ["Delhi", "Mumbai", "Bengaluru", "Pune", "Chennai", "Hyderabad", "Kolkata"];

// All 28 states + 8 union territories of India, alphabetical.
export const STATES = [
  "Andaman and Nicobar Islands",
  "Andhra Pradesh",
  "Arunachal Pradesh",
  "Assam",
  "Bihar",
  "Chandigarh",
  "Chhattisgarh",
  "Dadra and Nagar Haveli and Daman and Diu",
  "Delhi",
  "Goa",
  "Gujarat",
  "Haryana",
  "Himachal Pradesh",
  "Jammu and Kashmir",
  "Jharkhand",
  "Karnataka",
  "Kerala",
  "Ladakh",
  "Lakshadweep",
  "Madhya Pradesh",
  "Maharashtra",
  "Manipur",
  "Meghalaya",
  "Mizoram",
  "Nagaland",
  "Odisha",
  "Puducherry",
  "Punjab",
  "Rajasthan",
  "Sikkim",
  "Tamil Nadu",
  "Telangana",
  "Tripura",
  "Uttar Pradesh",
  "Uttarakhand",
  "West Bengal",
];

export interface SchemeResult {
  scheme_id: string;
  name: string;
  eligible: boolean;
  reason: string;
  coverage_details: string;
  application_steps: string[];
  official_link: string;
  note: string;
}

// ---------- Multimodal ----------

export interface MultimodalStatus {
  vision: boolean;
  transcription: boolean;
  text: boolean;
  vision_model: string | null;
  transcription_model: string | null;
  text_model: string | null;
}

export interface TranscriptionResult {
  text: string;
  language: string | null;
}

export interface BillLineItem {
  description: string;
  amount: number | null;
}

export interface ExtractedBill {
  hospital_name: string | null;
  document_type: string;
  detected_treatment: string | null;
  line_items: BillLineItem[];
  total_amount: number | null;
  currency: string;
  notes: string | null;
}

export type BillVerdict = "within" | "above" | "below" | "unknown";

export interface BillAnalysisResult {
  extracted: ExtractedBill;
  effective_total: number | null;
  matched_treatment: Treatment | null;
  our_estimate: Estimate | null;
  verdict: BillVerdict;
  disclaimer: string;
}

// ---------- Estimate explainer ----------

export interface EstimateExplanation {
  summary: string;
  line_item_notes: { item: string; note: string }[];
  questions_to_ask: string[];
  scheme_hint: string | null;
  disclaimer: string;
}

// ---------- Crowd-sourced contributions ----------

export interface ContributionInput {
  amount: number;
  treatment_id?: string;
  city?: string;
  state?: string;
  hospital_type?: string;
  hospital_name?: string;
  line_items?: BillLineItem[];
  source_note?: string;
}

export interface Contribution {
  id: string;
  created_at: string | null;
  user_id: string | null;
  treatment_id: string | null;
  city: string | null;
  state: string | null;
  hospital_type: string | null;
  hospital_name: string | null;
  amount: number;
  line_items: BillLineItem[];
  source_note: string;
  status: "pending" | "approved" | "rejected";
  reviewed_at: string | null;
  reviewed_by: string | null;
  promoted_cost_record_id: string | null;
}

export interface ContributionApproveInput {
  treatment_id?: string;
  city?: string;
  state?: string;
  hospital_type?: string;
  cost_min?: number;
  cost_max?: number;
}

// ---------- Saved estimates ----------

export interface EstimateDrift {
  current_avg: number;
  delta_pct: number;
  direction: "up" | "down" | "flat";
}

export interface SavedEstimate {
  id: string;
  created_at: string | null;
  treatment_id: string;
  treatment_name: string;
  city: string | null;
  state: string | null;
  hospital_type: string | null;
  label: string | null;
  note: string;
  cost_min: number;
  cost_avg: number;
  cost_max: number;
  confidence_label: "low" | "medium" | "high";
  lang: string;
  drift: EstimateDrift | null;
}

export interface SavedEstimateInput {
  treatment_id: string;
  city?: string;
  state?: string;
  hospital_type?: string;
  label?: string;
  note?: string;
  lang?: string;
}

// ---------- Episode estimator ----------

export interface EpisodeItemInput {
  treatment_id: string;
  quantity: number;
}

export interface EpisodeRequestInput {
  items: EpisodeItemInput[];
  city?: string;
  state?: string;
  hospital_type?: string;
  lang?: string;
  annual_household_income?: number;
  is_govt_employee_or_pensioner?: boolean;
}

export interface EpisodeLine {
  treatment: Treatment;
  quantity: number;
  estimate: Estimate;
  line_min: number;
  line_avg: number;
  line_max: number;
}

export interface EpisodeSkipped {
  treatment_id: string;
  quantity: number;
  reason: string;
}

export interface EpisodeResult {
  lines: EpisodeLine[];
  skipped: EpisodeSkipped[];
  totals: {
    cost_min: number;
    cost_avg: number;
    cost_max: number;
    confidence_label: "low" | "medium" | "high";
  };
  eligible_schemes: { scheme_id: string; name: string; coverage_details: string }[];
  disclaimer: string;
}
