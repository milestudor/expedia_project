# Saved hotel schema — October 1, 2026

The student reports completing the preflight comparison in DB Explorer. This change implements only the requested additive storage schema.

Database: `/Users/milestudor/Documents/ChatGPT/expedia_project/backend/data/expedia_lite.db`.

## Tables and mapping

`backend/app/migrations.py` creates the two tables with `CREATE TABLE IF NOT EXISTS`, called by the existing database initializer at startup. It works with a fresh database and the existing seeded database, and leaves existing tables and rows intact. Repeating the migration preserves saved records. No dependencies were added.

| API response field | saved_hotels column | Constraint |
| --- | --- | --- |
| hotels[].place_id | hotel_id | TEXT NOT NULL PRIMARY KEY; preserve verbatim, case-sensitive uniqueness |
| hotels[].name | name | Nullable TEXT |
| hotels[].address | address | Nullable TEXT |
| hotels[].latitude | latitude | Required numeric latitude, -90 through 90 |
| hotels[].longitude | longitude | Required numeric longitude, -180 through 180 |

The mapping is documented for the later save operation; this change adds no save endpoint or automatic persistence. Provider IDs are not trimmed, converted, or replaced by sample IDs.

`demo_hotel_nights` has a required `hotel_id` referencing `saved_hotels(hotel_id)` and a required `stay_date`. The composite primary key `(hotel_id, stay_date)` prevents duplicate nights. Date checks enforce YYYY-MM-DD and a valid calendar date (years 0001–9999). Required integer `nightly_rate_cents` defaults to 10000 and required integer `rooms_available` defaults to 20; both reject negative and fractional stored values.

Rates and room counts are fictional classroom defaults, not API prices or inventory. Defaults apply when inserting a row with those fields omitted; they do not generate hotels or dated rows. Both tables are empty after this migration.

The existing connection helper enables `PRAGMA foreign_keys = ON` on every backend connection, and the migration checks it. SQLite foreign-key enforcement is connection-specific: enable it in any external writer as well. Deleting a saved hotel with nightly records is restricted by the default foreign-key behavior; no cascading deletion was introduced.

## Verification

- 88 backend tests passed, including migration preservation/repeatability, fresh initialization, exact provider ID retention, nullable fields, uniqueness, default values, zero values, coordinate bounds, calendar dates, integer constraints, and foreign-key rejection.
- 24 frontend tests passed; frontend lint and production build passed.
- Applied the initializer twice to the real database and compared all five original tables against a snapshot captured before editing: original CREATE TABLE definitions and every row unchanged.
- Both new tables are present and empty; `PRAGMA foreign_key_check` reports no violations.
- Existing third-party Starlette/AnyIO deprecation warning remains.
- Part 1 route and frontend source code are unchanged. No new live provider request or browser verification was performed for this schema-only change; the student will verify the database next.

No frontend controls, chatbot features, ZIP associations, seeding of daily records, commits, or pushes were added. Stop here for manual database review.
