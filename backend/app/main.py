from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class Stay(BaseModel):
    trip_id: str
    trip_name: str
    hotel_id: str
    hotel_name: str
    city: str
    state: str
    check_in: date
    check_out: date
    nights: int
    nightly_rate_usd: Decimal
    stay_price_usd: Decimal


def _read_csv(name: str) -> list[dict[str, str]]:
    with (DATA_DIR / name).open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def search_stays(city: str) -> list[Stay]:
    normalized_city = city.strip().casefold()
    if not normalized_city:
        return []

    hotels = {hotel["hotel_id"]: hotel for hotel in _read_csv("hotels.csv")}
    stays: list[Stay] = []

    for trip in _read_csv("trips.csv"):
        hotel = hotels.get(trip["hotel_id"])
        if hotel is None or hotel["city"].casefold() != normalized_city:
            continue

        check_in = date.fromisoformat(trip["check_in"])
        check_out = date.fromisoformat(trip["check_out"])
        nights = (check_out - check_in).days
        nightly_rate = Decimal(hotel["nightly_rate_usd"])
        stays.append(
            Stay(
                trip_id=trip["trip_id"],
                trip_name=trip["trip_name"],
                hotel_id=hotel["hotel_id"],
                hotel_name=hotel["hotel_name"],
                city=hotel["city"],
                state=hotel["state"],
                check_in=check_in,
                check_out=check_out,
                nights=nights,
                nightly_rate_usd=nightly_rate,
                stay_price_usd=nightly_rate * nights,
            )
        )

    return stays


app = FastAPI(title="Expedia Lite API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/stays", response_model=list[Stay])
def get_stays(city: str = Query(min_length=1)) -> list[Stay]:
    return search_stays(city)
