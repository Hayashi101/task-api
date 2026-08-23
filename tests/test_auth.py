def login(client, email: str, password: str):
    return client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )


def test_login_success(client, user_factory):
    user = user_factory()

    response = login(client, user["email"], user["password"])

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, user_factory):
    user = user_factory()

    response = login(client, user["email"], "wrongpassword123")

    assert response.status_code == 401


def test_change_password_without_token(client, user_factory):
    user = user_factory()

    response = client.patch(
        "/users/me/password",
        json={
            "current_password": user["password"],
            "new_password": "NewPassword123",
        },
    )

    assert response.status_code == 401


def test_change_password_wrong_current_password(client, user_factory):
    user = user_factory()

    response = client.patch(
        "/users/me/password",
        headers=user["headers"],
        json={
            "current_password": "wrongpassword123",
            "new_password": "NewPassword123",
        },
    )

    assert response.status_code == 400


def test_change_password_success(client, user_factory):
    user = user_factory()
    new_password = "NewPassword123"

    response = client.patch(
        "/users/me/password",
        headers=user["headers"],
        json={
            "current_password": user["password"],
            "new_password": new_password,
        },
    )

    assert response.status_code == 204
    assert login(client, user["email"], user["password"]).status_code == 401

    new_login = login(client, user["email"], new_password)

    assert new_login.status_code == 200
    data = new_login.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"
