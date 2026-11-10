# A different user cannot read the owner's rating, and the owner still can.
def test_other_user_cannot_read_rating(api, auth, other_auth, rating):
    path = f"/api/ratings/{rating['id']}"

    attempt = api.get(path, headers=other_auth)
    assert 400 <= attempt.status_code <= 499

    owner_read = api.get(path, headers=auth)
    assert owner_read.status_code == 200
    assert owner_read.json() == rating


# A different user cannot change the owner's rating.
def test_other_user_cannot_update_rating(api, auth, other_auth, rating):
    path = f"/api/ratings/{rating['id']}"

    attempt = api.put(path, json={"stars": 5}, headers=other_auth)
    assert 400 <= attempt.status_code <= 499

    owner_read = api.get(path, headers=auth)
    assert owner_read.status_code == 200
    assert owner_read.json()["stars"] == rating["stars"]


# A different user cannot delete the owner's rating.
def test_other_user_cannot_delete_rating(api, auth, other_auth, rating):
    path = f"/api/ratings/{rating['id']}"

    attempt = api.delete(path, headers=other_auth)
    assert 400 <= attempt.status_code <= 499

    owner_read = api.get(path, headers=auth)
    assert owner_read.status_code == 200
    assert owner_read.json() == rating
