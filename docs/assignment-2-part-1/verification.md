# Part 1 verification — September 29, 2026

Runtime: existing `backend/.venv` (Python 3.13), Node 24.20.0, Vue 3.5.21, approved Leaflet 1.9.4, installed Google Chrome via bundled Playwright. FFmpeg v1011 was separately approved and downloaded for recording. No new backend dependency was needed.

## Automated checks

| Command / input | Expected | Observed |
| --- | --- | --- |
| `backend/.venv/bin/python -m pytest backend/tests -q` | Existing sample behavior and new provider contracts pass | 60 passed; one upstream anyio deprecation warning |
| `cd frontend && npm test` | Existing sample/ZIP checks and discovery state/selection checks pass | 24 passed across 3 files |
| `npm run lint` | No lint errors or warnings | Passed |
| `npm run build` | Production bundle generated | Passed |
| `npm ls leaflet` | Approved exact version | 1.9.4 |
| `git check-ignore .env` and `git ls-files .env` | Ignored and untracked | `.env` ignored; no tracked entry |
| Backend provider simulations | Empty is successful; 401/429/500/timeouts/malformed records are failures | Passed without calls to the live provider |
| Nonmatching country/postcode, invalid/leading-zero ZIPs | No fallback to a different location; ZIP remains text | Passed; Places not invoked for unresolved/invalid input |

## Browser checks

Recorded run completed at 09:44 ET on September 29, 2026. [Machine-readable observations](browser-verification.json), [screen-recorded demo](part-1-demo.webm).

| Input/action | Expected | Observed |
| --- | --- | --- |
| Initial load | No auto-search; clear ZIP input | Passed; initial guidance shown |
| `1234` | Invalid-input feedback without provider call | “Check your ZIP code” |
| Live `02108` | Preserve leading zero; exact U.S. postcode, provider hotels within requested 5 km circle | HTTP 200, Boston center `(42.357581412, -71.065946589)`, 50 returned records, result-limit warning |
| Loading / repeat submit | Clear old results and disable repeat submissions | Automated state test passed; live loading shown in recording |
| Live missing name | Honest fallback, not invented hotel title | First record displayed “Hotel name unavailable”; address from response |
| List versus markers | Same number of matching provider records | 50 list entries and 50 numbered markers |
| Select first list card | Matching marker highlights and popup opens | “1. Hotel name unavailable” popup, one selected marker |
| Focus marker 2, Enter | Same provider hotel selects in list | Beacon Hill Hotel and Bistro selected and scrolled into view |
| Simulated successful empty response | No-results message and resolved center map | Passed, “No nearby hotels returned” |
| Simulated unresolved ZIP | Separate not-found state | Passed, “ZIP code not found” |
| Simulated HTTP 502 | Failed-request state, not empty-success | Passed, “Search unavailable” |
| 390px viewport using replayed live data | Stacked layout, no horizontal overflow | Passed; [mobile screenshot](mobile.png) |
| Existing sample search “Harbor Lantern” | Existing CSV/SQLite behavior preserved | Matching table displayed at `/sample-stays` |
| Browser runtime errors | None | None |

Screenshots: [live results](live-results.png), [map selection](map-selection.png), [simulated empty](empty-simulated.png), [simulated failure](failure-simulated.png). Desktop and mobile screenshots were visually inspected. The recording is a silent 21.92-second browser capture at 1440 × 1100. Simulation and mobile-replay sections are labeled visibly; the main ZIP search is live. A brief original-sample regression check concludes the capture.

The live result count is an observation, not a test expectation. Assertions compare list and marker counts to that response. No quota exhaustion, retries, persistence, shortlist or booking functionality was added for this part.

## Corrections and limits

- Root `.venv` lacked dotenv; used the already configured `backend/.venv` instead.
- Sandboxed npm request could not resolve the registry; approved network installation succeeded.
- Bundled browser/FFmpeg were unavailable; used existing Chrome, then downloaded only the separately approved recording helper.
- Real browser testing found Enter opened a Leaflet popup without selecting the list item. Added explicit Enter/Space selection and in-place marker highlighting; rerun passed. Frontend tests/lint/build passed after this fix.
- Live search verified one ZIP, `02108`. Invalid/unresolved/empty/failure edge cases use simulations; they are not claims about those real locations or current service availability. The upstream 429 case is mocked at the provider boundary, not induced live.
- Fifty-result cap, no pagination, variable provider coverage, and normal network/tile-service dependency remain. Tile-failure UI is implemented but not explicitly forced in this recorded run. No user-position lookup is used.
- Manual student review, assessed commit, and instructor-accessible publication of code/artifacts remain. No commit or push has been made, in accordance with AGENTS.md.

## Student review follow-up — return navigation

Added a visible “← ZIP hotel search” link from Sample stays after the student identified its absence. Browser verification passed for discovery → Sample stays → keyboard Enter on return link → initial discovery form. Header fits a 390px viewport. Lint and production build passed. Existing recording predates this small navigation change. Local servers initially were stopped; restarted them for the browser check.
