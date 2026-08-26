from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.rate_limit import limiter
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import product as product_model  # noqa: F401
from app.models.user import User

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture
def client():
    limiter.reset()

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

    limiter.reset()

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

        user_data = response.json()

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
            "id": user_data["id"],
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
    def create_product(headers, **overrides):
        product_data = {
            "name": f"Product-{uuid4().hex}",
            "price": 10.5,
            "quantity": 3,
            "description": "Authorization test",
        }

        product_data.update(overrides)

        response = client.post(
            "/products/",
            headers=headers,
            json=product_data,
        )

        assert response.status_code == 201

        return response.json()

    return create_product


@pytest.fixture
def admin_factory(user_factory):
    def create_admin():
        user = user_factory()

        db = TestingSessionLocal()
        try:
            db_user = db.scalar(select(User).where(User.email == user["email"]))
            db_user.role = "admin"
            db.commit()
        finally:
            db.close()

        return user

    return create_admin
