from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def package_payload() -> dict[str, object]:
    return {
        "source_address": "Dizengoff Street 50, Tel Aviv",
        "source_latitude": 32.078,
        "source_longitude": 34.774,
        "destination_address": "Abba Hillel Street 10, Ramat Gan",
        "destination_latitude": 32.084,
        "destination_longitude": 34.802,
        "deadline": "14:00",
    }


def test_package_crud_lifecycle(client: TestClient) -> None:
    create_response = client.post("/packages", json=package_payload())

    assert create_response.status_code == 201
    created = create_response.json()
    package_id = created["id"]
    assert package_id > 0
    assert created["source_address"] == "Dizengoff Street 50, Tel Aviv"
    assert created["deadline"] == "14:00:00"
    assert created["status"] == "waiting"

    list_response = client.get("/packages")

    assert list_response.status_code == 200
    assert list_response.json() == [created]

    get_response = client.get(f"/packages/{package_id}")

    assert get_response.status_code == 200
    assert get_response.json() == created

    update_response = client.patch(
        f"/packages/{package_id}",
        json={"deadline": "16:30", "status": "picked_up"},
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["deadline"] == "16:30:00"
    assert updated["status"] == "picked_up"
    assert updated["source_address"] == created["source_address"]

    delete_response = client.delete(f"/packages/{package_id}")

    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert client.get(f"/packages/{package_id}").status_code == 404
    assert client.get("/packages").json() == []


@pytest.mark.parametrize("method", ["get", "patch", "delete"])
def test_missing_package_returns_404(client: TestClient, method: str) -> None:
    request = getattr(client, method)
    kwargs = {"json": {"status": "delivered"}} if method == "patch" else {}

    response = request("/packages/999", **kwargs)

    assert response.status_code == 404
    assert response.json() == {"detail": "Package not found"}


@pytest.mark.parametrize("deadline", ["07:59", "24:00", "not-a-time"])
def test_create_rejects_invalid_deadlines(
    client: TestClient,
    deadline: str,
) -> None:
    payload = package_payload()
    payload["deadline"] = deadline

    response = client.post("/packages", json=payload)

    assert response.status_code == 422
    assert client.get("/packages").json() == []


def test_create_rejects_blank_address(client: TestClient) -> None:
    payload = package_payload()
    payload["source_address"] = "   "

    response = client.post("/packages", json=payload)

    assert response.status_code == 422


def test_package_id_must_be_positive(client: TestClient) -> None:
    response = client.get("/packages/0")

    assert response.status_code == 422
