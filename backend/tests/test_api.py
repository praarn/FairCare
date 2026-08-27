"""End-to-end HTTP checks for the core (non-auth) endpoints + health."""


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["db"] == "ok"


def test_health_live_and_ready(client):
    assert client.get("/api/health/live").status_code == 200
    assert client.get("/api/health/ready").status_code == 200


def test_request_id_header_present(client):
    r = client.get("/api/health")
    assert r.headers.get("X-Request-ID")


def test_predict_cost_contract_shape(client):
    r = client.post(
        "/api/predict-cost", json={"treatment_id": "t_knee", "city": "Delhi"}
    )
    assert r.status_code == 200
    body = r.json()
    for key in ("treatment", "estimate", "factors", "sources", "disclaimer"):
        assert key in body
    assert body["estimate"]["confidence_label"] in {"low", "medium", "high"}


def test_predict_cost_requires_location(client):
    r = client.post("/api/predict-cost", json={"treatment_id": "t_knee"})
    assert r.status_code == 400


def test_predict_cost_unknown_treatment(client):
    r = client.post(
        "/api/predict-cost", json={"treatment_id": "t_nope", "city": "Delhi"}
    )
    assert r.status_code == 404


def test_hospitals_budget_mode_orders_by_cost(client):
    r = client.get(
        "/api/hospitals",
        params={"treatment_id": "t_knee", "city": "Delhi", "budget_mode": "true"},
    )
    assert r.status_code == 200
    rows = r.json()
    costs = [h["cost_avg"] for h in rows if h["cost_avg"] is not None]
    assert costs == sorted(costs)


def test_treatments_search_endpoint(client):
    r = client.get("/api/treatments/search", params={"q": "knee"})
    assert r.status_code == 200
    assert r.json()[0]["id"] == "t_knee"


def test_symptom_search_empty_on_weak_match(client):
    r = client.get(
        "/api/treatments/search-symptoms", params={"q": "slight headache today"}
    )
    assert r.status_code == 200
    assert r.json() == []


def test_auth_endpoint_is_rate_limited(client, monkeypatch):
    # RATE_LIMIT_AUTH defaults to 20/minute; the 21st call in the window is 429.
    from app.rate_limit import limiter

    limiter.reset()
    statuses = [
        client.post("/api/auth/forgot-password", json={"email": "x@example.com"}).status_code
        for _ in range(25)
    ]
    assert 429 in statuses
    assert statuses[0] == 200
    limiter.reset()
