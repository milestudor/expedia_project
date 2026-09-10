# Expedia Lite Part 1 verification report

Verified on 2026-09-10 in the in-app browser at `http://127.0.0.1:5174`. Ports 5173 and 8000 were already occupied by the reference calculator, so Expedia Lite was run on 5174 with its API on 8010 without stopping unrelated processes.

| Browser check | Expected | Observed |
| --- | --- | --- |
| Successful search: `Boston` | 4 stays: T001, T002, T009, T010 | PASS — “Hotel stays in Boston,” “4 stays,” and four rows for T001, T002, T009, and T010; joined hotel names, dates, nights, nightly rates, and stay prices were visible. |
| No-results search: `Miami` | Clear no-results message and no table rows | PASS — “No stays found” and “We found no hotel stays in ‘Miami.’ Check the spelling or try another city.” were visible; the results table was absent. |

## Automated evidence

- Backend: 3 pytest checks passed.
- Frontend lint: passed with 0 errors and 54 formatting warnings in `App.vue`.
- Frontend: 3 Vitest checks passed.
- Production build: Vite build completed successfully.
- Dependency audit: 0 known npm vulnerabilities after updating Vite/Vitest to patched releases.
