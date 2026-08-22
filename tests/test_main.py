def test_read_main(client):
    response = client.get("/")
    
    assert response.status_code == 200
    assert response.json() == {"message": "Hello FastAPI"}


def test_get_user_requires_auth(client):
    response = client.get("/users/me")
    
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
