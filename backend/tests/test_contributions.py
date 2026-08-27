"""Crowd-sourced contributions: anonymous submit, admin gate, promotion."""
from tests.conftest import make_admin


def _signup(client, email, password="longenough1", name="U"):
    r = client.post(
        "/api/auth/signup", json={"name": name, "email": email, "password": password}
    )
    assert r.status_code == 200
    return r.json()["token"]


def _admin(client, email):
    """Sign up, flip to admin on the shared session, return a bearer token."""
    token = _signup(client, email)
    make_admin(client.db_session, email)
    return {"Authorization": f"Bearer {token}"}


def test_anonymous_submit_is_accepted(client):
    r = client.post(
        "/api/contributions",
        json={"treatment_id": "t_knee", "city": "Delhi", "amount": 95000},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "received"
    assert r.json()["id"]


def test_submit_rejects_non_positive_amount(client):
    r = client.post("/api/contributions", json={"amount": 0})
    assert r.status_code == 422  # pydantic gt=0


def test_authed_submit_attaches_user(client):
    token = _signup(client, "sub@example.com")
    r = client.post(
        "/api/contributions",
        json={"treatment_id": "t_knee", "city": "Delhi", "amount": 90000},
        headers={"Authorization": f"Bearer {token}"},
    )
    cid = r.json()["id"]

    headers = _admin(client, "adm1@example.com")
    listing = client.get("/api/contributions", headers=headers)
    assert listing.status_code == 200
    match = [c for c in listing.json() if c["id"] == cid][0]
    assert match["user_id"] is not None


def test_list_requires_admin(client):
    assert client.get("/api/contributions").status_code == 401
    token = _signup(client, "plain@example.com")
    r = client.get(
        "/api/contributions", headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 403


def test_approve_creates_cost_record_visible_to_predict(client):
    cid = client.post("/api/contributions", json={"amount": 123456}).json()["id"]
    headers = _admin(client, "admin@example.com")

    approve = client.post(
        f"/api/contributions/{cid}/approve",
        json={
            "treatment_id": "t_knee",
            "city": "Indore",
            "state": "Madhya Pradesh",
            "hospital_type": "private_mid",
        },
        headers=headers,
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["cost_record_id"] == f"user_{cid}"

    pred = client.post(
        "/api/predict-cost", json={"treatment_id": "t_knee", "city": "Indore"}
    )
    assert pred.status_code == 200
    ids = [s["id"] for s in pred.json()["sources"]]
    assert f"user_{cid}" in ids


def test_approve_without_treatment_is_rejected(client):
    cid = client.post("/api/contributions", json={"amount": 5000}).json()["id"]
    headers = _admin(client, "admin2@example.com")
    approve = client.post(
        f"/api/contributions/{cid}/approve",
        json={"city": "Pune", "state": "Maharashtra", "hospital_type": "govt"},
        headers=headers,
    )
    assert approve.status_code == 400


def test_reject_marks_status_without_creating_row(client):
    cid = client.post("/api/contributions", json={"amount": 5000}).json()["id"]
    headers = _admin(client, "admin3@example.com")

    rej = client.post(f"/api/contributions/{cid}/reject", headers=headers)
    assert rej.status_code == 200
    assert rej.json()["status"] == "rejected"

    again = client.post(f"/api/contributions/{cid}/reject", headers=headers)
    assert again.status_code == 400
