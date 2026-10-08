# Database and Part 1 API comparison

Observed October 1, 2026 on `assignment2_part2_in_class`. This is agent-assisted evidence, not a claim that the student personally completed the manual checkpoint. No schema, application code, or database records were changed.

## Database evidence

Actual database: `/Users/milestudor/Documents/ChatGPT/expedia_project/backend/data/expedia_lite.db`.

The database was opened read-only with SQLite. Its actual table definitions, column metadata, and three existing hotel rows are captured in [database-inspection.json](database-inspection.json). The DB Explorer UI check is incomplete: opening the project in VS Code produced a blank window. No standalone DB Browser for SQLite was found in the standard application directories. The student should open the path above in their database viewer to complete that manual checkpoint.

`hotels` columns:

| Column | Definition |
| --- | --- |
| hotel_id | TEXT PRIMARY KEY |
| hotel_name | TEXT NOT NULL |
| city | TEXT NOT NULL |
| state | TEXT NOT NULL |
| nightly_rate_usd | NUMERIC NOT NULL CHECK (nightly_rate_usd >= 0) |

Sample existing rows:

| hotel_id | hotel_name | city | state | nightly_rate_usd |
| --- | --- | --- | --- | --- |
| H001 | Harbor Lantern Hotel | Boston | MA | 150 |
| H002 | Maple Square Inn | Boston | MA | 120 |
| H003 | Metro Garden Hotel | New York | NY | 200 |

## Live browser evidence

Submitted ZIP `16802` once in the Part 1 application. Chrome Network showed `GET http://127.0.0.1:5173/api/hotels?postcode=16802`, HTTP 200, with response header date `Thu, 01 Oct 2026 19:02:34 GMT` (3:02 p.m. EDT). The UI displayed 21 hotels near State College. The response reports radius 5000 meters, limit 50, and `limit_reached: false`.

Selected that request and inspected its Response panel. [hotel-response-16802.json](hotel-response-16802.json) is the complete response copied from that request and formatted as JSON, without making another provider request. [network-response.png](network-response.png) captures the application and selected Network response; use the JSON file for complete readable fields.

The first hotel is Scholar Hotel State College, at 205 East Beaver Avenue, State College, PA 16801, with latitude `40.7946313` and longitude `-77.8590467`. Its `place_id` is preserved in the response evidence. The searched ZIP differs from this hotel's address ZIP: a radius search can return nearby hotels in other postcodes.

## Field comparison

| API information | API field | Matching database column—or missing |
| --- | --- | --- |
| Provider hotel ID | hotels[].place_id | Missing provider-ID storage/mapping. `hotels.hotel_id` is an analogous identifier column, but existing values are sample IDs such as H001, not provider IDs. |
| Hotel name | hotels[].name | `hotels.hotel_name` is the conceptual match; it requires a value, whereas the API contract allows null. |
| Address | hotels[].address | Missing. City and state do not store a full address. |
| Latitude | hotels[].latitude | Missing. |
| Longitude | hotels[].longitude | Missing. |

All 21 returned hotel objects contain exactly `place_id`, `name`, `address`, `latitude`, and `longitude`. No nightly rate, price, currency, or rooms-available field appears in this actual Part 1 response. The existing sample `nightly_rate_usd` values do not establish rates for these API hotels. This observation concerns the application's normalized API response, not every possible Geoapify product or raw provider field.

## Date-specific storage and gaps for the next prompt

Actual tables: `hotels`, `trips`, `users`, `bookings`, and `id_sequences`. `trips` relates a sample hotel to check-in/check-out dates; `bookings` relates a user to a trip and status. Neither stores a per-date nightly rate or rooms available. There is no hotel/date inventory table or unique hotel/date relationship.

The next schema request should address:

- Separate saved API hotel storage keyed by the provider ID, preserving the Assignment 1 sample tables and rows.
- Nullable name/address and required valid latitude/longitude for saved API hotels.
- Daily records relating a saved hotel to a stay date, that night's simulated rate, and a nonnegative available-room count; each hotel/date pair must be unique and reference its saved hotel.
- A searched-ZIP/location association for future retrieval of saved results; the searched ZIP must not be inferred from the hotel's address postcode.
- Clear provenance for classroom rates and availability, since neither is supplied by this response. The legacy required sample price must not force a fabricated provider hotel price.

No schema migration, saved-hotel feature, new dependencies, commit, or push was performed. Existing tests were not rerun because this task only inspected state and recorded evidence.
