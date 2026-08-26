---
id: validator-fixture-b-auth-citation
type: architecture
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "buzz-auth is a real, ordinary, non-secret crate this repo publicly ships."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs"
---

# Validator fixture B: an ordinary path containing "auth" is accepted

Proves the credential-like blocklist is exact-filename/extension based, not a
substring match on words like "auth" -- an earlier draft of #623's plan would have
rejected this citation; serina:review-plan caught it before any code was written.
