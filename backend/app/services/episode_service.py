"""Multi-treatment "care episode" estimator.

Reuses ``cost_service.estimate_cost`` per line item (multiplied by a quantity),
sums the per-line ranges, and — when household details are supplied — reuses
``scheme_service.check_eligibility`` to surface which schemes *may* apply.

Scheme coverage stays qualitative: the seed schemes carry no per-procedure
rupee caps, so inventing a "covered amount" would violate the app's data-honesty
rule. We list eligible schemes and their coverage text; the arithmetic stops at
the pre-scheme total.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.services import cost_service, scheme_service, treatment_service

_CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}

DISCLAIMER_EN = (
    "This adds up per-treatment estimates, each built from limited sample data. "
    "A real episode's cost depends on complications, admission length, and how "
    "procedures are billed together. Confirm with the hospital and involve a doctor."
)
DISCLAIMER_HI = (
    "यह प्रति-इलाज अनुमानों को जोड़ता है, जिनमें से हर एक सीमित नमूना डेटा पर आधारित है। "
    "किसी वास्तविक एपिसोड की लागत जटिलताओं, भर्ती की अवधि और बिलिंग के तरीके पर निर्भर करती है। "
    "अस्पताल से पुष्टि करें और डॉक्टर की सलाह लें।"
)


def estimate_episode(
    db: Session,
    items: list[dict],
    *,
    city: str | None = None,
    state: str | None = None,
    hospital_type: str | None = None,
    lang: str = "en",
    annual_household_income: float | None = None,
    is_govt_employee_or_pensioner: bool = False,
) -> dict:
    lines: list[dict] = []
    skipped: list[dict] = []
    total_min = total_avg = total_max = 0.0
    weakest_rank = _CONFIDENCE_RANK["high"]
    saw_line = False

    for item in items:
        treatment_id = item["treatment_id"]
        quantity = int(item.get("quantity", 1))

        treatment = treatment_service.get_treatment_by_id(db, treatment_id)
        if not treatment:
            skipped.append(
                {
                    "treatment_id": treatment_id,
                    "quantity": quantity,
                    "reason": "Unknown treatment.",
                }
            )
            continue

        result = cost_service.estimate_cost(
            db, treatment_id, city, state, hospital_type, lang=lang
        )
        est = result.get("estimate")
        if not est:
            skipped.append(
                {
                    "treatment_id": treatment_id,
                    "quantity": quantity,
                    "reason": result.get("fallback_reason")
                    or "No cost data for this treatment and location.",
                }
            )
            continue

        line_min = round(est["cost_min"] * quantity, 2)
        line_avg = round(est["cost_avg"] * quantity, 2)
        line_max = round(est["cost_max"] * quantity, 2)
        total_min += line_min
        total_avg += line_avg
        total_max += line_max
        weakest_rank = min(
            weakest_rank, _CONFIDENCE_RANK.get(est["confidence_label"], 0)
        )
        saw_line = True

        lines.append(
            {
                "treatment": treatment,
                "quantity": quantity,
                "estimate": est,
                "line_min": line_min,
                "line_avg": line_avg,
                "line_max": line_max,
            }
        )

    confidence_label = (
        next(k for k, v in _CONFIDENCE_RANK.items() if v == weakest_rank)
        if saw_line
        else "low"
    )

    eligible_schemes: list[dict] = []
    if annual_household_income is not None or is_govt_employee_or_pensioner:
        for s in scheme_service.check_eligibility(
            db,
            annual_household_income,
            state,
            is_govt_employee_or_pensioner,
        ):
            if s["eligible"]:
                eligible_schemes.append(
                    {
                        "scheme_id": s["scheme_id"],
                        "name": s["name"],
                        "coverage_details": s["coverage_details"],
                    }
                )

    return {
        "lines": lines,
        "skipped": skipped,
        "totals": {
            "cost_min": round(total_min, 2),
            "cost_avg": round(total_avg, 2),
            "cost_max": round(total_max, 2),
            "confidence_label": confidence_label,
        },
        "eligible_schemes": eligible_schemes,
        "disclaimer": DISCLAIMER_HI if lang == "hi" else DISCLAIMER_EN,
    }
