from unittest.mock import Mock

import httpx
import pytest
from fastapi.testclient import TestClient

from backend.app import hotel_search, main
from backend.app.zip_lookup import ZipLookupError

CENTER = {"postcode": "02108", "country_code": "us", "latitude": 42.36, "longitude": -71.06}


def feature(**changes):
    return {"properties": {"place_id": "provider-1", "name": "Test Hotel", "formatted": "Boston",
                           "lat": 42.361, "lon": -71.061, **changes}}


@pytest.fixture
def provider(monkeypatch):
    monkeypatch.setenv("GEOAPIFY_API_KEY", "test-only-secret")
    mock = Mock()
    monkeypatch.setattr(hotel_search.httpx, "get", mock)
    return mock


def respond(provider, payload, status=200):
    provider.return_value = httpx.Response(status, json=payload, request=httpx.Request("GET", "https://example.test"))


def test_places_contract_and_honest_fields(provider):
    respond(provider, {"features": [feature(name=None, formatted=None), feature()]})
    result = hotel_search.find_hotels(CENTER)
    assert len(result["hotels"]) == 1
    assert result["hotels"][0] == {"place_id": "provider-1", "name": None, "address": None,
                                   "latitude": 42.361, "longitude": -71.061}
    params = provider.call_args.kwargs["params"]
    assert params == {"categories": "accommodation.hotel", "filter": "circle:-71.06,42.36,5000",
                      "bias": "proximity:-71.06,42.36", "limit": 50, "apiKey": "test-only-secret"}
    assert "test-only-secret" not in str(result)


def test_empty_is_success(provider):
    respond(provider, {"features": []})
    assert hotel_search.find_hotels(CENTER)["hotels"] == []


@pytest.mark.parametrize("status", [401, 429, 500])
def test_provider_failures_are_not_empty(provider, status):
    respond(provider, {}, status)
    with pytest.raises(ZipLookupError, match="request failed"):
        hotel_search.find_hotels(CENTER)


@pytest.mark.parametrize("payload", [{}, {"features": None}, {"features": [None]},
                                     {"features": [feature(lat=None)]}, {"features": [feature(lon=181)]},
                                     {"features": [feature(place_id="")]}, {"features": [feature(lat=True)]}])
def test_malformed_is_failure(provider, payload):
    respond(provider, payload)
    with pytest.raises(ZipLookupError):
        hotel_search.find_hotels(CENTER)


def test_timeout_sanitized(provider):
    provider.side_effect = httpx.ReadTimeout("secret-provider-url")
    with pytest.raises(ZipLookupError) as caught:
        hotel_search.find_hotels(CENTER)
    assert "secret" not in str(caught.value)


def test_limit_flag(provider):
    respond(provider, {"features": [feature(place_id=str(i)) for i in range(50)]})
    assert hotel_search.find_hotels(CENTER)["limit_reached"] is True


def test_route_gates_places_on_valid_zip(tmp_path, monkeypatch):
    client = TestClient(main.create_app(tmp_path / "test.db"))
    lookup = Mock(return_value=None)
    places = Mock()
    monkeypatch.setattr(main, "lookup_zip", lookup)
    monkeypatch.setattr(main, "find_hotels", places)
    assert client.get('/api/hotels?postcode=1234').status_code == 422
    lookup.assert_not_called()
    assert client.get('/api/hotels?postcode=00000').status_code == 404
    places.assert_not_called()
    lookup.return_value = CENTER
    places.return_value = {"center": CENTER, "hotels": [], "limit": 50}
    response = client.get('/api/hotels?postcode=%2002108%20')
    assert response.status_code == 200
    lookup.assert_called_with('02108')
    places.assert_called_once_with(CENTER)
    places.side_effect = ZipLookupError("Hotel provider request failed. Please try again later.")
    assert client.get('/api/hotels?postcode=02108').status_code == 502
