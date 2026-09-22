# Part 2 design note

Vue owns all user interactions: hotel-name or city search, traveler selection, simulated booking, booking history, cancellation, and test deletion. It never accesses storage directly. Every action calls FastAPI through the local `/api` proxy and refreshes history from server state.

FastAPI defines the HTTP boundary and validates request models. `GET /api/stays` searches hotel names and cities; `GET /api/users` supplies the traveler selector; `GET`, `POST`, `PATCH`, and `DELETE /api/bookings` provide CRUD. Cancellation is a status update, so the booking remains visible.

Python's built-in SQLite driver owns persistence. On first startup, tables are created and empty tables are seeded from `hotels.csv`, `trips.csv`, `users.csv`, and `bookings.csv`. Existing IDs are retained. Later startup is non-destructive, and a stored sequence assigns never-reused booking IDs. Hotel/trip records join through `hotel_id`; text search trims input and ignores case.

No authentication, payment processing, live inventory, or concurrent-seat reservation is simulated. Delete is intentionally exposed for assignment test records, while the interface warns that it is permanent.
