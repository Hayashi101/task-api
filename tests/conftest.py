from uuid import uuid4

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app

from app.models import product as product_model
from app.models import user as user_model

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client
        
    app.dependency_overrides.clear()
    
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def user_factory(client):
    def create_user():
        email = f"user_{uuid4().hex}@example.com"
        password = "Password123"

        # Register
        response = client.post(
            "/users/register",
            json={
                "email": email,
                "password": password,
            },
        )

        assert response.status_code == 201

        # Login
        response = client.post(
            "/auth/login",
            data={
                "username": email,
                "password": password,
            },
        )

        assert response.status_code == 200

        token = response.json()["access_token"]

        return {
            "email": email,
            "password": password,
            "token": token,
            "headers": {
                "Authorization": f"Bearer {token}",
            },
        }

    return create_user


@pytest.fixture
def product_factory(client):
    def create_product(headers):
        product_name = f"Product-{uuid4().hex}"

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

    return create_product
