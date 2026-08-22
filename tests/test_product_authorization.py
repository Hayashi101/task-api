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

    assert response.status_code == 200

    return response.json()["access_token"]


def get_auth_headers(token):
    return {
        "Authorization": f"Bearer {token}",
    }


def create_product(client, headers: dict, product_name: str):
    response = client.post(
        "/products/",
        headers=headers,
        json={
            "name": product_name,
            "price": 10.5,
            "quantity": 3,
            "description": "Authorization test",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_owner_can_get_own_product(client):
    # User A
    email_a, password_a = register_user(client)
    token_a = login(client, email_a, password_a)
    headers_a = get_auth_headers(token_a)

    # Create product by user A
    product_name = f"Product-{uuid4().hex}"
    product = create_product(client, headers_a, product_name)

    product_id = product["id"]

    # User A tries to get the product they created
    response = client.get(
        f"/products/{product_id}",
        headers=headers_a,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product_id
    assert data["name"] == product_name


def test_other_user_cannot_get_product(client):
    # User A
    email_a, password_a = register_user(client)
    token_a = login(client, email_a, password_a)
    headers_a = get_auth_headers(token_a)

    # User B
    email_b, password_b = register_user(client)
    token_b = login(client, email_b, password_b)
    headers_b = get_auth_headers(token_b)

    # Create product by user A
    product_name = f"Product-{uuid4().hex}"
    product = create_product(client, headers_a, product_name)

    product_id = product["id"]

    # User B tries to get the product created by user A
    response = client.get(
        f"/products/{product_id}",
        headers=headers_b,
    )

    assert response.status_code == 404


def test_other_user_cannot_update_product(client):
    # User A
    email_a, password_a = register_user(client)
    token_a = login(client, email_a, password_a)
    headers_a = get_auth_headers(token_a)

    # User B
    email_b, password_b = register_user(client)
    token_b = login(client, email_b, password_b)
    headers_b = get_auth_headers(token_b)

    # Create product by user A
    product_name = f"Product-{uuid4().hex}"
    product = create_product(client, headers_a, product_name)

    product_id = product["id"]

    # User B tries to update the product created by user A
    response = client.patch(
        f"/products/{product_id}",
        headers=headers_b,
        json={
            "name": f"Hacked-{uuid4().hex}",
            "price": 999.99,
            "quantity": 999,
            "description": "Hacked",
        },
    )

    assert response.status_code == 404

    # User A get product details
    response = client.get(
        f"/products/{product_id}",
        headers=headers_a,
    )

    assert response.status_code == 200

    data = response.json()

    # Confirm data is not changed by user B
    assert data["name"] == product_name
    assert data["price"] == 10.5
    assert data["quantity"] == 3
    assert data["description"] == "Authorization test"


def test_other_user_cannot_delete_product(client):
    # User A
    email_a, password_a = register_user(client)
    token_a = login(client, email_a, password_a)
    headers_a = get_auth_headers(token_a)

    # User B
    email_b, password_b = register_user(client)
    token_b = login(client, email_b, password_b)
    headers_b = get_auth_headers(token_b)

    # User A creates a product
    product_name = f"Product-{uuid4().hex}"

    product = create_product(
        client,
        headers_a,
        product_name,
    )

    product_id = product["id"]

    # User B tries to delete the product created by user A
    response = client.delete(
        f"/products/{product_id}",
        headers=headers_b,
    )

    assert response.status_code == 404

    # User A still gets the product
    response = client.get(
        f"/products/{product_id}",
        headers=headers_a,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product_id
    assert data["name"] == product_name


def test_owner_can_delete_own_product(client):
    # User A
    email_a, password_a = register_user(client)
    token_a = login(client, email_a, password_a)
    headers_a = get_auth_headers(token_a)

    # User B
    email_b, password_b = register_user(client)
    token_b = login(client, email_b, password_b)
    headers_b = get_auth_headers(token_b)

    # User A creates a product
    product_name = f"Product-{uuid4().hex}"

    product = create_product(
        client,
        headers_a,
        product_name,
    )

    product_id = product["id"]

    # User A deletes the product
    response = client.delete(
        f"/products/{product_id}",
        headers=headers_a,
    )

    assert response.status_code == 204

    # Product is not exists anymore
    response = client.get(f"/products/{product_id}", headers=headers_a)

    assert response.status_code == 404
