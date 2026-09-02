---
name: valid-technique-1
summary: First valid test technique
reach-for-when:
  - Service responds but data is wrong
evidence-required:
  - Response logs
reduces-with: delta
cost: low
---

# Valid Technique 1

## Reach for it when
Service is returning 200 but with incorrect data.

## Evidence it needs
HTTP response logs and expected vs actual output.

## How to run it
1. Capture the response
2. Compare to expected
3. Document differences

## Worked example
API endpoint returned user ID 5 instead of 3. Delta showed the query was modified after caching.

## Done when
You have identified the specific field that is wrong and why.

## Don't use it for
Finding hidden performance issues unrelated to data correctness.
