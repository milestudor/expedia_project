# install dotenv

CHECK
Read the backend setup instructions, dependency manifest, and any
lockfile. Identify the project interpreter. Check whether dotenv
(python-dotenv) and an HTTP client are already available there.
Report their availability and whether they are declared directly.
Do not read or print the API key.

TAKE ACTION
Reuse available capabilities. If a package installation or dependency
declaration is needed, explain why, the target environment, exact
command or manifest edit, and affected files. Ask for my approval and
wait before that change. Do not install or update anything otherwise.

VERIFY
Use a small version or import check in the intended environment.
Report what is ready for the next step, then stop.

# implement a health command in the backend for config check
Add the smallest backend configuration helper that loads the project-root
.env using an explicit path derived from the helper file, then reads
GEOAPIFY_API_KEY. Use the capability approved in the previous step.
Keep the helper separate from the Vue frontend and database logic.
Extend GET /api/health in the backend, or add it if it is not available,
to show "key is configured" or "key is not configured" along with the
other health checks. Preserve the existing health information and show
only the configuration status, never the key value.
Treat an absent, empty, or whitespace-only value as not configured.

Update README.md with the file location and when the backend must be
restarted after editing it. Do not call Geoapify yet. Stop.

# check
start the backend

When running, open the browser, enter the backend url http://127.0.0.1:8000,
followed by the /api/health/command. In summary, it would be http://127.0.0.1:8000/api/health.
The Browser should show the status

# one controller function in the backend to consume the API
Add one small backend controller function for a ZIP lookup. The only
live demonstration input for now is the string "16802".

Use Geoapify forward geocoding with postcode, type=postcode,
filter=countrycode:us, and format=json. Read the API key through the
configuration helper and supply it only in the backend request.
Use a finite timeout and the inspected HTTP capability.

Accept a result only if it identifies the requested U.S. postcode
and has valid coordinates. Return a small location response containing
postcode, country code, latitude, longitude, and locality if present.
Keep it separate from the sample Hotel model, which requires a price.

Distinguish an unresolved ZIP from a failed provider request. Never
print or return the key, full provider request URL, or raw exception
text containing credentials. Document the controller contract and
check success, mismatched-location, and failure behavior with mocked
responses. Do not edit routes or Vue yet. Stop.

# Add a route function (/api/demo/zip-location) in FastAPI to consume from frontend
Add GET /api/demo/zip-location as a thin FastAPI route. It calls the
controller with "16802" and returns its small location response.
Map missing configuration, unresolved ZIP, and provider failure to
clear error responses without exposing credentials. Preserve existing
routes and keep the provider logic in the controller.

Check the route with a mocked controller. Then use the documented
startup procedure to run this project, preserving unrelated processes.
If its backend is already running, identify the process and whether a
restart is needed before changing it. Make one live request to this
local route. Show only the sanitized location response or safe error.
Report live success only if Geoapify actually returned usable data. Stop.

# Add a button and a result in the frontend to check complete API
Add a small "ZIP lookup demonstration" panel to the existing Vue app.
Use one button labeled "Look up ZIP 16802". On a click, request
/api/demo/zip-location through the existing backend proxy convention.
Make no provider request directly from Vue.

Display loading feedback, then the returned postcode, available
locality, and labeled latitude and longitude, or the backend error.
Clear an earlier result when a new request begins, and prevent repeated
clicks while it is loading. Keep the existing hotel-name search working.

Do not add a key to frontend code or a VITE_ variable. Do not add hotels,
a ZIP input form, a map, or new dependencies. Run the relevant frontend
checks, then stop so I can inspect the panel in the browser.
