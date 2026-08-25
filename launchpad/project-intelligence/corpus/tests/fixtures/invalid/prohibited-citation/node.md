---
id: validator-fixture-prohibited-citation
type: verification
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This citation names a credential-shaped filename on purpose."
    entry_class: FACT
    evidence:
      - "some/path/id_rsa"
---

Invalid fixture: the one evidence citation's basename matches the credential-like
blocklist (`id_rsa*`). Rejected without echoing the path itself.
