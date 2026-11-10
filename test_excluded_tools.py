import pytest


# The pizza never needs a tool that the customer excluded.
@pytest.mark.parametrize(
    "excluded",
    [
        [],
        ["Knife"],
        ["Scissors"],
        ["Knife", "Scissors"],
    ],
)
def test_excluded_tool_is_not_used(api, auth, excluded):
    body = {"excludedTools": excluded}
    res = api.post("/api/pizza", json=body, headers=auth)

    assert res.status_code == 200
    assert res.json()["pizza"]["tool"] not in excluded


# Excluding every available tool should be a client error with a JSON error message.
@pytest.mark.xfail(
    reason=(
        "Defect 1: excluding all three tools is expected to return HTTP 400 "
        "with a JSON error, but QuickPizza currently returns HTTP 500 with an empty body. "
        "Remove xfail when the API is fixed."
    ),
    strict=True,
)
def test_excluding_all_tools_returns_client_error(api, auth):
    body = {"excludedTools": ["Knife", "Pizza cutter", "Scissors"]}
    res = api.post("/api/pizza", json=body, headers=auth)

    assert res.status_code == 400
    assert res.headers.get("Content-Type", "").startswith("application/json")
    error_body = res.json()
    assert isinstance(error_body.get("error"), str)
    assert error_body["error"]
