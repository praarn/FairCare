from datetime import date

from sqlalchemy.orm import Session

from app.db import repositories

CURRENT_YEAR = date.today().year


def _size_score(sample_size: int) -> float:
    return min(sample_size / 100.0, 1.0)


def _recency_score(data_year: int) -> float:
    age = max(CURRENT_YEAR - data_year, 0)
    if age == 0:
        return 1.0
    if age == 1:
        return 0.85
    if age == 2:
        return 0.7
    if age == 3:
        return 0.55
    return 0.4


def _confidence_label(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def _weighted_estimate(records: list[dict]) -> dict:
    """Pool multiple cost_records rows into one estimate, weighted by sample_size."""
    total_weight = sum(r["sample_size"] for r in records) or 1
    cost_min = min(r["cost_min"] for r in records)
    cost_max = max(r["cost_max"] for r in records)
    cost_avg = sum(r["cost_avg"] * r["sample_size"] for r in records) / total_weight

    total_sample_size = sum(r["sample_size"] for r in records)
    avg_year = sum(r["data_year"] * r["sample_size"] for r in records) / total_weight

    score = 0.6 * _size_score(total_sample_size) + 0.4 * _recency_score(round(avg_year))
    return {
        "cost_min": round(cost_min, 2),
        "cost_max": round(cost_max, 2),
        "cost_avg": round(cost_avg, 2),
        "confidence_score": round(score, 2),
        "confidence_label": _confidence_label(score),
    }


def _national_reference_record(
    nat_ref: dict[str, dict], treatment_id: str, hospital_type: str | None
) -> dict | None:
    """
    Returns a synthetic single 'record' built from a genuinely-sourced
    national reference entry, if one exists for this treatment. This is NOT
    pooled sample data — it's a cited government package rate, deliberately
    only present for the treatments where real research actually turned up a
    verifiable figure. PM-JAY/CGHS rates are the same nationwide, which is
    exactly why one entry here correctly covers all 36 states/UTs rather than
    faking per-state variation that doesn't really exist.
    """
    entry_by_type = nat_ref.get(treatment_id)
    if not entry_by_type:
        return None
    entry = (hospital_type and entry_by_type.get(hospital_type)) or entry_by_type.get("govt")
    if not entry:
        return None
    return {
        "id": f"national_ref_{treatment_id}",
        "treatment_id": treatment_id,
        "city": "",
        "state": "",
        "hospital_type": hospital_type or "govt",
        "cost_min": entry["cost_min"],
        "cost_max": entry["cost_max"],
        "cost_avg": entry["cost_avg"],
        "sample_size": entry["sample_size"],
        "source": entry["source"],
        "data_year": entry["data_year"],
    }


def _lookup_state_for_city(all_records: list[dict], city: str) -> str | None:
    for r in all_records:
        if r["city"].lower() == city.lower():
            return r.get("state")
    return None


def _response(est: dict, records: list[dict], factors: list[dict], is_fallback: bool, reason: str | None) -> dict:
    return {
        "estimate": {**est, "is_fallback": is_fallback, "fallback_reason": reason},
        "matched_records": records,
        "factors": factors,
        "is_fallback": is_fallback,
        "fallback_reason": reason,
    }


def estimate_cost(
    db: Session,
    treatment_id: str,
    city: str | None = None,
    state: str | None = None,
    hospital_type: str | None = None,
    lang: str = "en",
) -> dict:
    """
    Rule-based lookup, tried in progressively broader tiers — each one
    discloses exactly which tier produced the number, never silently:

      1. Exact city + hospital type
      2. Exact city, any hospital type
      3. State-wide pool (any city within the given/derived state)
      4. National reference rate (real, cited PM-JAY/CGHS figure — only
         exists for treatments where research actually found one)
      5. National pooled sample average (last resort, honestly labeled
         as sample data, not a verified location-specific figure)
    """
    all_records = repositories.all_cost_records(db)
    nat_ref = repositories.national_reference_map(db)

    by_treatment = [r for r in all_records if r["treatment_id"] == treatment_id]
    has_national_ref = treatment_id in nat_ref

    if not by_treatment and not has_national_ref:
        return {
            "estimate": None,
            "matched_records": [],
            "factors": [],
            "is_fallback": True,
            "fallback_reason": (
                "इस इलाज के लिए अभी तक कोई सत्यापित लागत डेटा उपलब्ध नहीं है।"
                if lang == "hi"
                else "No verified cost data exists for this treatment yet."
            ),
        }

    # Tier 1 & 2: exact city
    if city:
        exact_city = [r for r in by_treatment if r["city"].lower() == city.lower()]
        tier1 = [r for r in exact_city if r["hospital_type"] == hospital_type] if hospital_type else exact_city

        if tier1:
            est = _weighted_estimate(tier1)
            factors = _build_factors(tier1, city, fallback=False, lang=lang)
            return _response(est, tier1, factors, False, None)

        if exact_city:
            est = _weighted_estimate(exact_city)
            factors = _build_factors(exact_city, city, fallback=True, lang=lang)
            reason = _reason_city_any_type(city, hospital_type, lang)
            return _response(est, exact_city, factors, True, reason)

    # Tier 3: state-wide pool
    effective_state = state or (city and _lookup_state_for_city(all_records, city))
    if effective_state:
        state_records = [r for r in by_treatment if r.get("state", "").lower() == effective_state.lower()]

        if hospital_type:
            state_type_records = [r for r in state_records if r["hospital_type"] == hospital_type]
            if state_type_records:
                est = _weighted_estimate(state_type_records)
                factors = _build_factors(state_type_records, effective_state, fallback=True, lang=lang)
                reason = _reason_state(effective_state, hospital_type, lang)
                return _response(est, state_type_records, factors, True, reason)

        if state_records:
            est = _weighted_estimate(state_records)
            factors = _build_factors(state_records, effective_state, fallback=True, lang=lang)
            reason = _reason_state(effective_state, None, lang)
            return _response(est, state_records, factors, True, reason)

    # Tier 4: national reference rate (real, cited)
    national_record = _national_reference_record(nat_ref, treatment_id, hospital_type)
    if national_record:
        est = _weighted_estimate([national_record])
        factors = _build_factors([national_record], "", fallback=True, lang=lang)
        reason = _reason_national_ref(lang)
        return _response(est, [national_record], factors, True, reason)

    # Tier 5: national pooled sample average (last resort)
    if by_treatment:
        est = _weighted_estimate(by_treatment)
        factors = _build_factors(by_treatment, "", fallback=True, lang=lang)
        reason = _reason_national_pool(city or state or "", lang)
        return _response(est, by_treatment, factors, True, reason)

    return {
        "estimate": None,
        "matched_records": [],
        "factors": [],
        "is_fallback": True,
        "fallback_reason": (
            "इस स्थान/इलाज संयोजन के लिए कोई डेटा उपलब्ध नहीं है।"
            if lang == "hi"
            else "No data available for this location/treatment combination."
        ),
    }


def _reason_city_any_type(city: str, hospital_type: str | None, lang: str) -> str:
    if lang == "hi":
        return (
            f"{city} में '{hospital_type}' अस्पतालों का सत्यापित डेटा नहीं है — इसके बजाय "
            f"{city} के सभी अस्पताल प्रकारों की रेंज दिखाई जा रही है।"
            if hospital_type
            else f"{city} के सभी अस्पताल प्रकारों का संयुक्त अनुमान दिखाया जा रहा है।"
        )
    return (
        f"No verified data for '{hospital_type}' hospitals in {city} — "
        f"showing the range across all hospital types in {city} instead."
        if hospital_type
        else f"Showing pooled estimate across all hospital types in {city}."
    )


def _reason_state(state: str, hospital_type: str | None, lang: str) -> str:
    if lang == "hi":
        return (
            f"{state} में सटीक शहर का डेटा नहीं है — इसके बजाय {state} भर में "
            f"'{hospital_type}' अस्पतालों का औसत दिखाया जा रहा है।"
            if hospital_type
            else f"{state} में सटीक शहर का डेटा नहीं है — इसके बजाय {state} भर का संयुक्त अनुमान दिखाया जा रहा है।"
        )
    return (
        f"No exact city match in {state} — showing the average across "
        f"'{hospital_type}' hospitals state-wide instead."
        if hospital_type
        else f"No exact city match in {state} — showing a state-wide pooled estimate instead."
    )


def _reason_national_ref(lang: str) -> str:
    if lang == "hi":
        return (
            "आपके राज्य/शहर के लिए विशिष्ट डेटा नहीं है। यह राष्ट्रीय PM-JAY संदर्भ दर है, जो सभी "
            "राज्यों और केंद्र शासित प्रदेशों में एक समान लागू होती है — सरकारी योजना दरें निजी "
            "अस्पतालों की तरह स्थान के अनुसार नहीं बदलतीं।"
        )
    return (
        "No state/city-specific data available. This is the national PM-JAY reference "
        "rate, which applies uniformly across all states/UTs — government scheme rates "
        "don't vary by location the way private hospital costs do."
    )


def _reason_national_pool(location_label: str, lang: str) -> str:
    if lang == "hi":
        loc_part = f"{location_label} के लिए " if location_label else ""
        return f"{loc_part}पर्याप्त सत्यापित डेटा नहीं है — इसके बजाय उपलब्ध सैंपल डेटा का राष्ट्रीय औसत दिखाया जा रहा है।"
    loc_part = f"for {location_label} " if location_label else ""
    return f"Not enough verified data {loc_part}— showing a national average across available sample data instead."


def _build_factors(records: list[dict], location_label: str, fallback: bool, lang: str = "en") -> list[dict]:
    factors = []
    govt_records = [r for r in records if r["hospital_type"] == "govt"]
    private_records = [r for r in records if r["hospital_type"] != "govt"]

    if govt_records and private_records:
        govt_avg = sum(r["cost_avg"] for r in govt_records) / len(govt_records)
        priv_avg = sum(r["cost_avg"] for r in private_records) / len(private_records)
        if govt_avg > 0:
            pct = round(((priv_avg - govt_avg) / govt_avg) * 100)
            if lang == "hi":
                factors.append({
                    "label": "अस्पताल का प्रकार",
                    "detail": f"इस डेटा में निजी अस्पताल सरकारी अस्पतालों की तुलना में लगभग {pct}% महंगे हैं।"
                })
            else:
                factors.append({
                    "label": "Hospital type",
                    "detail": f"Private hospitals in this data run about {pct}% higher than government hospitals for the same procedure."
                })

    if lang == "hi":
        if location_label:
            location_detail = (
                f"अनुमान {location_label} से जुड़े रिकॉर्ड पर आधारित है।" if not fallback
                else "सटीक स्थान का डेटा उपलब्ध नहीं था, इसलिए व्यापक डेटा का उपयोग किया गया है — ऊपर दिया गया नोट देखें।"
            )
        else:
            location_detail = "यह एक राष्ट्रीय दर/औसत है, किसी विशेष शहर या राज्य पर आधारित नहीं।"
        factors.append({"label": "स्थान", "detail": location_detail})
    else:
        if location_label:
            location_detail = (
                f"Estimate is based on records tagged to {location_label}." if not fallback
                else "Exact location match wasn't available, so a broader pool was used — see the note above."
            )
        else:
            location_detail = "This is a national rate/average, not specific to any one city or state."
        factors.append({"label": "Location", "detail": location_detail})

    total_samples = sum(r["sample_size"] for r in records)
    if lang == "hi":
        factors.append({
            "label": "डेटा की मात्रा",
            "detail": f"{len(records)} सत्यापित डेटा पंक्तियों में {total_samples} रिकॉर्ड से बनाया गया।"
        })
    else:
        factors.append({
            "label": "Data volume",
            "detail": f"Built from {total_samples} pooled records across {len(records)} verified data row(s)."
        })

    return factors
