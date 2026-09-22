# Expedia Lite — Part 2

## Repository and commit

Private GitHub repository: [milestudor/expedia_project](https://github.com/milestudor/expedia_project)

Exact Part 1 implementation commit: [`8d5a952b0dcc9e282bf1c8380aaaa48d60ee106e`](https://github.com/milestudor/expedia_project/commit/8d5a952b0dcc9e282bf1c8380aaaa48d60ee106e). Exact Part 2 implementation commit: [`8cb4b3c3a6527798f59dd96690f2784da898c06f`](https://github.com/milestudor/expedia_project/commit/8cb4b3c3a6527798f59dd96690f2784da898c06f), developed on `codex/part-2-sqlite-crud` and merged into `main`.

## Implementation

Part 2 replaces runtime CSV reads with durable SQLite access. On first startup, Python creates the schema and seeds hotels/trips plus starter users/bookings while preserving IDs. Later starts leave nonempty tables unchanged. A stored sequence assigns unique IDs to new bookings.

The Vue frontend searches hotel names or cities, selects a traveler, creates a simulated booking, reads booking history, cancels a booking by changing its status while retaining it, and permanently deletes a test booking. Every action uses FastAPI, which validates requests and performs all SQLite reads and writes.

## Verification

Automated verification passed again on September 21, 2026: 6 backend tests, including full CRUD and database-restart persistence; 4 frontend tests; ESLint with no warnings; and the Vite production build.

| Frontend action | Expected result | Observed result |
| --- | --- | --- |
| Search for `Harbor Lantern` | Matching Harbor Lantern stays appear from SQLite | Passed: two Harbor Lantern stays appeared with dates and prices |
| Search for `No Such Hotel` | A clear no-results message appears | Passed: “No stays found” appeared with corrective guidance |
| Book an available stay | A new unique booking appears in history | Passed: `B004` appeared as confirmed for Alex Morgan |
| Refresh the browser | The new booking remains and starter rows are not duplicated | Passed: four total bookings appeared, including `B004` once |
| Cancel the new booking | Its status becomes cancelled and the record remains | Passed: `B004` remained in history with cancelled status |
| Restart both servers and refresh | The cancelled status remains | Passed: four total bookings remained and `B004` was still cancelled |
| Delete the test booking | The record disappears from history | Passed: `B004` disappeared and history returned to three records |
| Restart both servers and refresh | The deleted record stays absent | Passed: `B004` remained absent and starter records were not reloaded |

All required browser CRUD and persistence behaviors passed. The following screenshots were captured from the frontend on September 21, 2026. The new example booking in these captures is `B005`; the earlier completed restart/delete verification used `B004`.

![Hotel-name search returning two stays](https://github.com/milestudor/expedia_project/blob/main/docs/screenshots/part-2-search-results.png?raw=true)

![Clear no-results message](https://github.com/milestudor/expedia_project/blob/main/docs/screenshots/part-2-no-results.png?raw=true)

![New confirmed booking B005 in history](https://github.com/milestudor/expedia_project/blob/main/docs/screenshots/part-2-created-booking.png?raw=true)

![Cancelled booking B005 retained in history](https://github.com/milestudor/expedia_project/blob/main/docs/screenshots/part-2-cancelled-booking.png?raw=true)

Demo video: the silent [98-second Part 2 demo](https://github.com/milestudor/expedia_project/blob/main/docs/expedia-lite-part-2-demo.mp4) shows search, no-results, create/read, refresh, cancellation, and deletion through the frontend. The final deletion segment creates and removes disposable booking `B007`; after refresh, history again shows only the three starter bookings. The recording is assembled from two browser captures, and the screenshot evidence above shows the earlier `B005` example.

## Project context and next steps

Project documentation: [README](https://github.com/milestudor/expedia_project/blob/main/README.md), [AGENTS.md](https://github.com/milestudor/expedia_project/blob/main/AGENTS.md), [design note](https://github.com/milestudor/expedia_project/blob/main/docs/design.md), [selected prompts](https://github.com/milestudor/expedia_project/blob/main/prompts/selected.md), and [current handoff](https://github.com/milestudor/expedia_project/blob/main/handoffs/current.md).

Remaining limitations are intentionally classroom-scale: no authentication, real payment, live room inventory, or concurrent reservation control. The user reviewed the completed demo and authorized commit and push on September 21, 2026. Submit this `report.md` to the Part 2 Canvas assignment. Because the repository is private, the instructor must have repository access for links to work.
