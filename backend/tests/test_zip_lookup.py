from unittest.mock import Mock

import httpx
import pytest

from backend.app import zip_lookup


@pytest.fixture
def provider(monkeypatch):
    monkeypatch.setenv("GEOAPIFY_API_KEY", "fake-test-key")
    request = Mock()
    monkeypatch.setattr(zip_lookup.httpx, "get", request)
    return request


def result(**changes):
    return {"postcode": "16802", "country_code": "us", "lat": 40.8, "lon": -77.86,
            "city": "University Park", **changes}


def respond(provider, payload, status=200):
    provider.return_value = httpx.Response(
        status, json=payload, request=httpx.Request("GET", "https://example.test/")
    )


def test_success_and_request_contract(provider):
    respond(provider, {"results": [result()]})
    assert zip_lookup.lookup_zip("16802") == {
        "postcode": "16802", "country_code": "us", "latitude": 40.8,
        "longitude": -77.86, "locality": "University Park",
    }
    provider.assert_called_once_with(
        "https://api.geoapify.com/v1/geocode/search",
        params={"postcode": "16802", "type": "postcode", "filter": "countrycode:us",
                "format": "json", "apiKey": "fake-test-key"}, timeout=10.0,
    )


@pytest.mark.parametrize("changes", [
    {"postcode": "16801"}, {"country_code": "ca"}, {"lat": None},
    {"lat": 91}, {"lon": -181}, {"lat": float("inf")},
    {"lon": float("nan")}, {"lat": True}, {"lat": "40.8"},
])
def test_unresolved_invalid_location(provider, changes):
    provider.return_value.json.return_value = {"results": [result(**changes)]}
    assert zip_lookup.lookup_zip("16802") is None


def test_empty_results(provider):
    respond(provider, {"results": []})
    assert zip_lookup.lookup_zip("16802") is None


def test_skips_mismatch_and_omits_absent_locality(provider):
    respond(provider, {"results": [result(postcode="16801"), result(city=None)]})
    location = zip_lookup.lookup_zip("16802")
    assert location is not None and "locality" not in location


@pytest.mark.parametrize("status", [401, 429, 500])
def test_provider_http_failure(provider, status):
    respond(provider, {}, status)
    with pytest.raises(zip_lookup.ZipLookupError, match="^Geoapify request failed.$"):
        zip_lookup.lookup_zip("16802")


@pytest.mark.parametrize("error", [httpx.ReadTimeout("credential-bearing text"),
                                  httpx.ConnectError("credential-bearing text"),
                                  ValueError("credential-bearing text")])
def test_sanitized_failure(provider, error):
    provider.side_effect = error
    with pytest.raises(zip_lookup.ZipLookupError) as caught:
        zip_lookup.lookup_zip("16802")
    assert str(caught.value) == "Geoapify request failed."
    assert caught.value.__suppress_context__


@pytest.mark.parametrize("payload", [{}, {"results": None}, {"results": [None]}])
def test_malformed_response_is_failure(provider, payload):
    respond(provider, payload)
    with pytest.raises(zip_lookup.ZipLookupError, match="invalid response"):
        zip_lookup.lookup_zip("16802")


def test_missing_key_does_not_request(provider, monkeypatch):
    monkeypatch.setenv("GEOAPIFY_API_KEY", "  ")
    with pytest.raises(zip_lookup.ZipLookupError, match="not configured"):
        zip_lookup.lookup_zip("16802")
    provider.assert_not_called()


def test_httpx_provider_url_is_not_logged(caplog):
    import logging
    with caplog.at_level(logging.INFO, logger="httpx"):
        logging.getLogger("httpx").info("HTTP Request: %s", "https://api.geoapify.com/?apiKey=fake-test-key")
    assert "fake-test-key" not in caplog.text
