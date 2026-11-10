import uuid


# A second user cannot register a username that is already taken.
def test_duplicate_username_is_refused(api):
    name = "lab-" + uuid.uuid4().hex[:12]
    user = {"username": name, "password": "Pizza-2026"}

    first = api.post("/api/users", json=user)
    assert first.status_code == 201

    second = api.post("/api/users", json=user)
    assert second.status_code == 400
    assert second.json() == {"error": "username already taken"}


# Logging in with a wrong password is refused with an authentication error.
def test_wrong_password_is_refused(api):
    name = "lab-" + uuid.uuid4().hex[:12]
    user = {"username": name, "password": "Pizza-2026"}

    created = api.post("/api/users", json=user)
    assert created.status_code == 201

    wrong_user = {"username": name, "password": "Definitely-Wrong"}
    res = api.post("/api/users/token/login", json=wrong_user)

    assert res.status_code == 401
    assert res.json() == {"error": "authentication failed"}


# A user with an empty name is refused with a validation error.
def test_empty_username_is_refused(api):
    user = {"username": "", "password": "Pizza-2026"}
    res = api.post("/api/users", json=user)

    assert res.status_code == 400
    assert res.json() == {"error": "username field is empty"}
