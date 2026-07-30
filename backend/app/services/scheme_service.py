from typing import List, Dict, Optional
from .data_loader import load_schemes


def check_eligibility(
    annual_household_income: Optional[float],
    state: Optional[str],
    is_govt_employee_or_pensioner: bool,
) -> List[Dict]:
    """
    Plain deterministic rules — intentionally not an LLM call. Insurance/scheme
    eligibility is factually and legally sensitive, so this stays auditable
    and unit-testable rule-by-rule.
    """
    results = []
    for scheme in load_schemes():
        rules = scheme["eligibility_rules"]
        eligible = True
        reasons = []

        if "max_annual_household_income" in rules:
            if annual_household_income is None:
                eligible = False
                reasons.append("Income not provided — cannot confirm income-based eligibility.")
            elif annual_household_income > rules["max_annual_household_income"]:
                eligible = False
                reasons.append(
                    f"Household income exceeds the Rs. {rules['max_annual_household_income']:,} threshold used by this scheme."
                )
            else:
                reasons.append(
                    f"Household income is within the Rs. {rules['max_annual_household_income']:,} threshold."
                )

        if "states_included" in rules:
            if not state or state not in rules["states_included"]:
                eligible = False
                reasons.append(f"This scheme is limited to: {', '.join(rules['states_included'])}.")
            else:
                reasons.append(f"{state} is covered by this scheme.")

        if rules.get("requires_govt_employment_or_pension"):
            if not is_govt_employee_or_pensioner:
                eligible = False
                reasons.append("This scheme requires current or retired central government employment.")
            else:
                reasons.append("Government employment/pension status matches this scheme's requirement.")

        results.append({
            "scheme_id": scheme["id"],
            "name": scheme["name"],
            "eligible": eligible,
            "reason": " ".join(reasons) if reasons else "No specific criteria to check.",
            "coverage_details": scheme["coverage_details"],
            "application_steps": scheme["application_steps"],
            "official_link": scheme["official_link"],
            "note": scheme["note"],
        })

    return results
