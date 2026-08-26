def test_get_products_filter_and_sort(client, user_factory, product_factory):
    user = user_factory()

    product_factory(user["headers"], price=10)
    product_factory(user["headers"], price=20)
    product_factory(user["headers"], price=30)

    response = client.get(
        "/products/?min_price=20&sort_by=price&order=desc",
        headers=user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert data["items"][0]["price"] == 30
    assert data["items"][1]["price"] == 20


def test_get_products_pagination(client, user_factory, product_factory):
    user = user_factory()

    product_factory(user["headers"], price=10)
    product_factory(user["headers"], price=20)
    product_factory(user["headers"], price=30)

    response = client.get(
        "/products/?page=2&limit=2",
        headers=user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 3
    assert data["page"] == 2
    assert data["limit"] == 2
    assert data["total_pages"] == 2
    assert len(data["items"]) == 1


def test_get_products_invalid_price_range(client, user_factory):
    user = user_factory()

    response = client.get(
        "/products/?min_price=100&max_price=10",
        headers=user["headers"],
    )

    assert response.status_code == 422

    data = response.json()

    assert data["detail"] == ("min_price must be less than or equal to max_price")


def test_update_nonexistent_product(client, user_factory):
    user = user_factory()

    response = client.put(
        "/products/999999",
        headers=user["headers"],
        json={
            "name": "Updated Product",
            "price": 99.9,
            "quantity": 10,
            "description": "Updated description",
        },
    )

    assert response.status_code == 404


def test_patch_nonexistent_product(client, user_factory):
    user = user_factory()

    response = client.patch(
        "/products/999999",
        headers=user["headers"],
        json={
            "price": 99.9,
        },
    )

    assert response.status_code == 404
