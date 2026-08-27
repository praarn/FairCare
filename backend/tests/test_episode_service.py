"""Multi-treatment episode estimator."""


def test_episode_sums_per_line_multiples(client):
    r = client.post(
        "/api/estimate-episode",
        json={
            "items": [
                {"treatment_id": "t_knee", "quantity": 2},
                {"treatment_id": "t_cataract", "quantity": 1},
            ],
            "city": "Delhi",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["lines"]) == 2
    assert body["skipped"] == []

    by_id = {ln["treatment"]["id"]: ln for ln in body["lines"]}
    knee = by_id["t_knee"]
    assert knee["quantity"] == 2
    assert knee["line_avg"] == round(knee["estimate"]["cost_avg"] * 2, 2)

    expected_total = round(sum(ln["line_avg"] for ln in body["lines"]), 2)
    assert body["totals"]["cost_avg"] == expected_total


def test_unknown_treatment_is_skipped_not_fatal(client):
    r = client.post(
        "/api/estimate-episode",
        json={
            "items": [
                {"treatment_id": "t_knee", "quantity": 1},
                {"treatment_id": "t_does_not_exist", "quantity": 1},
            ],
            "city": "Delhi",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert len(body["lines"]) == 1
    assert len(body["skipped"]) == 1
    assert body["skipped"][0]["treatment_id"] == "t_does_not_exist"
    assert body["totals"]["cost_avg"] == body["lines"][0]["line_avg"]


def test_episode_requires_location(client):
    r = client.post(
        "/api/estimate-episode",
        json={"items": [{"treatment_id": "t_knee", "quantity": 1}]},
    )
    assert r.status_code == 400


def test_episode_requires_at_least_one_item(client):
    r = client.post(
        "/api/estimate-episode", json={"items": [], "city": "Delhi"}
    )
    assert r.status_code == 422  # pydantic min_length=1


def test_episode_surfaces_eligible_schemes_when_income_given(client):
    r = client.post(
        "/api/estimate-episode",
        json={
            "items": [{"treatment_id": "t_knee", "quantity": 1}],
            "city": "Delhi",
            "annual_household_income": 100000,
        },
    )
    assert r.status_code == 200
    names = {s["scheme_id"] for s in r.json()["eligible_schemes"]}
    # PM-JAY (income threshold 250000 in the fixture) should qualify
    assert "s_pmjay" in names
