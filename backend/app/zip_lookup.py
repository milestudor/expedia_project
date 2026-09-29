"""Backend-only ZIP lookup; no routes or database dependencies."""

import math
import logging
import re
from typing import TypedDict, NotRequired

import httpx

from .config import get_geoapify_api_key


class _HideProviderRequest(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # HTTPX logs full query strings at INFO level when application logging enables it.
        return "api.geoapify.com" not in record.getMessage()


logging.getLogger("httpx").addFilter(_HideProviderRequest())


class Location(TypedDict):
    postcode: str
    country_code: str
    latitude: float
    longitude: float
    locality: NotRequired[str]


class ZipLookupError(Exception):
    """A configuration or provider failure, with a credential-free message."""


class ZipConfigurationError(ZipLookupError):
    """The provider key is absent or blank."""


def lookup_zip(postcode: str) -> Location | None:
    """Return a verified U.S. location, None if unresolved, or raise ZipLookupError."""
    if not isinstance(postcode, str) or not re.fullmatch(r"[0-9]{5}", postcode):
        raise ValueError("A five-digit U.S. ZIP string is required.")
    key = get_geoapify_api_key()
    if not key:
        raise ZipConfigurationError("Geoapify key is not configured.")
    try:
        response = httpx.get(
            "https://api.geoapify.com/v1/geocode/search",
            params={
                "postcode": postcode,
                "type": "postcode",
                "filter": "countrycode:us",
                "format": "json",
                "apiKey": key,
            },
            timeout=10.0,
        )
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError):
        raise ZipLookupError("Geoapify request failed.") from None
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise ZipLookupError("Geoapify returned an invalid response.")
    for result in payload["results"]:
        if not isinstance(result, dict):
            raise ZipLookupError("Geoapify returned an invalid response.")
        if result.get("postcode") != postcode or result.get("country_code") != "us":
            continue
        lat, lon = result.get("lat"), result.get("lon")
        if any(type(value) not in (int, float) for value in (lat, lon)):
            continue
        if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
            continue
        location: Location = {
            "postcode": postcode, "country_code": "us",
            "latitude": float(lat), "longitude": float(lon),
        }
        locality = result.get("city") or result.get("town") or result.get("village")
        if isinstance(locality, str) and locality.strip():
            location["locality"] = locality.strip()
        return location
    return None
