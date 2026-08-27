"""Signup / login / me / logout / password-reset over the DB-backed service."""


def test_signup_login_me_logout_flow(client):
    r = client.post(
        "/api/auth/signup",
        json={"name": "Asha", "email": "asha@example.com", "password": "hunter2hunter"},
    )
    assert r.status_code == 200
    token = r.json()["token"]
    assert r.json()["user"]["email"] == "asha@example.com"

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["name"] == "Asha"

    out = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert out.status_code == 200

    me2 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me2.status_code == 401


def test_signup_rejects_short_password(client):
    r = client.post(
        "/api/auth/signup",
        json={"name": "X", "email": "x@example.com", "password": "short"},
    )
    assert r.status_code == 400


def test_duplicate_email_conflicts(client):
    body = {"name": "A", "email": "dup@example.com", "password": "longenough1"}
    assert client.post("/api/auth/signup", json=body).status_code == 200
    assert client.post("/api/auth/signup", json=body).status_code == 409


def test_login_wrong_password(client):
    client.post(
        "/api/auth/signup",
        json={"name": "B", "email": "b@example.com", "password": "correcthorse"},
    )
    r = client.post(
        "/api/auth/login", json={"email": "b@example.com", "password": "wrongwrong"}
    )
    assert r.status_code == 401


def test_forgot_and_reset_password_dev_mode(client):
    client.post(
        "/api/auth/signup",
        json={"name": "C", "email": "c@example.com", "password": "originalpass1"},
    )
    fp = client.post("/api/auth/forgot-password", json={"email": "c@example.com"})
    assert fp.status_code == 200
    reset_token = fp.json()["reset_token"]
    assert reset_token  # dev mode returns it in the body

    rp = client.post(
        "/api/auth/reset-password",
        json={"token": reset_token, "new_password": "brandnewpass1"},
    )
    assert rp.status_code == 200

    ok = client.post(
        "/api/auth/login", json={"email": "c@example.com", "password": "brandnewpass1"}
    )
    assert ok.status_code == 200


def test_forgot_password_unknown_email_same_shape(client):
    fp = client.post("/api/auth/forgot-password", json={"email": "ghost@example.com"})
    assert fp.status_code == 200
    assert fp.json()["reset_token"] is None
