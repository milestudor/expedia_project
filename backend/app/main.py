from __future__ import annotations

import csv
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Iterator, Literal

from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_DATABASE = DATA_DIR / "expedia_lite.db"


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


class User(BaseModel):
    user_id: str
    name: str
    email: str


class BookingCreate(BaseModel):
    user_id: str
    trip_id: str


class BookingStatusUpdate(BaseModel):
    status: Literal["confirmed", "cancelled"]


class Booking(BaseModel):
    booking_id: str
    user_id: str
    user_name: str
    trip_id: str
    trip_name: str
    hotel_name: str
    city: str
    check_in: date
    check_out: date
    total_price_usd: Decimal
    status: Literal["confirmed", "cancelled"]
    created_at: datetime


def _read_csv(name: str) -> list[dict[str, str]]:
    with (DATA_DIR / name).open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def _connect(database: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def _database(database: Path) -> Iterator[sqlite3.Connection]:
    connection = _connect(database)
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def initialize_database(database: Path) -> None:
    database.parent.mkdir(parents=True, exist_ok=True)
    with _database(database) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS hotels (
                hotel_id TEXT PRIMARY KEY, hotel_name TEXT NOT NULL, city TEXT NOT NULL,
                state TEXT NOT NULL, nightly_rate_usd NUMERIC NOT NULL CHECK (nightly_rate_usd >= 0)
            );
            CREATE TABLE IF NOT EXISTS trips (
                trip_id TEXT PRIMARY KEY, hotel_id TEXT NOT NULL REFERENCES hotels(hotel_id),
                trip_name TEXT NOT NULL, check_in TEXT NOT NULL, check_out TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(user_id),
                trip_id TEXT NOT NULL REFERENCES trips(trip_id),
                status TEXT NOT NULL CHECK (status IN ('confirmed', 'cancelled')), created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS id_sequences (
                name TEXT PRIMARY KEY, next_value INTEGER NOT NULL
            );
            """
        )
        seeds = [
            ("hotels", "INSERT INTO hotels VALUES (:hotel_id, :hotel_name, :city, :state, :nightly_rate_usd)", "hotels.csv"),
            ("trips", "INSERT INTO trips VALUES (:trip_id, :hotel_id, :trip_name, :check_in, :check_out)", "trips.csv"),
            ("users", "INSERT INTO users VALUES (:user_id, :name, :email)", "users.csv"),
            ("bookings", "INSERT INTO bookings VALUES (:booking_id, :user_id, :trip_id, :status, :created_at)", "bookings.csv"),
        ]
        for table, statement, filename in seeds:
            if connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0:
                connection.executemany(statement, _read_csv(filename))
        maximum = max((int(row[0][1:]) for row in connection.execute("SELECT booking_id FROM bookings")), default=0)
        connection.execute(
            "INSERT OR IGNORE INTO id_sequences VALUES ('booking', ?)", (maximum + 1,)
        )


def _stay_from_row(row: sqlite3.Row) -> Stay:
    values = dict(row)
    check_in = date.fromisoformat(values["check_in"])
    check_out = date.fromisoformat(values["check_out"])
    nights = (check_out - check_in).days
    nightly_rate = Decimal(str(values["nightly_rate_usd"]))
    return Stay(**values, nights=nights, stay_price_usd=nightly_rate * nights)


def _booking_from_row(row: sqlite3.Row) -> Booking:
    values = dict(row)
    nights = (date.fromisoformat(values["check_out"]) - date.fromisoformat(values["check_in"])).days
    values["total_price_usd"] = Decimal(str(values.pop("nightly_rate_usd"))) * nights
    return Booking(**values)


def create_app(database: Path = DEFAULT_DATABASE) -> FastAPI:
    initialize_database(database)
    application = FastAPI(title="Expedia Lite API", version="2.0.0")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["*"],
    )

    @application.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/api/stays", response_model=list[Stay])
    def get_stays(q: str = Query(min_length=1)) -> list[Stay]:
        normalized = q.strip().casefold()
        if not normalized:
            raise HTTPException(status_code=422, detail="Search text is required")
        query = f"%{normalized}%"
        with _database(database) as connection:
            rows = connection.execute(
                """SELECT t.trip_id, t.trip_name, h.hotel_id, h.hotel_name, h.city, h.state,
                          t.check_in, t.check_out, h.nightly_rate_usd
                   FROM trips t JOIN hotels h ON h.hotel_id = t.hotel_id
                   WHERE lower(h.hotel_name) LIKE ? OR lower(h.city) LIKE ? ORDER BY t.trip_id""",
                (query, query),
            ).fetchall()
        return [_stay_from_row(row) for row in rows]

    @application.get("/api/users", response_model=list[User])
    def get_users() -> list[User]:
        with _database(database) as connection:
            rows = connection.execute("SELECT * FROM users ORDER BY user_id").fetchall()
        return [User(**dict(row)) for row in rows]

    booking_query = """
        SELECT b.booking_id, b.user_id, u.name AS user_name, b.trip_id, t.trip_name,
               h.hotel_name, h.city, t.check_in, t.check_out, h.nightly_rate_usd,
               b.status, b.created_at
        FROM bookings b JOIN users u ON u.user_id = b.user_id
        JOIN trips t ON t.trip_id = b.trip_id JOIN hotels h ON h.hotel_id = t.hotel_id
    """

    @application.get("/api/bookings", response_model=list[Booking])
    def get_bookings() -> list[Booking]:
        with _database(database) as connection:
            rows = connection.execute(booking_query + " ORDER BY b.created_at DESC, b.booking_id DESC").fetchall()
        return [_booking_from_row(row) for row in rows]

    @application.post("/api/bookings", response_model=Booking, status_code=status.HTTP_201_CREATED)
    def create_booking(payload: BookingCreate) -> Booking:
        with _database(database) as connection:
            user_exists = connection.execute("SELECT 1 FROM users WHERE user_id = ?", (payload.user_id,)).fetchone()
            trip_exists = connection.execute("SELECT 1 FROM trips WHERE trip_id = ?", (payload.trip_id,)).fetchone()
            if not user_exists or not trip_exists:
                raise HTTPException(status_code=404, detail="User or trip not found")
            next_value = connection.execute(
                "SELECT next_value FROM id_sequences WHERE name = 'booking'"
            ).fetchone()[0]
            booking_id = f"B{next_value:03d}"
            connection.execute(
                "UPDATE id_sequences SET next_value = next_value + 1 WHERE name = 'booking'"
            )
            connection.execute(
                "INSERT INTO bookings VALUES (?, ?, ?, 'confirmed', ?)",
                (booking_id, payload.user_id, payload.trip_id, datetime.now(timezone.utc).isoformat()),
            )
            row = connection.execute(booking_query + " WHERE b.booking_id = ?", (booking_id,)).fetchone()
        return _booking_from_row(row)

    @application.patch("/api/bookings/{booking_id}", response_model=Booking)
    def update_booking(booking_id: str, payload: BookingStatusUpdate) -> Booking:
        with _database(database) as connection:
            result = connection.execute("UPDATE bookings SET status = ? WHERE booking_id = ?", (payload.status, booking_id))
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Booking not found")
            row = connection.execute(booking_query + " WHERE b.booking_id = ?", (booking_id,)).fetchone()
        return _booking_from_row(row)

    @application.delete(
        "/api/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
    )
    def delete_booking(booking_id: str) -> Response:
        with _database(database) as connection:
            result = connection.execute("DELETE FROM bookings WHERE booking_id = ?", (booking_id,))
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Booking not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return application


app = create_app()
