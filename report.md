# Expedia Lite — Part 1

## Repository and commit

Private GitHub repository: [milestudor/expedia_project](https://github.com/milestudor/expedia_project)

Exact Part 1 implementation commit: [`8d5a952b0dcc9e282bf1c8380aaaa48d60ee106e`](https://github.com/milestudor/expedia_project/commit/8d5a952b0dcc9e282bf1c8380aaaa48d60ee106e) (`Implement Expedia Lite Part 1`).

## Implementation

The Vue frontend provides a labeled city input, Search button, request states, a results table, empty-input guidance, and a clear no-results message. It sends `GET /api/stays?city=...` requests to FastAPI through the Vite development proxy.

FastAPI validates the request and delegates the search to the Python backend. The backend reads `hotels.csv` and `trips.csv` using UTF-8 BOM-aware decoding, joins their rows through `hotel_id`, and matches city names case-insensitively after trimming surrounding whitespace. Each response row combines the trip and hotel fields and derives the number of nights and total stay price.

## Verification

Manual review was approved on September 10, 2026. The application was reviewed in a browser with the Vue frontend on port 5174 and FastAPI on port 8010 because ports 5173 and 8000 were already occupied by the Hello Agent reference project.

| Action | Expected result | Observed result |
| --- | --- | --- |
| Enter `Boston` and select **Search** | Four stays with trip IDs T001, T002, T009, and T010 | Passed. The page displayed “Hotel stays in Boston,” a “4 stays” count, and four rows with the expected IDs, joined hotels, dates, nights, nightly rates, and stay prices. |
| Enter `Miami` and select **Search** | No result rows and a clear no-results message | Passed. The results table was absent and the page displayed “No stays found” with guidance to check the spelling or try another city. |

![Boston search showing four matching hotel stays](https://github.com/milestudor/expedia_project/blob/main/docs/screenshots/boston-search.png?raw=true)

![Miami search showing the no-results message](https://github.com/milestudor/expedia_project/blob/main/docs/screenshots/miami-no-results.png?raw=true)

Automated verification also passed: 3 backend pytest checks, frontend ESLint with 0 errors and 54 formatting warnings, 3 frontend Vitest checks, a Vite production build, and an npm audit with 0 known vulnerabilities.

## Project context and next steps

Project documentation: [README](https://github.com/milestudor/expedia_project/blob/main/README.md), [AGENTS.md](https://github.com/milestudor/expedia_project/blob/main/AGENTS.md), [design note](https://github.com/milestudor/expedia_project/blob/main/docs/design.md), [selected prompts](https://github.com/milestudor/expedia_project/blob/main/prompts/selected.md), and [current handoff](https://github.com/milestudor/expedia_project/blob/main/handoffs/current.md).

Part 1 intentionally remains read-only and CSV-backed. It does not include users, bookings, authentication, payments, live inventory, or persistence. The next task is Part 2: introduce SQLite-backed persistence and the required booking workflows without re-importing starter data destructively on every startup. Because the repository is private, the instructor must be granted repository access for these links and screenshots to open.
