import pytest


STARS_ERROR = "number of stars must be between 1 and 5 (inclusive)"
AUTH_ERROR = "authentication failed"


# Base choice: 3 stars as a whole number, a real pizza, and the user's own token.
def test_base_choice_is_saved(api, auth, pizza_id):
    new = {"pizza_id": pizza_id, "stars": 3}
    res = api.post("/api/ratings", json=new, headers=auth)

    assert res.status_code == 201
    created = res.json()
    try:
        assert created["stars"] == 3
        assert created["pizza_id"] == pizza_id
    finally:
        cleanup = api.delete(f"/api/ratings/{created['id']}", headers=auth)
        assert cleanup.status_code == 204, cleanup.text


# C1: a number of stars below 1 or above 5 is refused with the documented range error.
@pytest.mark.parametrize("stars", [0, 6])
def test_stars_out_of_range(api, auth, pizza_id, stars):
    new = {"pizza_id": pizza_id, "stars": stars}
    res = api.post("/api/ratings", json=new, headers=auth)

    assert res.status_code == 400
    assert res.json() == {"error": STARS_ERROR}


# C2: decimal, text and missing stars are rejected with their observed API error messages.
@pytest.mark.parametrize(
    ("stars", "omit_stars", "expected_error"),
    [
        (
            3.5,
            False,
            "json: cannot unmarshal number 3.5 into Go struct field Rating.stars of type int",
        ),
        (
            "3",
            False,
            "json: cannot unmarshal string into Go struct field Rating.stars of type int",
        ),
        (None, True, STARS_ERROR),
    ],
    ids=["decimal", "text", "missing"],
)
def test_stars_must_be_a_whole_number(
    api, auth, pizza_id, stars, omit_stars, expected_error
):
    new = {"pizza_id": pizza_id, "stars": stars}
    if omit_stars:
        new.pop("stars")

    res = api.post("/api/ratings", json=new, headers=auth)

    assert res.status_code == 400
    assert res.json() == {"error": expected_error}


# C3: a rating cannot refer to a pizza that does not exist.
def test_rating_with_unknown_pizza_is_refused(api, auth):
    new = {"pizza_id": 999999999, "stars": 3}
    res = api.post("/api/ratings", json=new, headers=auth)

    assert res.status_code == 400
    assert res.json() == {"error": "pizza ID 999999999 not found"}


# C4: a request without an Authorization header is refused.
def test_rating_without_token_is_refused(api, pizza_id):
    new = {"pizza_id": pizza_id, "stars": 3}
    res = api.post("/api/ratings", json=new)

    assert res.status_code == 401
    assert res.json() == {"error": AUTH_ERROR}


# C4: a token with an invalid, short value is refused.
def test_rating_with_short_token_is_refused(api, pizza_id):
    new = {"pizza_id": pizza_id, "stars": 3}
    short_auth = {"Authorization": "token short"}
    res = api.post("/api/ratings", json=new, headers=short_auth)

    assert res.status_code == 401
    assert res.json() == {"error": AUTH_ERROR}
