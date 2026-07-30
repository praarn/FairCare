from typing import List, Optional
from pydantic import BaseModel, Field


class Treatment(BaseModel):
    id: str
    name: str
    name_hi: Optional[str] = None
    category: str
    category_hi: Optional[str] = None
    aliases: List[str] = []
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
    city: Optional[str] = None
    state: Optional[str] = None
    hospital_type: Optional[str] = None  # govt | private_low | private_mid | private_high
    lang: Optional[str] = "en"  # "en" | "hi"


class Estimate(BaseModel):
    cost_min: float
    cost_max: float
    cost_avg: float
    confidence_score: float = Field(..., ge=0, le=1)
    confidence_label: str  # "low" | "medium" | "high"
    is_fallback: bool
    fallback_reason: Optional[str] = None


class Factor(BaseModel):
    label: str
    detail: str


class PredictCostResponse(BaseModel):
    treatment: Treatment
    city: Optional[str] = None
    state: Optional[str] = None
    hospital_type: Optional[str]
    estimate: Estimate
    factors: List[Factor]
    sources: List[CostRecordOut]
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
    empanelled_schemes: List[str]
    basic_rating: float
    cost_avg: Optional[float] = None
    cost_source: Optional[str] = None
    source: str


class SchemeEligibilityRequest(BaseModel):
    annual_household_income: Optional[float] = None
    state: Optional[str] = None
    is_govt_employee_or_pensioner: bool = False


class SchemeEligibilityResult(BaseModel):
    scheme_id: str
    name: str
    eligible: bool
    reason: str
    coverage_details: str
    application_steps: List[str]
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


class AuthResponse(BaseModel):
    token: str
    user: UserOut


class ForgotPasswordRequest(BaseModel):
    email: str


class ForgotPasswordResponse(BaseModel):
    message: str
    reset_token: Optional[str] = None
    note: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
