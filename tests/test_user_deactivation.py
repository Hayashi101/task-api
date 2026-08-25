def test_deactivate_without_token(client, user_factory):
    user = user_factory()

    response = client.patch(
        f"/users/{user['id']}/deactivate",
    )

    assert response.status_code == 401


def test_normal_user_cannot_deactivate(client, user_factory):
    admin_target = user_factory()
    user = user_factory()

    response = client.patch(
        f"/users/{admin_target['id']}/deactivate",
        headers=user["headers"],
    )

    assert response.status_code == 403


def test_admin_can_deactivate_user(client, admin_factory, user_factory):
    admin = admin_factory()
    user = user_factory()

    response = client.patch(
        f"/users/{user['id']}/deactivate",
        headers=admin["headers"],
    )

    assert response.status_code == 204


def test_admin_deactivate_nonexistent_user(client, admin_factory):
    admin = admin_factory()

    response = client.patch(
        "/users/999999/deactivate",
        headers=admin["headers"],
    )

    assert response.status_code == 404


def test_deactivated_user_cannot_login_or_use_old_token(
    client,
    admin_factory,
    user_factory,
):
    admin = admin_factory()
    user = user_factory()

    # Admin deactivate user
    response = client.patch(
        f"/users/{user['id']}/deactivate",
        headers=admin["headers"],
    )

    assert response.status_code == 204

    # Old token must no longer work
    response = client.get(
        "/users/me",
        headers=user["headers"],
    )

    assert response.status_code == 401

    # User cannot login again
    response = client.post(
        "/auth/login",
        data={
            "username": user["email"],
            "password": user["password"],
        },
    )

    assert response.status_code == 401
