# Research and early design — September 29, 2026

Prepared before the new discovery interface. [Early mockup](mockup.svg).

| Source consulted | Useful pattern / limitation | Adopted decision |
| --- | --- | --- |
| [Expedia Hotels](https://www.expedia.com/Hotels) | Prominent destination search and discovery suggestions; dates and booking offers belong to a different inventory model. | Put ZIP search first; omit rates, availability, and booking claims from live discovery. |
| [Google Travel hotels](https://www.google.com/travel/hotels) | Research reader was redirected to an unsupported-browser page, so its interactions could not be evaluated here. | Do not claim to have tested its list/map synchronization; use Leaflet's documented interactions. |
| [Geoapify Geocoding](https://apidocs.geoapify.com/docs/geocoding/) | Postcode search and U.S. country filter; search responses still require verification. | Keep ZIP as text, require matching postcode and country plus valid coordinates before Places. |
| [Geoapify Places](https://apidocs.geoapify.com/docs/places/) | Hotel category, circle filter in longitude/latitude/meters order, proximity bias and limit. Coverage is variable. | Search accommodation.hotel within 5,000 meters; request at most 50 records and label the limit. |
| [Leaflet quick start](https://leafletjs.com/examples/quick-start/) and [reference](https://leafletjs.com/reference) | Markers support keyboard focus and Enter; popup strings are HTML and map containers need explicit height. | Numbered keyboard markers, one selected provider ID, safe DOM text in popups, fixed map height. |
| [OSM tile policy](https://operations.osmfoundation.org/policies/tiles/) | Attribution and normal browser caching required; no bulk download or guaranteed service. | Standard HTTPS tiles for modest classroom use, visible attribution, no prefetch, explicit tile-failure feedback. No tile key. |
| [Geoapify pricing](https://www.geoapify.com/pricing/) and [terms](https://www.geoapify.com/terms-and-conditions/) | Usage is metered and plans/credits vary; free use requires attribution. | Explicit-submit searches only, no automatic retries or search-as-you-type; Geoapify attribution. Check account limits before demonstrations. |

One submitted search makes one geocoding request, then one Places request only if the requested U.S. ZIP is resolved. No pagination or exhaustive inventory claim. Backend credentials are never sent to Vue. The 5 km circle describes the returned postcode point, not ZIP boundaries or the user's position.

Implementation revisions will be recorded in the verification record. Existing sample-data pages remain available separately; no new shortlist, saving, or persistence work is included.

Follow-up research: [Booking.com](https://www.booking.com/) returned a JavaScript/bot-verification screen in the research reader. No claims about its interactive behavior are made. The application comparison is therefore limited to accessible Expedia content; API and Leaflet decisions are grounded in their primary documentation.

Implementation revision from browser evidence: Leaflet's popup Enter handler did not trigger our `click` selection listener. Added explicit Enter and Space selection and updated marker styles in place, preserving keyboard focus. Layout follows the early mockup, with a larger introductory hero, numbered cards, and separate navigation to the earlier sample application.
