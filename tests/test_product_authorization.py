from uuid import uuid4


def test_owner_can_get_own_product(client, user_factory, product_factory):
    owner = user_factory()
    product = product_factory(owner["headers"])

    response = client.get(
        f"/products/{product['id']}", headers=owner["headers"]
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product["id"]
    assert data["name"] == product["name"]


def test_other_user_cannot_get_product(client, user_factory, product_factory):
    owner = user_factory()
    other_user = user_factory()
    product = product_factory(owner["headers"])

    response = client.get(
        f"/products/{product['id']}", headers=other_user["headers"]
    )

    assert response.status_code == 404


def test_other_user_cannot_update_product(
    client, user_factory, product_factory
):
    owner = user_factory()
    other_user = user_factory()
    product = product_factory(owner["headers"])

    response = client.patch(
        f"/products/{product['id']}",
        headers=other_user["headers"],
        json={
            "name": f"Hacked-{uuid4().hex}",
            "price": 999.99,
            "quantity": 999,
            "description": "Hacked",
        },
    )

    assert response.status_code == 404

    response = client.get(
        f"/products/{product['id']}", headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json() == product


def test_other_user_cannot_delete_product(
    client, user_factory, product_factory
):
    owner = user_factory()
    other_user = user_factory()
    product = product_factory(owner["headers"])

    response = client.delete(
        f"/products/{product['id']}", headers=other_user["headers"]
    )

    assert response.status_code == 404

    response = client.get(
        f"/products/{product['id']}", headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json() == product


def test_owner_can_delete_own_product(client, user_factory, product_factory):
    owner = user_factory()
    product = product_factory(owner["headers"])

    response = client.delete(
        f"/products/{product['id']}", headers=owner["headers"]
    )

    assert response.status_code == 204

    response = client.get(
        f"/products/{product['id']}", headers=owner["headers"]
    )

    assert response.status_code == 404
