---
id: validator-fixture-e-citation-forms
type: verification
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "A file-range citation names real lines in a real repository file."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py:1-5"
  - statement: "A file-line citation names one real line in a real repository file."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py:1"
  - statement: "A bare path citation names a real repository file and carries no position."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "The three unopenable citation forms are reported as unverified, never as missing files."
    entry_class: FACT
    evidence:
      - "is_shared_gated_kind -> is_unshared_gated_event (1 hop)"
      - "find_references('x', crate='buzz-core') -> no callers in this crate"
      - "commit 69baedd197e5d35c9ae4736115789da59929e288 (2026-08-25) by Serina"
---

# Validator fixture E: all six citation forms

`launchpad/project-intelligence/CONTRACT.md` section 3 enumerates six citation shapes.
An earlier revision of the validator passed every non-URL citation straight to
`Path.exists()`, so five of these six were rejected as nonexistent files -- including
the two positional forms that CONTRACT.md itself uses as its worked examples. A
cross-model review panel found it.

The first three entries must validate clean. The fourth must produce no errors either:
a graph edge, a tool result and a commit reference name nothing openable, so they are
reported through the `UNVERIFIED` channel instead, which is exactly what CONTRACT.md
asks for -- "parse what is parseable, and report the rest as unverified rather than
skipping it".
