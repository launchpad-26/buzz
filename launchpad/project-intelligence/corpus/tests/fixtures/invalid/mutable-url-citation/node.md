---
id: validator-fixture-mutable-url-citation
type: verification
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This repository file link is pinned to a mutable branch ref on purpose."
    entry_class: FACT
    evidence:
      - "https://github.com/launchpad-26/buzz/blob/main/.env.example"
---

Invalid fixture: ADR-0003 fixes the reference format as a markdown link to the cited
file at the pinned commit, "using the full SHA. Never `blob/main`", and the schema
README repeats it. A `blob/main` link is evidence that can change underneath a green
validation run, which is the failure mode provenance exists to prevent.
