export interface User {
  id: string;
  name: string;
  email: string;
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
  vision_model: string | null;
  transcription_model: string | null;
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
