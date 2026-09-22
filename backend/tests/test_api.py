import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.main import create_app


@pytest.fixture
def database(tmp_path: Path) -> Path:
    return tmp_path / "test.db"


@pytest.fixture
def client(database: Path) -> TestClient:
    return TestClient(create_app(database))


def test_hotel_name_search_joins_sqlite_records(client: TestClient) -> None:
    response = client.get("/api/stays", params={"q": "  lantern  "})
    assert response.status_code == 200
    stays = response.json()
    assert [stay["trip_id"] for stay in stays] == ["T001", "T009"]
    assert stays[0]["hotel_name"] == "Harbor Lantern Hotel"
    assert stays[0]["stay_price_usd"] == "300"


def test_city_search_remains_available(client: TestClient) -> None:
    response = client.get("/api/stays", params={"q": "bOsToN"})
    assert [stay["trip_id"] for stay in response.json()] == ["T001", "T002", "T009", "T010"]


def test_search_without_matches_returns_empty_list(client: TestClient) -> None:
    assert client.get("/api/stays", params={"q": "No Such Hotel"}).json() == []


def test_booking_crud_and_restart_persistence(database: Path) -> None:
    first_client = TestClient(create_app(database))
    created = first_client.post("/api/bookings", json={"user_id": "U001", "trip_id": "T003"})
    assert created.status_code == 201
    booking_id = created.json()["booking_id"]
    assert booking_id == "B004"
    assert any(item["booking_id"] == booking_id for item in first_client.get("/api/bookings").json())

    cancelled = first_client.patch(f"/api/bookings/{booking_id}", json={"status": "cancelled"})
    assert cancelled.json()["status"] == "cancelled"

    restarted_client = TestClient(create_app(database))
    restarted = restarted_client.get("/api/bookings").json()
    assert len(restarted) == 4
    assert next(item for item in restarted if item["booking_id"] == booking_id)["status"] == "cancelled"

    assert restarted_client.delete(f"/api/bookings/{booking_id}").status_code == 204
    final_client = TestClient(create_app(database))
    assert len(final_client.get("/api/bookings").json()) == 3


def test_new_booking_ids_remain_unique_after_delete(client: TestClient) -> None:
    first = client.post("/api/bookings", json={"user_id": "U001", "trip_id": "T003"}).json()
    second = client.post("/api/bookings", json={"user_id": "U002", "trip_id": "T004"}).json()
    client.delete(f"/api/bookings/{first['booking_id']}")
    third = client.post("/api/bookings", json={"user_id": "U003", "trip_id": "T006"}).json()
    assert [first["booking_id"], second["booking_id"], third["booking_id"]] == ["B004", "B005", "B006"]


def test_seeded_ids_are_preserved(client: TestClient, database: Path) -> None:
    client.get("/api/bookings")
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT hotel_id FROM hotels ORDER BY hotel_id LIMIT 1").fetchone()[0] == "H001"
        assert connection.execute("SELECT trip_id FROM trips ORDER BY trip_id LIMIT 1").fetchone()[0] == "T001"
        assert connection.execute("SELECT booking_id FROM bookings ORDER BY booking_id LIMIT 1").fetchone()[0] == "B001"
