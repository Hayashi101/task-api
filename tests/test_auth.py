from uuid import uuid4


def register_user(client):
    email = f"test_{uuid4().hex[:8]}@example.com"
    password = "strongpassword123"

    response = client.post(
        "/users/register", json={"email": email, "password": password}
    )

    assert response.status_code == 201

    return email, password


def login(client, email: str, password: str):
    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    return response


def get_auth_headers(token):
    return {
        "Authorization": f"Bearer {token}",
    }


def test_login_success(client):
    email, password = register_user(client)

    response = login(client, email, password)

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    email, password = register_user(client)

    response = login(client, email, "wrongpassword123")

    assert response.status_code == 401


def test_change_password_without_token(client):
    email, password = register_user(client)

    response = client.patch(
        "/users/me/password",
        json={
            "current_password": password,
            "new_password": "NewPassword123",
        },
    )

    assert response.status_code == 401


def test_change_password_wrong_current_password(client):
    email, password = register_user(client)

    login_response = login(client, email, password)

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.patch(
        "/users/me/password",
        headers=get_auth_headers(token),
        json={
            "current_password": "wrongpassword123",
            "new_password": "NewPassword123",
        },
    )

    assert response.status_code == 400


def test_change_password_success(client):
    email, password = register_user(client)

    login_response = login(client, email, password)

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    new_password = "NewPassword123"

    response = client.patch(
        "/users/me/password",
        headers=get_auth_headers(token),
        json={
            "current_password": password,
            "new_password": new_password,
        },
    )

    assert response.status_code == 204

    old_login = login(client, email, password)

    assert old_login.status_code == 401

    new_login = login(client, email, new_password)

    assert new_login.status_code == 200

    data = new_login.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
