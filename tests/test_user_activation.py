def test_activate_without_token(client, user_factory):
    user = user_factory()

    response = client.patch(
        f"/users/{user['id']}/activate",
    )

    assert response.status_code == 401


def test_normal_user_cannot_activate(client, user_factory):
    admin_target = user_factory()
    user = user_factory()

    response = client.patch(
        f"/users/{admin_target['id']}/activate",
        headers=user["headers"],
    )

    assert response.status_code == 403


def test_admin_can_activate_user(client, admin_factory, user_factory):
    admin = admin_factory()
    user = user_factory()

    response = client.patch(
        f"/users/{user['id']}/activate",
        headers=admin["headers"],
    )

    assert response.status_code == 204


def test_admin_activate_nonexistent_user(client, admin_factory):
    admin = admin_factory()

    response = client.patch(
        "/users/999999/activate",
        headers=admin["headers"],
    )

    assert response.status_code == 404


def test_admin_can_reactivate_user(client, admin_factory, user_factory):
    admin = admin_factory()
    user = user_factory()

    response = client.patch(
        f"/users/{user['id']}/deactivate",
        headers=admin["headers"],
    )
    assert response.status_code == 204

    response = client.post(
        "/auth/login",
        data={
            "username": user["email"],
            "password": user["password"],
        },
    )
    assert response.status_code == 401

    response = client.patch(
        f"/users/{user['id']}/activate",
        headers=admin["headers"],
    )
    assert response.status_code == 204

    login_response = client.post(
        "/auth/login",
        data={
            "username": user["email"],
            "password": user["password"],
        },
    )
    assert login_response.status_code == 200

    new_token = login_response.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {new_token}"},
    )
    assert response.status_code == 200
