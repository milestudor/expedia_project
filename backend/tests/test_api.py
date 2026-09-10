from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_boston_search_joins_hotels_and_trips() -> None:
    response = client.get("/api/stays", params={"city": "  bOsToN  "})

    assert response.status_code == 200
    stays = response.json()
    assert [stay["trip_id"] for stay in stays] == ["T001", "T002", "T009", "T010"]
    assert stays[0] == {
        "trip_id": "T001",
        "trip_name": "Boston Harbor Weekend",
        "hotel_id": "H001",
        "hotel_name": "Harbor Lantern Hotel",
        "city": "Boston",
        "state": "MA",
        "check_in": "2026-09-18",
        "check_out": "2026-09-20",
        "nights": 2,
        "nightly_rate_usd": "150",
        "stay_price_usd": "300",
    }


def test_city_without_stays_returns_empty_list() -> None:
    response = client.get("/api/stays", params={"city": "Miami"})

    assert response.status_code == 200
    assert response.json() == []


def test_empty_city_is_rejected() -> None:
    response = client.get("/api/stays", params={"city": ""})

    assert response.status_code == 422
