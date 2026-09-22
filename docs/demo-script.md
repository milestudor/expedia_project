# Expedia Lite Part 2 demo script

Target length: 2 minutes 15 seconds. Before recording, start both servers, open `http://127.0.0.1:5173`, and confirm the history shows the three starter bookings.

## 0:00–0:15 — Introduce the application

“This is Expedia Lite Part 2. The Vue frontend sends every search and booking action through FastAPI, and the backend now stores all application data in SQLite.”

Show the search area and scroll briefly to the three seeded history records.

## 0:15–0:35 — Search and no-results behavior

Enter `Harbor Lantern` and select **Search stays**.

“Hotel-name search returns two available stays joined to their hotel through the preserved IDs. The table shows dates, nights, rates, and total prices.”

Enter `No Such Hotel` and search.

“A search without matches produces a clear no-results message.”

## 0:35–1:05 — Create and read

Search for `Harbor Lantern` again. Leave Alex Morgan selected and select **Book** on the first row.

“This creates a new booking beyond the seeded examples. The backend assigns the next unique ID, and the new confirmed booking appears immediately in history.”

Point out booking `B004`, then refresh the browser.

“The booking remains after refresh because history is read from SQLite.”

## 1:05–1:30 — Update without deleting

Select **Cancel booking** on `B004`.

“Cancellation is an update, not a deletion. The status changes to cancelled while the booking remains in history.”

Refresh once more and point out that `B004` is still cancelled.

## 1:30–1:55 — Delete a test record

Select **Delete test booking** on `B004`.

“Delete permanently removes this test booking. The history returns to the original three records.”

Refresh and show that `B004` remains absent.

## 1:55–2:15 — Restart persistence and close

Stop and restart both servers, then refresh the browser. If recording the terminal would slow the demo, perform the restart just before recording and state that it was completed.

“After restarting both applications, the database still contains exactly the three starter bookings: the deleted record was not restored and the starter data was not duplicated. This demonstrates create, read, update, delete, and persistent SQLite storage entirely through the frontend.”

## Capture checklist

- Keep the recording under three minutes.
- Show the browser URL at least once.
- Keep `B004` visible when demonstrating create, refresh, and cancel.
- End with three total bookings after deletion and restart.
- Upload the video somewhere the instructor can access, then replace the video placeholder in `report.md` with its link.
