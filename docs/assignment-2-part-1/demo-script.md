# Assignment 2 Part 1 demonstration

1. Open the default discovery page. Identify the 5 km returned-point rule and absence of price/booking claims.
2. Submit `1234`: invalid-input feedback, no provider request.
3. Submit `02108`: loading, live result list and map, Boston postcode point, variable result count, 50-record cap, and honest missing-name labels.
4. Select the first list card: corresponding numbered marker highlights and opens its label.
5. Tab/focus the second marker and press Enter: the same hotel becomes selected in the list.
6. Clearly label response simulations, then demonstrate successful empty results, unresolved ZIP and provider failure. The unit tests separately simulate upstream 429 without consuming provider quota.
7. Show the narrow layout. State when a previously observed response is replayed to avoid additional service requests.
8. The original sample-stay page can be checked separately for regression; it is not the Assignment 2 submission feature.

Never display `.env`, provider request URLs containing keys, browser account information, or private data. This demo does not save hotels or claim persistence. Publish the finished recording to an instructor-accessible location after manual review.
