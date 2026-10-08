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
- Assignment 2 Part 2 features are outside the frozen Part 1 submission; preserve that behavior while extending the application.

## Assignment 2 — revised Part 2 scope (October 1, 2026)

- Preserve SQLite local storage, Add/Remove, duplicate prevention, local-first lookup, and Assignment 1 tables and records.
- `hotel_chat.py` owns provider requests, proposed SQL validation, bounded read-only retrieval, and grounded second-request answer generation. `model_preflight.py` checks provider availability and quota without generation.
- FastAPI owns chatbot input validation and HTTP error mapping. `HotelChat.vue` owns request state and renders answers, canonical nightly evidence, and the workflow trace.
- Demo prices and rooms must be labeled simulated course data. Stay calculations exclude checkout; missing nights cannot imply availability or a complete total.
- Use one approved provider, with credentials only on the backend. Fixed model fixtures are verification evidence, never live-call evidence or production fallbacks.
- Model-proposed hotel retrieval must never mutate records or book. Application-owned writes to conversation/history tables are required and must remain separate from the read-only hotel connection. No dependency installation without CHECK, exact installation explanation, student approval, TAKE ACTION, and VERIFY.
- Part 2 is due October 8, 2026, at 11:59 PM Eastern. Keep submission claims pending until observed, including live model calls and student review.

## Supplied RAG-context activity

- Use OpenAI Responses with OPEN_AI passed explicitly and OPENAI_MODEL (class default gpt-5.6-luna). Runtime prompt is prompts/hotel-assistant.md, loaded at startup and versioned in traces.
- chat_history.py owns per-stage conversation writes/reads and interrupted-turn recovery; history survives frontend refresh/backend restart. Never fabricate a completed answer for a failed attempt.
- Follow-up requests include bounded successful history, while each hotel answer requires fresh checked retrieval. Approved hotel JOINs use actual postcode column and hotel_id relationships.
- Active requested branch is rag_integration. Preserve all earlier work and do not commit/push without manual review.
