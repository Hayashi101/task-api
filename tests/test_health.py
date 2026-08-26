from sqlalchemy.exc import SQLAlchemyError

from app.db.session import get_db
from app.main import app


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_check(client):
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_readiness_check_database_unavailable(client):
    def broken_get_db():
        class BrokenDB:
            def execute(self, *args, **kwargs):
                raise SQLAlchemyError("Database connection failed")

        yield BrokenDB()

    original_override = app.dependency_overrides[get_db]
    app.dependency_overrides[get_db] = broken_get_db

    try:
        response = client.get("/ready")

        assert response.status_code == 503
        assert response.json() == {
            "detail": "Database unavailable",
        }
    finally:
        app.dependency_overrides[get_db] = original_override
