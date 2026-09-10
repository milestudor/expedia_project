# Expedia Lite Start-Up Prompts

These prompts are reusable project checkpoints. Run them in order when preparing or rechecking the Expedia Lite development environment. Each prompt must preserve existing project work unless it explicitly authorizes a change.

## Create the Project Boundary

Create the starting structure as follows:

- Add `backend/` for FastAPI.
- Add `frontend/` for Vue.
- Add `README.md` for the goal and setup.
- Add `AGENTS.md` for durable project rules.

Work only inside the current `expedia_project` project. Do not install dependencies or write application code yet. If the structure already exists, do not replace or remove it. Report the files and folders created or already present.

## Check and Prepare Python

Read `AGENTS.md` and `README.md`. Work only inside `expedia_project`.

Run only the Python checkpoint of the environment setup loop.

### CHECK

- Detect the operating system.
- Report every available Python executable, version, and path.
- Treat Python 3.10 or higher as compatible.

### TAKE ACTION

- If a compatible Python already exists, do not reinstall it.
- If Python is missing or incompatible, identify the safest supported installation method from an official source.
- Explain the exact download or system change, whether it needs administrator access, and then stop for my permission.
- After I approve, perform only the approved Python installation when the computer permits it.
- Never use `sudo` automatically and never bypass a managed-computer policy.

### VERIFY

- Report the installed Python version and executable path.
- Confirm whether the Python checkpoint passed.

Do not create project environments, install packages, or write application code yet.

## Check the Project-Owned Backend Environment

Read `AGENTS.md` and `README.md`. Work only inside `expedia_project`.

Do not write any backend function, API route, test, or frontend application code.

Prepare the backend development environment:

- Create `backend/.venv` using the compatible Python that just passed verification.
- Create `backend/requirements.txt` containing `fastapi[standard]` and `pytest` if it does not already declare them.
- Install only those declared dependencies into `backend/.venv`.
- Verify that the interpreter used for the checks belongs to `backend/.venv`.
- Verify that `fastapi` and `pytest` import successfully.

Do not install Python packages globally. Ask before any machine-level change. Report every file or directory created, every command run, and the evidence from each check.

## Check and Prepare Node.js

Read `AGENTS.md` and `README.md`. Work only inside `expedia_project`.

Run only the Node.js checkpoint of the environment setup loop.

### CHECK

- Read the current official Vue Quick Start requirement for supported Node.js versions.
- Report the installed Node.js and npm versions and executable paths.
- Compare the installed Node.js version with the current Vue requirement.

### TAKE ACTION

- If the installed version is compatible, do not reinstall it.
- If Node.js is missing or incompatible, identify a supported LTS installation from an official source.
- Explain the exact download or system change, whether it needs administrator access, and then stop for my permission.
- After I approve, perform only the approved Node.js installation when the computer permits it.
- Never use `sudo` automatically and never bypass a managed-computer policy.

### VERIFY

- Report the Node.js and npm versions and executable paths.
- Confirm whether the Node.js checkpoint passed.

Do not initialize Vue or write application code yet.

## Initialize the Project-Owned Vue Environment

Read `AGENTS.md` and `README.md`. Work only inside `expedia_project`.

Initialize a minimal JavaScript Vue project inside the existing empty `frontend/` folder.

- Use the current official `create-vue` workflow.
- Do not create a second nested `frontend` folder.
- Do not install Vue or Vue CLI globally.
- Omit Router, Pinia, TypeScript, JSX, unit-test, and end-to-end-test options.
- Include ESLint for code-quality checks.
- Install the declared frontend dependencies.
- Run the frontend lint and production-build checks.

If `frontend/` is no longer empty and is already a valid Vue project, do not reinitialize or overwrite it. Verify the existing project instead. The generated Vue starter screen is allowed, but do not build an application interface yet. Do not change backend files. Report every file or directory created, every command run, and the evidence from each check.

## Verify the Complete Project Environment

Verify the Expedia Lite environment without changing source files or dependency declarations.

Confirm:

- The exact Python interpreter path used for backend checks.
- That the interpreter belongs to `backend/.venv`.
- That `fastapi` and `pytest` import successfully.
- The Node.js and npm versions and paths.
- That `frontend/package.json` declares Vue.
- That the frontend lint and production build pass.
- Every project file or directory created during setup.
- Whether any backend function, API route, test, or application interface existed before these environment checks or was created by them.

Report any check that did not pass. Do not hide partial readiness.

## Install SQLite DB

### CHECK

Identify the project's Python interpreter. Use it to check whether `sqlite3` imports, and report its executable path and SQLite library version. Do not change files or the environment during this check.

### TAKE ACTION

If the import succeeds, skip installation. If it fails, identify the missing capability and explain the smallest appropriate correction, exact command, and target environment. Stop for my approval before installing software or changing dependencies. Do not assume `pip install sqlite3` is the solution. Do not use `sudo` automatically.

### VERIFY

Use the selected project interpreter to repeat the import/version check. Report the evidence and any remaining blocker. Do not build the persistence layer or change application behavior yet.
