import pytest


# Updating stars accepts the two boundary values and refuses values outside 1 to 5.
@pytest.mark.parametrize(
    ("new_stars", "expected_status"),
    [
        (0, 400),
        (1, 200),
        (5, 200),
        (6, 400),
    ],
)
def test_update_rating_boundary_values(api, auth, rating, new_stars, expected_status):
    path = f"/api/ratings/{rating['id']}"
    res = api.put(path, json={"stars": new_stars}, headers=auth)

    assert res.status_code == expected_status

    read_back = api.get(path, headers=auth)
    assert read_back.status_code == 200

    if expected_status == 200:
        assert read_back.json()["stars"] == new_stars
    else:
        # A refused update must leave the saved rating unchanged.
        assert read_back.json()["stars"] == rating["stars"]
