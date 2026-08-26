def test_register_user(client):
    response = client.post(
        "/users/register", json={"email": "test@example.com", "password": "password123"}
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "test@example.com"
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "password123",
    }

    # Lần 1
    response = client.post(
        "/users/register",
        json=payload,
    )

    assert response.status_code == 201

    # Lần 2
    response = client.post(
        "/users/register",
        json=payload,
    )

    assert response.status_code == 409
