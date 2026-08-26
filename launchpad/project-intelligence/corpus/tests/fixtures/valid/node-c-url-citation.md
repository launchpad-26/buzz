---
id: validator-fixture-c-url-citation
type: architecture
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "A commit-pinned repository file link is accepted even when its path superficially resembles a credential-like filename."
    entry_class: FACT
    evidence:
      - "https://github.com/launchpad-26/buzz/blob/69baedd197e5d35c9ae4736115789da59929e288/.env.example"
      - "[.env.example at a pinned commit](https://github.com/launchpad-26/buzz/blob/69baedd197e5d35c9ae4736115789da59929e288/.env.example)"
---

# Validator fixture C: commit-pinned URL citations are accepted

Both citations would be rejected by the credential blocklist if it ran before the URL
check -- an independent review-code pass found exactly that ordering bug before this
fixture existed. This proves the fix, not just that it was made.

Both are also pinned to a full commit SHA. An earlier revision of this fixture used
`blob/main`, and passed, because the validator waved every `http` string through
unchecked -- a cross-model review panel found that the fixture was asserting the
opposite of the contract it was meant to demonstrate. The mutable-ref case now lives in
`invalid/mutable-url-citation/`, where it belongs.

Only the second citation is ADR-0003's prescribed shape: a markdown link to the pinned
file. The first is a bare pinned URL, which the validator also accepts -- pinning is the
property ADR-0003 exists to guarantee, and a bare pinned URL has it. A review-final pass
read the earlier wording here as claiming the bare form satisfies ADR-0003's *format*,
which it does not; the two citations sit side by side to make the distinction visible,
with the markdown-link case proving the link is unwrapped to its target before the pin
is checked rather than falling through as an unrecognised shape.
