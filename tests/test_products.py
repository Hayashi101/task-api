def get_auth_headers(
    client,
    email: str,
    password: str,
):
    response = client.post(
        "/users/register", json={"email": email, "password": password}
    )

    assert response.status_code == 201

    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    access_token = response.json()["access_token"]

    return {"Authorization": f"Bearer {access_token}"}


def test_product_ownership_is_protected(client):
    user_a_header = get_auth_headers(
        client, email="usera@example.coom", password="password123"
    )
    user_b_header = get_auth_headers(
        client, email="userb@example.coom", password="password456"
    )

    response = client.post(
        "/products/",
        json={
            "name": "iPhone",
            "price": 1000,
            "quantity": 1,
        },
        headers=user_a_header,
    )

    assert response.status_code == 201

    product_id = response.json()["id"]

    response = client.get(f"/products/{product_id}", headers=user_b_header)

    assert response.status_code == 404

    response = client.get("/products", headers=user_b_header)

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["total"] == 0
