# A vegetarian request gets a named pizza with vegetarian ingredients only.
def test_vegetarian_pizza(api):
    public_auth = {"Authorization": "token abcdef0123456789"}
    vegetarian = {"mustBeVegetarian": True}

    res = api.post("/api/pizza", json=vegetarian, headers=public_auth)

    assert res.status_code == 200
    body = res.json()
    assert body["pizza"]["name"] != ""
    for ingredient in body["pizza"]["ingredients"]:
        assert ingredient["vegetarian"] is True, ingredient["name"]


# A request without a token is refused with 401 and an error message.
def test_pizza_without_token_is_refused(api):
    vegetarian = {"mustBeVegetarian": True}

    res = api.post("/api/pizza", json=vegetarian)

    assert res.status_code == 401
    assert res.json() == {"error": "authentication failed"}
