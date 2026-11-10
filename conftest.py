import uuid

import pytest
import requests


SITE = "https://quickpizza.grafana.com"


class QuickPizza(requests.Session):
    """A session that puts the QuickPizza site address in front of each API path."""

    def request(self, method, url, *args, **kwargs):
        return super().request(method, SITE + url, *args, **kwargs)


@pytest.fixture(scope="session")
def api():
    """Share one HTTP session so the AWSALB cookie keeps requests on one server."""
    with QuickPizza() as session:
        yield session


def log_in_new_user(api):
    """Create a unique test user, log in, and return that user's Authorization header."""
    name = "lab-" + uuid.uuid4().hex[:12]
    user = {"username": name, "password": "Pizza-2026"}

    res = api.post("/api/users", json=user)
    assert res.status_code == 201, f"Could not create test user: {res.status_code} {res.text}"

    res = api.post("/api/users/token/login", json=user)
    assert res.status_code == 200, f"Could not log in test user: {res.status_code} {res.text}"

    return {"Authorization": "token " + res.json()["token"]}


@pytest.fixture
def auth(api):
    """Give each test a fresh user and that user's own token."""
    return log_in_new_user(api)


@pytest.fixture
def pizza_id(api, auth):
    """Create a pizza owned by the test user and return its id."""
    res = api.post("/api/pizza", json={}, headers=auth)
    assert res.status_code == 200, f"Could not create test pizza: {res.status_code} {res.text}"
    return res.json()["pizza"]["id"]


@pytest.fixture
def rating(api, auth, pizza_id):
    """Create a 3-star rating before the test and delete it after the test."""
    new = {"pizza_id": pizza_id, "stars": 3}
    res = api.post("/api/ratings", json=new, headers=auth)
    assert res.status_code == 201, f"Could not create test rating: {res.status_code} {res.text}"
    made = res.json()

    yield made

    cleanup = api.delete(f"/api/ratings/{made['id']}", headers=auth)
    if cleanup.status_code == 204:
        return

    # test_delete_rating removes the rating itself, so fixture cleanup can receive
    # the API's 400 "not found" response when it tries to remove it a second time.
    assert cleanup.status_code in (400, 404), (
        f"Could not clean up test rating {made['id']}: "
        f"{cleanup.status_code} {cleanup.text}"
    )
    assert "not found" in cleanup.json().get("error", "").lower(), (
        f"Unexpected cleanup response for rating {made['id']}: {cleanup.text}"
    )


@pytest.fixture
def other_auth(api):
    """Give the test a second, different user's token."""
    return log_in_new_user(api)
