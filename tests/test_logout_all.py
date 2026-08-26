def test_logout_all_invalidates_all_tokens(client, user_factory):
    user = user_factory()

    # Login
    login_response = client.post(
        "/auth/login",
        data={
            "username": user["email"],
            "password": user["password"],
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()
    access_token = data["access_token"]
    refresh_token = data["refresh_token"]

    # Logout all devices
    response = client.post(
        "/auth/logout-all",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 204

    # Old access token must be invalid
    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 401

    # Old refresh token must be invalid
    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == 401

    # Login again
    login_response = client.post(
        "/auth/login",
        data={
            "username": user["email"],
            "password": user["password"],
        },
    )

    assert login_response.status_code == 200

    new_data = login_response.json()
    new_access_token = new_data["access_token"]

    # New access token must work
    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {new_access_token}",
        },
    )

    assert response.status_code == 200


def test_logout_all_without_token_returns_401(client):
    response = client.post("/auth/logout-all")

    assert response.status_code == 401
