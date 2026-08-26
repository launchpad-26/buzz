---
id: validator-fixture-d-env-example-citation
type: development
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: ".env.example is this repo's own real, tracked, non-secret config template."
    entry_class: FACT
    evidence:
      - ".env.example"
---

# Validator fixture D: .env.example is not a credential

`.env.*` matches the prohibited-content blocklist, but `.env.example` (and
`.env.sample`/`.env.template`) are conventional non-secret suffixes and must be
exempted -- an independent review-code pass found this repo's own `.env.example`
would otherwise be rejected.
