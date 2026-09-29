# Expedia Lite project guidance

- Keep the Vue application in `frontend/` and the FastAPI application in `backend/`.
- Treat `backend/data/hotels.csv` and `backend/data/trips.csv` as the Part 1 source of truth.
- Join stays by `hotel_id`; city matching is case-insensitive and ignores surrounding whitespace.
- Follow CHECK -> TAKE ACTION -> VERIFY before changing dependencies.
- Update `README.md`, `docs/`, `prompts/`, and `handoffs/current.md` when behavior or verification changes.
- Do not commit or push until the user has manually reviewed the changes and browser results.

## Assignment 2 — Part 1 scope

- The CSV source-of-truth rule above applies to the original sample-stay application. Live discovery uses Geoapify responses, never fabricated or CSV-substituted hotels.
- Model/service: `zip_lookup.py` verifies the requested U.S. postcode; `hotel_search.py` requests and normalizes provider hotels. Neither contains route or UI behavior.
- Controller: FastAPI validates input and maps unresolved/configuration/provider errors to HTTP responses; Vue controls request state and selected provider ID.
- View: `HotelDiscovery.vue` renders honest results and statuses; `HotelMap.vue` renders Leaflet markers and emits selection. Original sample UI is `LegacyApp.vue` at `/sample-stays`.
- Verification loop: CHECK existing environment and dependency availability; explain exact installation and receive student approval before TAKE ACTION; VERIFY installed version, tests, lint, build, and browser behavior. Leaflet 1.9.4 was approved September 29, 2026.
- Assignment 2 Part 2 shortlist features are out of scope for this submission.
