"""Local hotel persistence; no provider calls or Assignment 1 writes."""
from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

ProviderId = Annotated[str, StringConstraints(min_length=1)]
Postcode = Annotated[str, StringConstraints(pattern=r'^[0-9]{5}$')]
Latitude = Annotated[float, Field(ge=-90, le=90, allow_inf_nan=False)]
Longitude = Annotated[float, Field(ge=-180, le=180, allow_inf_nan=False)]


class Hotel(BaseModel):
    place_id: ProviderId
    name: str | None = None
    address: str | None = None
    latitude: Latitude
    longitude: Longitude


class Center(BaseModel):
    postcode: Postcode
    country_code: Literal['us'] = 'us'
    latitude: Latitude
    longitude: Longitude
    locality: str | None = None


class SaveHotel(BaseModel):
    hotel: Hotel
    center: Center


class HotelIds(BaseModel):
    place_ids: list[ProviderId] = Field(max_length=50)


def save_hotel(connection, request: SaveHotel):
    h, center = request.hotel, request.center
    connection.execute('''INSERT INTO saved_hotels VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(hotel_id) DO NOTHING''',
        (h.place_id, h.name, h.address, h.latitude, h.longitude))
    connection.execute('''INSERT INTO saved_zip_contexts VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(postcode) DO NOTHING''',
        (center.postcode, center.country_code, center.latitude, center.longitude, center.locality))
    connection.execute('''INSERT INTO saved_hotel_zips VALUES (?, ?)
        ON CONFLICT(hotel_id, postcode) DO NOTHING''', (h.place_id, center.postcode))
    for day in range(10, 15):
        connection.execute('''INSERT INTO demo_hotel_nights (hotel_id, stay_date) VALUES (?, ?)
            ON CONFLICT(hotel_id, stay_date) DO NOTHING''', (h.place_id, date(2026, 10, day).isoformat()))


def get_saved_hotels(connection, postcode):
    center = connection.execute('SELECT * FROM saved_zip_contexts WHERE postcode=?', (postcode,)).fetchone()
    rows = connection.execute('''SELECT h.* FROM saved_hotels h JOIN saved_hotel_zips z
        ON h.hotel_id=z.hotel_id WHERE z.postcode=? ORDER BY h.hotel_id''', (postcode,)).fetchall()
    hotels = []
    for row in rows:
        hotel = dict(row)
        hotel['place_id'] = hotel.pop('hotel_id')
        hotel['demo_nights'] = [dict(n) for n in connection.execute('''SELECT stay_date,
            nightly_rate_cents, rooms_available FROM demo_hotel_nights WHERE hotel_id=?
            ORDER BY stay_date''', (hotel['place_id'],))]
        hotels.append(hotel)
    return {'center': dict(center) if center else None, 'hotels': hotels, 'source': 'local'}


def remove_hotel(connection, hotel_id):
    postcodes = [r[0] for r in connection.execute(
        'SELECT postcode FROM saved_hotel_zips WHERE hotel_id=?', (hotel_id,))]
    connection.execute('DELETE FROM demo_hotel_nights WHERE hotel_id=?', (hotel_id,))
    connection.execute('DELETE FROM saved_hotel_zips WHERE hotel_id=?', (hotel_id,))
    connection.execute('DELETE FROM saved_hotels WHERE hotel_id=?', (hotel_id,))
    for postcode in postcodes:
        connection.execute('''DELETE FROM saved_zip_contexts WHERE postcode=? AND NOT EXISTS (
            SELECT 1 FROM saved_hotel_zips WHERE saved_hotel_zips.postcode=saved_zip_contexts.postcode)''',
            (postcode,))
