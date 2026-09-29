"""Geoapify hotel discovery, independent of the original CSV/SQLite stay model."""
import math

import httpx

from .config import get_geoapify_api_key
from .zip_lookup import Location, ZipLookupError

RADIUS_METERS = 5000
RESULT_LIMIT = 50


def _text(value):
    return value.strip() if isinstance(value, str) and value.strip() else None


def find_hotels(location: Location) -> dict:
    lon, lat = location["longitude"], location["latitude"]
    try:
        response = httpx.get(
            "https://api.geoapify.com/v2/places",
            params={"categories": "accommodation.hotel", "filter": f"circle:{lon},{lat},{RADIUS_METERS}",
                    "bias": f"proximity:{lon},{lat}", "limit": RESULT_LIMIT,
                    "apiKey": get_geoapify_api_key()},
            timeout=15.0,
        )
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError):
        raise ZipLookupError("Hotel provider request failed. Please try again later.") from None
    if not isinstance(payload, dict) or not isinstance(payload.get("features"), list):
        raise ZipLookupError("Hotel provider returned an invalid response.")
    hotels = []
    seen = set()
    for feature in payload["features"]:
        if not isinstance(feature, dict) or not isinstance(feature.get("properties"), dict):
            raise ZipLookupError("Hotel provider returned an invalid hotel record.")
        properties = feature["properties"]
        place_id = _text(properties.get("place_id"))
        latitude, longitude = properties.get("lat"), properties.get("lon")
        if not place_id or any(type(v) not in (float, int) or not math.isfinite(v) for v in (latitude, longitude)):
            raise ZipLookupError("Hotel provider returned a hotel without a valid identifier or coordinates.")
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise ZipLookupError("Hotel provider returned invalid coordinates.")
        if place_id in seen:
            continue
        seen.add(place_id)
        hotels.append({"place_id": place_id, "name": _text(properties.get("name")),
                       "address": _text(properties.get("formatted")),
                       "latitude": latitude, "longitude": longitude})
    return {"center": location, "hotels": hotels, "radius_meters": RADIUS_METERS,
            "limit": RESULT_LIMIT, "limit_reached": len(payload["features"]) >= RESULT_LIMIT}
