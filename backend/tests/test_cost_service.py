"""Cost-estimation tier fallback + confidence, unchanged behaviour on the DB."""
from app.services.cost_service import estimate_cost


def test_tier1_exact_city_and_type(db):
    res = estimate_cost(db, "t_knee", city="Delhi", hospital_type="govt")
    assert res["is_fallback"] is False
    assert res["estimate"]["cost_avg"] == 100000
    assert [r["id"] for r in res["matched_records"]] == ["cr_k1"]


def test_tier2_exact_city_any_type_is_flagged_fallback(db):
    res = estimate_cost(db, "t_knee", city="Delhi", hospital_type="private_low")
    assert res["is_fallback"] is True
    assert "private_low" in res["fallback_reason"]
    # pooled across both Delhi rows
    assert {r["id"] for r in res["matched_records"]} == {"cr_k1", "cr_k2"}


def test_tier3_state_pool_when_city_missing(db):
    # Mumbai has no knee rows; with the state supplied we pool Maharashtra (Pune row).
    res = estimate_cost(db, "t_knee", city="Mumbai", state="Maharashtra")
    assert res["is_fallback"] is True
    assert "Maharashtra" in res["fallback_reason"]
    assert [r["id"] for r in res["matched_records"]] == ["cr_k3"]


def test_tier4_national_reference(db):
    # cataract only has a Chennai row; ask for Delhi -> national PM-JAY reference.
    res = estimate_cost(db, "t_cataract", city="Delhi")
    assert res["is_fallback"] is True
    assert res["estimate"]["cost_avg"] == 6500
    assert res["matched_records"][0]["source"].startswith("Approx. PM-JAY")


def test_tier5_national_pool(db):
    # knee, unknown state -> pooled national sample average across all knee rows.
    res = estimate_cost(db, "t_knee", state="Kerala")
    assert res["is_fallback"] is True
    assert len(res["matched_records"]) == 3


def test_no_data_returns_none(db):
    res = estimate_cost(db, "t_rare", city="Delhi")
    assert res["estimate"] is None
    assert res["is_fallback"] is True


def test_confidence_label_bands(db):
    res = estimate_cost(db, "t_knee", city="Delhi", hospital_type="govt")
    assert 0.0 <= res["estimate"]["confidence_score"] <= 1.0
    assert res["estimate"]["confidence_label"] in {"low", "medium", "high"}


def test_hindi_reason_language(db):
    res = estimate_cost(db, "t_cataract", city="Delhi", lang="hi")
    assert res["fallback_reason"]
    # crude check: contains Devanagari
    assert any("ऀ" <= ch <= "ॿ" for ch in res["fallback_reason"])
