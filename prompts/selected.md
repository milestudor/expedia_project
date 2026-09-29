# Selected prompts

- Add a standalone backend ZIP lookup controller using Geoapify forward geocoding,
  existing HTTPX, and the configuration helper. Validate exact U.S. postcode and coordinates,
  distinguish unresolved results from safe provider failures, and verify with mocks.
  Keep routes and Vue unchanged; only `"16802"` is approved as a live demonstration input.

- Load the project-root `.env` in a separate backend helper using existing python-dotenv;
  extend health with only the key configuration status, preserve existing health information,
  treat absent/empty/whitespace values as unconfigured, and document backend restart requirements.
  Do not expose the key or call Geoapify.

- Implement Part 2 with SQLite-backed reads and writes after one-time seeding; preserve existing IDs and saved changes across restarts.
- Keep Vue in `frontend/` and FastAPI/Python in `backend/`; route every CRUD action through the frontend and API.
- Search by hotel name, simulate booking creation, read history, cancel by retaining and updating the record, and delete a test booking.
- Use a persistent sequence for unique new booking IDs and test CRUD plus restart persistence in a temporary database.
- Follow CHECK → TAKE ACTION → VERIFY for dependencies, update project context, and do not commit, merge, or push before manual review.

- Add the thin fixed-ZIP demo route, map configuration/unresolved/provider errors safely,
  test with a mocked controller, preserve unrelated processes, and make exactly one
  live request to the local route after checking project startup.

- Add a small ZIP lookup demonstration panel with one fixed-ZIP button, backend-proxy
  requests, loading/duplicate-click protection, cleared stale results, labeled location
  fields, and backend errors. Preserve hotel search; run frontend checks and stop for review.

- Verify the visible browser ZIP round trip against Chrome Network, check a quota-free
  mocked provider failure and hotel-name search, restore normal behavior, and document
  expected versus observed results and the responsible files without adding features.

- Replace the fixed ZIP demonstration with a text field that searches the entered U.S.
  ZIP, preserving leading zeros, validating input, and retaining backend-only credentials.

## Assignment 2 Part 1 — September 29, 2026

AI tool/model: OpenAI Codex desktop, GPT-6 (agent session). Used for assignment interpretation, repository inspection, primary-source research through web tools, the pre-implementation SVG mockup, Vue/FastAPI changes, tests, browser automation, documentation and report drafting. Playwright/Chrome are verification tools, not additional AI models. No subagents were used. The exact deployment build identifier is not exposed in this session.

Selected excerpts and linked effects:

- User: “please view the following instructions and only complete what is asked for part 1 please.” → [live service](../backend/app/hotel_search.py), [discovery view](../frontend/src/HotelDiscovery.vue), [map](../frontend/src/HotelMap.vue); existing sample app preserved; no shortlist.
- Agent asked: “May I install Leaflet 1.9.4 in frontend/ for the required interactive map?” User: “Approve Leaflet 1.9.4 installation.” → CHECK found it absent; TAKE ACTION installed the exact approved version; VERIFY `npm ls leaflet`, tests, lint and build passed.
- Design decision: exact requested postcode and U.S. country must match before Places; public records are not room inventory → [research](../docs/assignment-2-part-1/research.md), [early mockup](../docs/assignment-2-part-1/mockup.svg), [provider tests](../backend/tests/test_hotel_search.py).
- Failed/revised approach: first environment check used root `.venv`, which lacked dotenv. The project's documented `backend/.venv` already had the required libraries; switched to that runtime without installing another Python dependency.
- Failed/revised approach: normal sandbox install could not reach npm. The approved installation succeeded with network access; no package/version substitution.
- Failed/revised approach: the bundled Playwright browser and recording helper were unavailable. Browser verification switched to the existing Chrome installation; recording helper approval was requested separately.
- Verification decision: use one real ZIP response for live evidence, and label simulated empty/unresolved/failure states; automated tests simulate provider rate limits, never deliberately exhaust quota. See [verification](../docs/assignment-2-part-1/verification.md).

All generated work remains subject to student review. No commit, push, repository visibility change, deployment, or course submission was performed by the agent in this turn.
- Browser-discovered correction: Leaflet Enter opened a popup without firing the marker click selection handler. Added explicit Enter/Space selection handling and preserved marker DOM while highlighting; reran the browser check. This was a real implementation failure, not a simulated provider failure.
- User approved: “Approve video helper download.” Downloaded Playwright FFmpeg v1011 solely for verification, leaving app manifests unchanged; existing Chrome used for browser capture.

- Student review: “once i click sample stays, should i be able to go back to the new search” → added a visible return link in [LegacyApp.vue](../frontend/src/LegacyApp.vue), with keyboard focus styling and wrapping navigation. No dependencies changed.

## Publication approval

User: “okay it looks really good. Unless there's anything extra you want to add to make this look more fancy, please commit and push”. No extra visual features added. Manual review and return-navigation correction accepted; approved implementation committed, repository verified public, and report finalized with public links. Prior “no commit” statements describe earlier checkpoints.
