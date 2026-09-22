# Selected prompts

- Implement Part 2 with SQLite-backed reads and writes after one-time seeding; preserve existing IDs and saved changes across restarts.
- Keep Vue in `frontend/` and FastAPI/Python in `backend/`; route every CRUD action through the frontend and API.
- Search by hotel name, simulate booking creation, read history, cancel by retaining and updating the record, and delete a test booking.
- Use a persistent sequence for unique new booking IDs and test CRUD plus restart persistence in a temporary database.
- Follow CHECK → TAKE ACTION → VERIFY for dependencies, update project context, and do not commit, merge, or push before manual review.
