# Current handoff

## Implemented

- Latest: ZIP lookup now accepts a five-digit U.S. ZIP text field and sends it as the
  `postcode` query parameter. Vue and FastAPI validate input; leading zeros are preserved.
  This supersedes the fixed-16802 behavior described in earlier entries.

- Added the Vue ZIP lookup demonstration panel below hotel search results. It calls
  only the backend demo route on click, clears stale results, prevents repeated clicks
  while loading, and displays labeled location data or errors.

- Added `GET /api/demo/zip-location` for fixed ZIP `16802`, with 503/404/502 error
  mappings for missing configuration/unresolved ZIP/provider failure.

- Standalone `lookup_zip` controller added in `backend/app/zip_lookup.py`; reads the key
  through the configuration helper and returns a validated location or `None`, with
  sanitized `ZipLookupError` failures. No routes/Vue changes or live Geoapify calls.

- Added `backend/app/config.py` using existing python-dotenv to load the project-root `.env`
  by explicit file-relative path. Backend restart is required after `.env` edits.
- Health preserves `status: ok` and adds only the Geoapify key configuration status;
  absent, empty, and whitespace-only values are unconfigured. No Geoapify calls are made.

- Feature branch: `codex/part-2-sqlite-crud`; Part 1 checkpoint remains in history
- One-time SQLite seeding for hotels, trips, starter users, and starter bookings
- SQLite-backed hotel-name/city search and complete booking CRUD through FastAPI
- Vue booking creation, history, cancellation with record retention, and test deletion
- Persistent, never-reused booking IDs beyond seeded examples

## Verification status

- ZIP input update: 45 backend and 13 frontend tests passed, lint and build passed.
  Checks include invalid/missing ZIPs, leading zeros, whitespace, loading/error behavior,
  and existing hotel search. Provider responses are mocked in automated checks.

- ZIP panel: all 6 frontend tests passed (including existing hotel search/booking checks),
  lint passed, and production build passed. New mocked checks cover on-click requests,
  loading, result clearing, repeated-click prevention, optional locality, backend errors,
  and network failure recovery. No live lookup was made for this UI change; browser
  inspection is left to the user. No dependencies or credentials were added.

- September 24 demo route: 37 backend tests passed, including four mocked controller
  outcomes. Existing backend reloader PID 47087 was identified as this project and
  OpenAPI confirmed the new route loaded; no manual restart was needed. Started the
  frontend using documented `npm run dev`; unrelated processes were preserved.
  Exactly one live local demo-route request returned usable Geoapify data: U.S. ZIP
  16802, State College, latitude 40.803167822, longitude -77.861384958.

- ZIP controller: 33 total backend tests passed using existing dependencies, including
  mocked success, mismatched-location, coordinate validation, provider failures, and
  credential-safe logging checks. Only `"16802"` is approved for a future live demonstration.

- Configuration update: all 10 backend tests passed, including four key-status cases;
  explicit root `.env` path verified from an unrelated working directory with loading mocked.
  One third-party Starlette/AnyIO deprecation warning remains. No dependencies changed.

- Dependency CHECK: SQLite is in Python's standard library; no dependency action was required
- Backend: 6 tests passed, including CRUD, restart persistence, seed non-duplication, and unique IDs
- Frontend: 4 tests passed; lint passed with no warnings; production build passed
- Browser search, no-results, create/read, cancel/retain, delete, refresh, and both-server restart checks passed with test booking `B004`
- `B004` was removed after verification; restart did not reseed the deleted record
- Four Part 2 browser screenshots captured and linked in `report.md`; a silent 98-second assembled demo video now covers all frontend CRUD actions and has been frame-checked
- Demo test bookings `B005` and `B007` were deleted after use. Browser refresh and a direct SQLite check show only the three starter bookings (`B001`–`B003`); the user reviewed and approved the completed video
- User authorized commit and push on September 21, 2026; feature implementation commit `8cb4b3c3a6527798f59dd96690f2784da898c06f` was fast-forwarded into `main`, checked, and pushed with the final report

