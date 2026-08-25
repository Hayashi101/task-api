def test_login_returns_access_and_refresh_tokens(client, user_factory):
    user = user_factory()

    response = client.post(
        "/auth/login",
        data={
            "username": user["email"],
            "password": user["password"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["access_token"]
    assert data["refresh_token"]
    assert data["token_type"] == "bearer"


def test_valid_refresh_token_creates_new_access_token(
    client,
    user_factory,
):
    user = user_factory()

    login_response = client.post(
        "/auth/login",
        data={
            "username": user["email"],
            "password": user["password"],
        },
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_access_token_cannot_be_used_to_refresh(
    client,
    user_factory,
):
    user = user_factory()

    login_response = client.post(
        "/auth/login",
        data={
            "username": user["email"],
            "password": user["password"],
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": access_token,
        },
    )

    assert response.status_code == 401


def test_old_refresh_token_invalid_after_password_change(
    client,
    user_factory,
):
    user = user_factory()

    login_response = client.post(
        "/auth/login",
        data={
            "username": user["email"],
            "password": user["password"],
        },
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    response = client.patch(
        "/users/me/password",
        headers=user["headers"],
        json={
            "current_password": user["password"],
            "new_password": "NewPassword123!",
        },
    )

    assert response.status_code == 204

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == 401


def test_old_refresh_token_invalid_after_deactivate_and_activate(
    client,
    admin_factory,
    user_factory,
):
    admin = admin_factory()
    user = user_factory()

    login_response = client.post(
        "/auth/login",
        data={
            "username": user["email"],
            "password": user["password"],
        },
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    # Deactivate
    response = client.patch(
        f"/users/{user['id']}/deactivate",
        headers=admin["headers"],
    )

    assert response.status_code == 204

    # Activate
    response = client.patch(
        f"/users/{user['id']}/activate",
        headers=admin["headers"],
    )

    assert response.status_code == 204

    # Old refresh token must remain invalid
    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == 401
