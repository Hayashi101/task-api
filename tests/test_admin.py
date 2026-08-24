def test_get_all_users_without_token(client):
    response = client.get("/users/")

    assert response.status_code == 401


def test_regular_user_cannot_get_all_users(client, user_factory):
    user = user_factory()

    response = client.get("/users/", headers=user["headers"])

    assert response.status_code == 403


def test_get_users_as_admin(client, admin_factory):
    admin = admin_factory()

    response = client.get("/users/", headers=admin["headers"])

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    assert any(user["email"] == admin["email"] for user in data)
