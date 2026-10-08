# Local hotel storage and local-first lookup

Implemented October 1, 2026 on `assignment2_part2_in_class`. Student manual browser/database review is pending. No commit or push performed.

## Storage and API

Database: `/Users/milestudor/Documents/ChatGPT/expedia_project/backend/data/expedia_lite.db`.

An additive startup migration now also creates `saved_zip_contexts` (searched postcode, country, center coordinates and optional locality) and `saved_hotel_zips` (unique provider hotel ID/postcode relationship). These preserve search context separately from the hotel's address postcode. One hotel can belong to multiple searched ZIPs. Existing ZIP context is retained on repeat saves.

- `GET /api/local-hotels?postcode=02108`: returns saved hotels, stored center and each hotel's dated `demo_nights`. An empty successful result permits provider fallback; a storage error returns 503.
- `POST /api/local-hotels`: accepts `{hotel, center}` using the existing API hotel fields (`place_id`, nullable `name`/`address`, latitude/longitude) and result center. Copies provider ID verbatim to `saved_hotels.hotel_id`. Saves hotel, searched ZIP association and five nightly rows in one transaction.
- `POST /api/local-hotels/status`: accepts `{place_ids: [...]}` and returns `{saved_ids: [...]}` from the database, including hotels saved under another ZIP.
- `DELETE /api/local-hotels?hotel_id=...`: atomically removes the saved hotel, all its ZIP associations and demo nights. Unused contexts for its ZIPs are removed; contexts shared by other hotels remain. A repeated deletion succeeds harmlessly.

Dates are October 10–14, 2026 inclusive. Inserts omit rate/room columns to use defaults of 10000 cents and 20 rooms. Targeted conflict handling prevents duplicate hotels, associations and nights without overwriting existing rates or availability. Failed mutations roll back. Backend connections enable foreign keys. Invalid request data returns 422; SQLite failures return a sanitized 503.

The Part 1 `/api/hotels` contract and provider search are unchanged. No automatic API hotel saving occurs. No Assignment 1 writes are introduced.

## Browser behavior

Search validates the ZIP, requests local matches, and uses them when available. Only successful empty local lookup calls Part 1 search. API results then get a provider-ID saved-status check. Fresh searches after reload read the database again. A local request failure never triggers provider fallback.

Results are labeled “Saved locally” or “API results.” Local results are explicitly a saved subset, not a complete area inventory. Dates, stored cents formatted as dollars, and rooms available are shown as simulated classroom data. They are not provider prices or inventory.

Add and Remove are sibling buttons beside the existing accessible selection button, avoiding nested buttons. Add is disabled for saved/pending hotels; Remove appears only for saved hotels. Search is disabled during a mutation to keep the result context stable. Saving uses the result's center even if the input was edited. Feedback and saved state update after success; failed removal preserves the card. Removing a local result rebuilds the map, clears selection if necessary, and does not trigger provider discovery automatically. After removing the final local result, the page invites another search.

## Verification

- 95 backend tests passed. Mutation tests use temporary databases, covering repeat saves, five exact dates/defaults, edited values surviving repeat saves/restart, multiple ZIP associations, provider-ID status, input validation, rollback on failed save/delete, unrelated record preservation, and storage-read failure.
- 30 frontend tests passed, including local-first ordering, no fallback after local failure, saved state on fresh mount, stored dated values, pending/success/failure states, result context and separate accessible buttons. Existing map/card selection checks remain passing.
- Frontend lint and production build passed; `git diff --check` passed. Existing Starlette/AnyIO deprecation warning remains.
- Actual database's original table definitions and all rows still match the pre-migration snapshot. All four local-storage tables are empty; no mutation tests touched the real database.
- Checked process commands and working directories before stopping only this project's backend reloader and Vite process. Restarted backend at http://127.0.0.1:8000 and frontend at http://127.0.0.1:5173. Health, frontend HTTP 200, and successful empty local lookup through Vite's proxy verified.
- No new live provider search or manual browser/database mutation verification was claimed. Stop here for student review.

## Manual review

Search a ZIP, save one API hotel, inspect its ID/ZIP association and five dated rows. Repeat the search and refresh to see the saved subset without a provider lookup. Edit one night's rate/rooms in the database viewer, commit those changes, and repeat the search to compare the same hotel/date. Remove the saved hotel and check that its related rows disappear while Assignment 1 and unrelated saved records remain. Keep the before/after evidence before removing your example.

## Agent-assisted real database edit — October 1, 2026

At the user's request, edited the saved Nittany Lion Inn for searched ZIP 16802 on stay date 2026-10-10. Committed a direct SQLite transaction changing 10000 cents / 20 rooms to 500 cents / 10 rooms. Repeated the ZIP search in the browser and observed `2026-10-10 · $5.00/night · 10 rooms available` under Saved locally. Other nights remained $100.00 / 20 rooms; all unrelated records matched the before snapshot. This was an agent-performed database edit and browser check, not a student DB Browser UI demonstration. Left the edited values and hotel in place for review.

Evidence: [database before/after](rate-edit-evidence.json), [browser before](rate-before.png), [browser after](rate-after.png).
