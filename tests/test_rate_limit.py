def test_login_rate_limit(client):
    for _ in range(5):
        response = client.post(
            "/auth/login",
            data={
                "username": "unknown@example.com",
                "password": "wrong-password",
            },
        )

        assert response.status_code == 401

    response = client.post(
        "/auth/login",
        data={
            "username": "unknown@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 429