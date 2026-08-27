"""Server-side saved estimates: auth, roundtrip, drift, owner-scoped delete."""


def _signup(client, email):
    r = client.post(
        "/api/auth/signup",
        json={"name": "U", "email": email, "password": "longenough1"},
    )
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['token']}"}


def test_save_requires_auth(client):
    r = client.post(
        "/api/saved-estimates", json={"treatment_id": "t_knee", "city": "Delhi"}
    )
    assert r.status_code == 401


def test_save_requires_location(client):
    headers = _signup(client, "loc@example.com")
    r = client.post(
        "/api/saved-estimates", json={"treatment_id": "t_knee"}, headers=headers
    )
    assert r.status_code == 400


def test_save_and_list_roundtrip_with_drift(client):
    headers = _signup(client, "round@example.com")
    saved = client.post(
        "/api/saved-estimates",
        json={"treatment_id": "t_knee", "city": "Delhi", "label": "Mrs. Rao"},
        headers=headers,
    )
    assert saved.status_code == 200, saved.text
    body = saved.json()
    assert body["treatment_name"] == "Knee Replacement"
    assert body["label"] == "Mrs. Rao"
    assert body["cost_avg"] > 0

    listing = client.get("/api/saved-estimates", headers=headers)
    assert listing.status_code == 200
    rows = listing.json()
    assert len(rows) == 1
    assert rows[0]["id"] == body["id"]
    # nothing changed since saving -> drift computed, direction flat
    assert rows[0]["drift"] is not None
    assert rows[0]["drift"]["direction"] == "flat"


def test_save_unknown_treatment_404(client):
    headers = _signup(client, "unk@example.com")
    r = client.post(
        "/api/saved-estimates",
        json={"treatment_id": "t_missing", "city": "Delhi"},
        headers=headers,
    )
    assert r.status_code == 404


def test_delete_is_owner_scoped(client):
    owner = _signup(client, "owner@example.com")
    other = _signup(client, "other@example.com")

    est_id = client.post(
        "/api/saved-estimates",
        json={"treatment_id": "t_knee", "city": "Delhi"},
        headers=owner,
    ).json()["id"]

    # a different user cannot delete it
    assert client.delete(f"/api/saved-estimates/{est_id}", headers=other).status_code == 404
    assert len(client.get("/api/saved-estimates", headers=owner).json()) == 1

    # the owner can
    assert client.delete(f"/api/saved-estimates/{est_id}", headers=owner).status_code == 204
    assert client.get("/api/saved-estimates", headers=owner).json() == []
