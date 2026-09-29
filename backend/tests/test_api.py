import sqlite3
from unittest.mock import Mock
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app import main
from backend.app.zip_lookup import ZipConfigurationError, ZipLookupError


@pytest.mark.parametrize("outcome,code,body", [
    ({"postcode": "16802", "country_code": "us", "latitude": 40.8, "longitude": -77.86},
     200, {"postcode": "16802", "country_code": "us", "latitude": 40.8, "longitude": -77.86}),
    (None, 404, {"detail": "ZIP 16802 could not be resolved."}),
    (ZipConfigurationError("private configuration detail"), 503,
     {"detail": "Geoapify key is not configured."}),
    (ZipLookupError("private provider detail"), 502,
     {"detail": "Location provider request failed."}),
])
def test_demo_zip_route(client, monkeypatch, outcome, code, body):
    controller = Mock()
    if isinstance(outcome, Exception):
        controller.side_effect = outcome
    else:
        controller.return_value = outcome
    monkeypatch.setattr(main, "lookup_zip", controller)
    response = client.get("/api/demo/zip-location", params={"postcode": "16802"})
    assert response.status_code == code
    assert response.json() == body
    controller.assert_called_once_with("16802")


@pytest.fixture
def database(tmp_path: Path) -> Path:
    return tmp_path / "test.db"


@pytest.fixture
def client(database: Path) -> TestClient:
    return TestClient(create_app(database))


@pytest.mark.parametrize("value", [None, "", " \t\n", "test-placeholder"])
def test_health_reports_only_key_status(client: TestClient, monkeypatch, value) -> None:
    monkeypatch.delenv("GEOAPIFY_API_KEY", raising=False)
    if value is not None:
        monkeypatch.setenv("GEOAPIFY_API_KEY", value)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "geoapify": "key is configured" if value and value.strip() else "key is not configured",
    }


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


@pytest.mark.parametrize("postcode", [None, "", "1234", "123456", "abcde", "１２３４５", "16802-1234"])
def test_invalid_zip_never_calls_provider(client, monkeypatch, postcode):
    controller = Mock()
    monkeypatch.setattr(main, "lookup_zip", controller)
    response = client.get("/api/demo/zip-location", params={} if postcode is None else {"postcode": postcode})
    assert response.status_code == 422
    assert response.json() == {"detail": "Enter a five-digit U.S. ZIP code."}
    controller.assert_not_called()


def test_zip_preserves_leading_zero_and_trims(client, monkeypatch):
    controller = Mock(return_value=None)
    monkeypatch.setattr(main, "lookup_zip", controller)
    response = client.get("/api/demo/zip-location", params={"postcode": " 02108 "})
    controller.assert_called_once_with("02108")
    assert response.status_code == 404
    assert response.json() == {"detail": "ZIP 02108 could not be resolved."}
