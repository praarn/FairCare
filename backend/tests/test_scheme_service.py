"""Deterministic scheme-eligibility rules."""
from app.services.scheme_service import check_eligibility


def _by_id(results):
    return {r["scheme_id"]: r for r in results}


def test_income_within_threshold_passes_pmjay(db):
    res = _by_id(check_eligibility(db, 200000, "Delhi", False))
    assert res["s_pmjay"]["eligible"] is True
    assert "within" in res["s_pmjay"]["reason"].lower()


def test_income_over_threshold_fails_pmjay(db):
    res = _by_id(check_eligibility(db, 400000, "Delhi", False))
    assert res["s_pmjay"]["eligible"] is False
    assert "exceeds" in res["s_pmjay"]["reason"].lower()


def test_missing_income_cannot_confirm(db):
    res = _by_id(check_eligibility(db, None, "Delhi", False))
    assert res["s_pmjay"]["eligible"] is False
    assert "not provided" in res["s_pmjay"]["reason"].lower()


def test_state_inclusion_list(db):
    inside = _by_id(check_eligibility(db, 100000, "Karnataka", False))
    outside = _by_id(check_eligibility(db, 100000, "Delhi", False))
    assert inside["s_ka"]["eligible"] is True
    assert outside["s_ka"]["eligible"] is False


def test_govt_employment_requirement(db):
    no = _by_id(check_eligibility(db, 100000, "Delhi", False))
    yes = _by_id(check_eligibility(db, 100000, "Delhi", True))
    assert no["s_cghs"]["eligible"] is False
    assert yes["s_cghs"]["eligible"] is True
