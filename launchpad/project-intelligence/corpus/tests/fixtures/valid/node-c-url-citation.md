---
id: validator-fixture-c-url-citation
type: architecture
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "URL citations are accepted as-is, even when their path superficially resembles a credential-like filename."
    entry_class: FACT
    evidence:
      - "https://example.com/posts/id_rsa-security-best-practices"
      - "https://github.com/launchpad-26/buzz/blob/main/.env.example"
---

# Validator fixture C: URL citations are accepted unconditionally

Both citations here would be rejected by the credential blocklist if it ran before
the URL passthrough check -- an independent review-code pass found exactly that
ordering bug before this fixture existed. This proves the fix, not just that it
was made.
