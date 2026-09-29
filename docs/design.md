# Part 2 design note

Backend configuration is isolated in `backend/app/config.py`. It loads the root `.env`
using a path derived from the helper file, preserving process environment precedence.
`GET /api/health` retains its existing status and adds only the Geoapify key configuration
status; missing or blank values are unconfigured. No Geoapify request is made.

Vue owns all user interactions: hotel-name or city search, traveler selection, simulated booking, booking history, cancellation, and test deletion. It never accesses storage directly. Every action calls FastAPI through the local `/api` proxy and refreshes history from server state.

FastAPI defines the HTTP boundary and validates request models. `GET /api/stays` searches hotel names and cities; `GET /api/users` supplies the traveler selector; `GET`, `POST`, `PATCH`, and `DELETE /api/bookings` provide CRUD. Cancellation is a status update, so the booking remains visible.

Python's built-in SQLite driver owns persistence. On first startup, tables are created and empty tables are seeded from `hotels.csv`, `trips.csv`, `users.csv`, and `bookings.csv`. Existing IDs are retained. Later startup is non-destructive, and a stored sequence assigns never-reused booking IDs. Hotel/trip records join through `hotel_id`; text search trims input and ignores case.

No authentication, payment processing, live inventory, or concurrent-seat reservation is simulated. Delete is intentionally exposed for assignment test records, while the interface warns that it is permanent.

## ZIP lookup controller contract

`backend/app/zip_lookup.py::lookup_zip(postcode)` is separate from routes, Vue, database
logic, and hotel/price models. Input must be an exact five-digit ASCII string (otherwise
`ValueError`); any valid five-digit U.S. ZIP is accepted.

Using existing HTTPX, it sends a backend-only GET to Geoapify's forward geocoding
endpoint `/v1/geocode/search` with `postcode`, `type=postcode`,
`filter=countrycode:us`, `format=json`, and the key from the configuration helper.
HTTPX has a 10-second timeout for network operations, with no application retries.
Request parameters follow the [Geoapify geocoding documentation](https://apidocs.geoapify.com/docs/geocoding/).

- Success: a dictionary containing `postcode`, `country_code` (`us`), `latitude`,
  `longitude`, and optional `locality` (city, then town, then village). No price is required.
- Acceptance requires exact postcode and U.S. country code plus finite numeric coordinates
  within latitude −90…90 and longitude −180…180. Booleans and numeric strings are rejected.
  Candidates are checked in provider order; mismatches and invalid coordinates are skipped.
- Unresolved: `None` when no candidate qualifies, including an empty results list.
- Failure: `ZipLookupError` for missing configuration, transport/timeouts, non-success
  HTTP status, invalid JSON, or malformed response structure. Messages and displayed
  tracebacks omit underlying exception details. HTTPX request logs for Geoapify are
  suppressed to avoid logging credential-bearing URLs. No raw response is returned.

Mocked tests cover request parameters, success, missing locality, mismatches, invalid
coordinates, no results, HTTP errors, transport/timeouts, malformed responses, missing
configuration, and credential-safe error/log behavior. These tests make no live provider calls.

## Demo route

`GET /api/demo/zip-location?postcode=02108` trims and validates the supplied ZIP string
before calling `lookup_zip(postcode)`. Missing or invalid input returns 422 with
“Enter a five-digit U.S. ZIP code.” Leading zeros are preserved.
It returns the location directly on 200, maps `None` to 404,
`ZipConfigurationError` (a `ZipLookupError` subclass) to 503, and other
`ZipLookupError` failures to 502. Error messages are fixed and never include exception text.
Provider logic remains in the controller; existing routes are preserved.
Mocked route tests cover all four outcomes. One live request on September 24, 2026
returned U.S. ZIP 16802, State College, latitude 40.803167822, longitude -77.861384958.

## ZIP demonstration panel

`frontend/src/ZipLookup.vue` is mounted below search results in the existing app. It
requests `/api/demo/zip-location?postcode=<entered ZIP>` when the ZIP form is submitted, using the
existing Vite backend proxy. Its independent loading, result, and error state leaves
hotel-name search and bookings unchanged. Loading clears stale output and disables
the button; success labels postcode, optional locality, latitude, and longitude.
Backend errors are displayed as text, with a safe fallback for connection failures.
The ZIP text field accepts five ASCII digits, trims surrounding whitespace, and preserves
leading zeros. Both Vue and FastAPI reject invalid input before contacting the provider.
No frontend credentials, direct provider requests, or new dependencies were added.

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

The earlier fixed-ZIP browser demonstration below is historical evidence; the form now accepts user-entered ZIPs.

## Assignment 2 Part 1 — live discovery (September 29, 2026)

The default page is now live ZIP-based discovery. The existing application is preserved at `/sample-stays`, including the earlier standalone ZIP demo. This separates provider hotel locations from priced sample stays. No shortlist or new SQLite persistence was added.

`GET /api/hotels?postcode=02108` validates five ASCII digits after trimming whitespace, resolves an exact U.S. postcode, then queries Geoapify Places with `accommodation.hotel`, a 5,000-meter circle around the returned point, proximity bias, and limit 50. A nonmatching geocoder result cannot initiate Places. Error contracts: 422 invalid, 404 unresolved, 503 key absent, 502 provider/response failure. Successful empty Places results retain the returned center map and display a distinct no-results state.

Response shape: `center` (postcode, country code, latitude, longitude, optional locality), `hotels` (provider `place_id`, nullable `name`/`address`, latitude/longitude), `radius_meters`, `limit`, `limit_reached`. No rate, rating, room availability or booking fields. Duplicate place IDs collapse to one list/marker record. A malformed identifier or coordinate fails visibly rather than silently becoming an empty success; missing text receives an honest label. Provider popup text uses DOM textContent, never HTML interpolation.

Vue owns one selected provider ID shared by list buttons and keyboard-accessible Leaflet markers. Numbered pins correspond to numbered list entries. Selecting a marker scrolls its card into view; selecting a card highlights and opens its marker. Each new search destroys the old map and clears stale results. Controls disable during loading. No geolocation permission, pan-triggered requests, search-as-you-type, automatic retries, or pagination.

Map tiles use public OSM HTTPS imagery, visible attribution, and normal browser caching. Tile failures receive their own warning while hotel data remains visible. Geoapify attribution is visible in the footer. The root `.env` is ignored and untracked; the backend key is neither returned by API responses nor copied into frontend configuration. The existing httpx log filter protects credential-bearing provider URLs.

Research, early mockup and verification: [Part 1 research](assignment-2-part-1/research.md), [early mockup](assignment-2-part-1/mockup.svg), [verification](assignment-2-part-1/verification.md). The final UI uses a stacked search hero and separates legacy sample navigation, while retaining the mockup's split list/map and responsive stack.

### Review correction: return navigation

Student review identified that Sample stays had no visible route back to live discovery. Added a keyboard-accessible “← ZIP hotel search” header link to `/`, keeping the booking-history anchor and wrapping navigation on narrow screens. Navigation returns to the initial ZIP search form.
