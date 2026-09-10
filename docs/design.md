# Part 1 design note

The application has two independently runnable layers. FastAPI owns CSV access and the `hotel_id` join; Vue owns input, request state, and presentation. `GET /api/stays?city=Boston` returns enriched stay records with dates, nights, nightly rate, and derived stay price. City matching trims whitespace and ignores capitalization, while an empty query is rejected at the API boundary.

The earlier Hello Agent calculator informed the repository boundary (`backend/` and `frontend/`), FastAPI app shape, Vue/Vite entry point, local CORS setup, and README run/check sections. Expedia Lite otherwise uses its own domain model, API contract, CSV reader, interface, and tests.

The frontend uses a native form and semantic table. It distinguishes three states: an empty input prompt, a successful results table, and a no-results message. A development proxy keeps browser requests same-origin; explicit CORS origins also support local development.

The CSVs retain the supplied UTF-8 byte-order mark and are read with `utf-8-sig`. Part 1 intentionally does not introduce SQLite, users, bookings, authentication, live inventory, or write operations.
