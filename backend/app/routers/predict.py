from fastapi import APIRouter, HTTPException
from app.schemas import PredictCostRequest, PredictCostResponse
from app.services.treatment_service import get_treatment_by_id
from app.services.cost_service import estimate_cost

router = APIRouter(prefix="/api/predict-cost", tags=["predict"])

STANDARD_DISCLAIMER_EN = (
    "This is an estimate built from limited sample data, not an exact price. "
    "Actual costs vary by hospital, complexity, and admission length. "
    "Please confirm final costs with the hospital and involve a doctor in any treatment decision."
)

STANDARD_DISCLAIMER_HI = (
    "यह सीमित नमूना डेटा पर आधारित एक अनुमान है, सटीक कीमत नहीं। "
    "वास्तविक लागत अस्पताल, जटिलता और भर्ती की अवधि के अनुसार बदलती है। "
    "कृपया अंतिम लागत की पुष्टि अस्पताल से करें और किसी भी इलाज के फैसले में डॉक्टर की सलाह लें।"
)


@router.post("", response_model=PredictCostResponse)
def predict_cost(payload: PredictCostRequest):
    treatment = get_treatment_by_id(payload.treatment_id)
    if not treatment:
        raise HTTPException(status_code=404, detail="Unknown treatment_id")

    if not payload.city and not payload.state:
        raise HTTPException(status_code=400, detail="Provide at least a city or a state/UT.")

    lang = payload.lang if payload.lang in ("en", "hi") else "en"

    result = estimate_cost(
        payload.treatment_id, payload.city, payload.state, payload.hospital_type, lang=lang
    )

    if result["estimate"] is None:
        raise HTTPException(
            status_code=404,
            detail="Not enough verified data for this treatment to produce any estimate.",
        )

    return PredictCostResponse(
        treatment=treatment,
        city=payload.city,
        state=payload.state,
        hospital_type=payload.hospital_type,
        estimate=result["estimate"],
        factors=result["factors"],
        sources=result["matched_records"],
        disclaimer=STANDARD_DISCLAIMER_HI if lang == "hi" else STANDARD_DISCLAIMER_EN,
    )
