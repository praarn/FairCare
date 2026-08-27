
from pydantic import BaseModel, Field


class Treatment(BaseModel):
    id: str
    name: str
    name_hi: str | None = None
    category: str
    category_hi: str | None = None
    aliases: list[str] = []
    typical_duration: str
    description: str


class CostRecordOut(BaseModel):
    id: str
    treatment_id: str
    city: str
    state: str
    hospital_type: str
    cost_min: float
    cost_max: float
    cost_avg: float
    sample_size: int
    source: str
    data_year: int


class PredictCostRequest(BaseModel):
    treatment_id: str
    city: str | None = None
    state: str | None = None
    hospital_type: str | None = None  # govt | private_low | private_mid | private_high
    lang: str | None = "en"  # "en" | "hi"


class Estimate(BaseModel):
    cost_min: float
    cost_max: float
    cost_avg: float
    confidence_score: float = Field(..., ge=0, le=1)
    confidence_label: str  # "low" | "medium" | "high"
    is_fallback: bool
    fallback_reason: str | None = None


class Factor(BaseModel):
    label: str
    detail: str


class PredictCostResponse(BaseModel):
    treatment: Treatment
    city: str | None = None
    state: str | None = None
    hospital_type: str | None
    estimate: Estimate
    factors: list[Factor]
    sources: list[CostRecordOut]
    disclaimer: str


class HospitalOut(BaseModel):
    id: str
    name: str
    type: str
    city: str
    state: str
    lat: float
    lng: float
    contact: str
    empanelled_schemes: list[str]
    basic_rating: float
    cost_avg: float | None = None
    cost_source: str | None = None
    source: str


class SchemeEligibilityRequest(BaseModel):
    annual_household_income: float | None = None
    state: str | None = None
    is_govt_employee_or_pensioner: bool = False


class SchemeEligibilityResult(BaseModel):
    scheme_id: str
    name: str
    eligible: bool
    reason: str
    coverage_details: str
    application_steps: list[str]
    official_link: str
    note: str


# ---------- Auth ----------

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    is_admin: bool = False


class AuthResponse(BaseModel):
    token: str
    user: UserOut


class ForgotPasswordRequest(BaseModel):
    email: str


class ForgotPasswordResponse(BaseModel):
    message: str
    reset_token: str | None = None
    note: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


# ---------- Multimodal ----------

class MultimodalStatus(BaseModel):
    vision: bool
    transcription: bool
    text: bool = False
    vision_model: str | None = None
    transcription_model: str | None = None
    text_model: str | None = None


class TranscriptionResponse(BaseModel):
    text: str
    language: str | None = None


class BillLineItem(BaseModel):
    description: str = ""
    amount: float | None = None


class ExtractedBillOut(BaseModel):
    hospital_name: str | None = None
    document_type: str = "other"
    detected_treatment: str | None = None
    line_items: list[BillLineItem] = []
    total_amount: float | None = None
    currency: str = "INR"
    notes: str | None = None


class BillAnalysisResponse(BaseModel):
    extracted: ExtractedBillOut
    effective_total: float | None = None
    matched_treatment: Treatment | None = None
    our_estimate: Estimate | None = None
    verdict: str  # "within" | "above" | "below" | "unknown"
    disclaimer: str


# ---------- Estimate explainer (Groq text model) ----------

class ExplainEstimateRequest(BaseModel):
    treatment_id: str
    city: str | None = None
    state: str | None = None
    hospital_type: str | None = None
    lang: str | None = "en"
    line_items: list[BillLineItem] = []


class ExplanationLineItemNote(BaseModel):
    item: str
    note: str


class EstimateExplanationOut(BaseModel):
    summary: str
    line_item_notes: list[ExplanationLineItemNote] = []
    questions_to_ask: list[str] = []
    scheme_hint: str | None = None
    disclaimer: str


# ---------- Crowd-sourced cost contributions ----------

class ContributionCreate(BaseModel):
    amount: float = Field(..., gt=0)
    treatment_id: str | None = None
    city: str | None = None
    state: str | None = None
    hospital_type: str | None = None
    hospital_name: str | None = None
    line_items: list[BillLineItem] = []
    source_note: str | None = None


class ContributionCreateResponse(BaseModel):
    status: str
    id: str


class ContributionOut(BaseModel):
    id: str
    created_at: str | None = None
    user_id: str | None = None
    treatment_id: str | None = None
    city: str | None = None
    state: str | None = None
    hospital_type: str | None = None
    hospital_name: str | None = None
    amount: float
    line_items: list[BillLineItem] = []
    source_note: str = ""
    status: str
    reviewed_at: str | None = None
    reviewed_by: str | None = None
    promoted_cost_record_id: str | None = None


class ContributionApprove(BaseModel):
    treatment_id: str | None = None
    city: str | None = None
    state: str | None = None
    hospital_type: str | None = None
    cost_min: float | None = None
    cost_max: float | None = None


class ContributionApproveResponse(BaseModel):
    contribution: ContributionOut
    cost_record_id: str


# ---------- Saved estimates ----------

class SavedEstimateCreate(BaseModel):
    treatment_id: str
    city: str | None = None
    state: str | None = None
    hospital_type: str | None = None
    label: str | None = None
    note: str | None = None
    lang: str | None = "en"


class EstimateDrift(BaseModel):
    current_avg: float
    delta_pct: float
    direction: str  # "up" | "down" | "flat"


class SavedEstimateOut(BaseModel):
    id: str
    created_at: str | None = None
    treatment_id: str
    treatment_name: str
    city: str | None = None
    state: str | None = None
    hospital_type: str | None = None
    label: str | None = None
    note: str = ""
    cost_min: float
    cost_avg: float
    cost_max: float
    confidence_label: str
    lang: str = "en"
    drift: EstimateDrift | None = None


# ---------- Episode / multi-treatment estimator ----------

class EpisodeItem(BaseModel):
    treatment_id: str
    quantity: int = Field(default=1, ge=1, le=50)


class EpisodeRequest(BaseModel):
    items: list[EpisodeItem] = Field(..., min_length=1, max_length=12)
    city: str | None = None
    state: str | None = None
    hospital_type: str | None = None
    lang: str | None = "en"
    annual_household_income: float | None = None
    is_govt_employee_or_pensioner: bool = False


class EpisodeLine(BaseModel):
    treatment: Treatment
    quantity: int
    estimate: Estimate
    line_min: float
    line_avg: float
    line_max: float


class EpisodeSkipped(BaseModel):
    treatment_id: str
    quantity: int
    reason: str


class EpisodeTotals(BaseModel):
    cost_min: float
    cost_avg: float
    cost_max: float
    confidence_label: str


class EpisodeEligibleScheme(BaseModel):
    scheme_id: str
    name: str
    coverage_details: str


class EpisodeResponse(BaseModel):
    lines: list[EpisodeLine]
    skipped: list[EpisodeSkipped]
    totals: EpisodeTotals
    eligible_schemes: list[EpisodeEligibleScheme]
    disclaimer: str