## Data note and next task

The repository had no user/booking starter files, so `users.csv` and `bookings.csv` contain a small documented starter set; the original hotel/trip CSVs remain intact. The repository is private. Next: enable Chrome extension file-URL access, upload `report.md` to the Part 2 Canvas assignment, verify a submission receipt, and ensure the instructor can access the repository links. The Part 1 checkpoint remains in history.

## Visible browser demonstration — September 24, 2026

- One live button click returned HTTP 200. Chrome Network showed a GET to
  `/api/demo/zip-location` through port 5173; request/response headers and response JSON
  contained no API key. The displayed postcode 16802, locality State College, latitude
  40.803167822, and longitude -77.861384958 exactly matched the backend response.
- A temporary mocked connection failure before the controller's outbound HTTP call
  produced 502 and “Location provider request failed.” Loading cleared the old result
  and disabled the button. This failure consumed no provider quota. The controller was
  restored byte-for-byte and backend reload completion was confirmed.
- Hotel-name search “Harbor Lantern” returned T001 and T009, each $300.
- Not exercised live: missing configuration, unresolved ZIP, provider timeout/rate limit,
  other ZIPs, or booking mutations. No second live ZIP call was made after restoration.
  Repeated-click prevention has automated coverage; the browser check observed the disabled state.
- Trace: `frontend/src/App.vue` mounts `frontend/src/ZipLookup.vue`; its fetch goes through
  `frontend/vite.config.js` to `backend/app/main.py`, which calls `lookup_zip("16802")`
  in `backend/app/zip_lookup.py`. `backend/app/config.py` supplies the backend-only key.
  HTTPX calls Geoapify forward geocoding; the controller validates and reduces the response,
  FastAPI returns JSON, and Vue renders the returned fields.

## Current task — Assignment 2 Part 1 (September 29, 2026)

Implemented live ZIP hotel discovery at `/`, preserving previous sample UI at `/sample-stays`. Geoapify geocoding verifies exact U.S. ZIP before Places circle search (5 km, hotel category, limit 50). Leaflet list/map selection, honest fields, distinct request states, mobile layout and attribution complete. No shortlist or new persistence added.

Leaflet 1.9.4 installation approved and verified. Existing backend/.venv has needed HTTP/environment libraries; root .venv was unsuitable. Playwright uses installed Chrome. User separately approved FFmpeg v1011 helper download for local recording.

Verification: 60 backend tests, 24 frontend tests, lint/build pass. Live 02108 at 09:44 ET returned Boston center (42.357581412, -71.065946589) and 50 records (cap reached). Browser list→map and keyboard marker→list passed after correcting a real Enter-selection bug. Simulated empty/unresolved/502 states and 390px mobile layout passed. Original Harbor Lantern sample search passed. No browser runtime errors.

Deliverables: root report.md now covers Assignment 2 Part 1; prior report archived as docs/assignment-1-report.md. Research, pre-implementation SVG, screenshots, browser observations, 21.92-second WebM demo and verification record live under docs/assignment-2-part-1/. AI evidence appended to prompts/selected.md. No credential values were displayed or published; `.env` ignored/untracked.

Outstanding student actions: manual code/browser/video review; only then authorize commit/push. The assessed commit and instructor-accessible artifact URLs are deliberately pending in report.md. Repository access is not verified (prior report said private). Do not represent the existing base commit as the assessed implementation. No deployment, shortlist, or course submission performed.

### Student review follow-up

Student reports completing the review checklist and testing several ZIPs. Found missing return navigation from Sample stays. Added “← ZIP hotel search” in its header, linking to `/`; booking history retained. This is a new change for review; no commit/push authorized or performed.

Return-navigation verification: round-trip browser navigation, keyboard Enter, 390px header layout, lint and build all passed. Local frontend/backend restarted for review.
