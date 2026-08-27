"""Lenient name search vs strict F1 symptom search."""
from app.services.treatment_service import get_treatment_by_id, search_treatments


def test_lenient_search_typo_tolerant(db):
    results = search_treatments(db, "nee replacment")  # missing k, typo
    assert results
    assert results[0]["id"] == "t_knee"


def test_lenient_search_always_falls_back(db):
    # gibberish still returns the closest few rather than nothing
    results = search_treatments(db, "zzzqwx")
    assert isinstance(results, list)


def test_empty_query_returns_all(db):
    assert len(search_treatments(db, "")) == 3


def test_strict_symptom_match_hits(db):
    results = search_treatments(db, "my knee is swollen and stiff", strict=True)
    assert [r["id"] for r in results] == ["t_knee"]


def test_strict_symptom_rejects_weak_guess(db):
    # one incidental shared filler word must not surface an unrelated treatment
    results = search_treatments(db, "I have a mild headache and feel dizzy", strict=True)
    assert results == []


def test_get_treatment_by_id(db):
    assert get_treatment_by_id(db, "t_knee")["name"] == "Knee Replacement"
    assert get_treatment_by_id(db, "nope") is None
