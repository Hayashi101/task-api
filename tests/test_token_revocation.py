def test_old_token_remains_invalid_after_reactivation(
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

    # Admin activate user
    response = client.patch(
        f"/users/{user['id']}/activate",
        headers=admin["headers"],
    )

    assert response.status_code == 204

    # Old token must remain invalid
    response = client.get(
        "/users/me",
        headers=user["headers"],
    )

    assert response.status_code == 401

    # Login again
    response = client.post(
        "/auth/login",
        data={
            "username": user["email"],
            "password": user["password"],
        },
    )

    assert response.status_code == 200

    new_token = response.json()["access_token"]

    # New token must work
    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {new_token}",
        },
    )

    assert response.status_code == 200


def test_password_change_invalidates_old_token(
    client,
    user_factory,
):
    user = user_factory()

    response = client.patch(
        "/users/me/password",
        headers=user["headers"],
        json={
            "current_password": user["password"],
            "new_password": "NewPassword123!",
        },
    )

    assert response.status_code == 204

    # Old token must be invalid
    response = client.get(
        "/users/me",
        headers=user["headers"],
    )

    assert response.status_code == 401

    # Login with new password
    response = client.post(
        "/auth/login",
        data={
            "username": user["email"],
            "password": "NewPassword123!",
        },
    )

    assert response.status_code == 200

    new_token = response.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {new_token}"},
    )

    assert response.status_code == 200
