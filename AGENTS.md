# Expedia Lite project guidance

- Keep the Vue application in `frontend/` and the FastAPI application in `backend/`.
- Treat `backend/data/hotels.csv` and `backend/data/trips.csv` as the Part 1 source of truth.
- Join stays by `hotel_id`; city matching is case-insensitive and ignores surrounding whitespace.
- Follow CHECK -> TAKE ACTION -> VERIFY before changing dependencies.
- Update `README.md`, `docs/`, `prompts/`, and `handoffs/current.md` when behavior or verification changes.
- Do not commit or push until the user has manually reviewed the changes and browser results.
