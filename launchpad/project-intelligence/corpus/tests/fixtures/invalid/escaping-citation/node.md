---
id: validator-fixture-escaping-citation
type: verification
status: active
origin: launchpad
audiences:
  - agent
evidence:
  - statement: "This citation climbs out of the repository with a relative path."
    entry_class: FACT
    evidence:
      - "../../../../../../../../etc/passwd"
  - statement: "This citation names a real directory rather than a real file."
    entry_class: FACT
    evidence:
      - "launchpad"
---

Invalid fixture: two escapes from the same missing check. An earlier revision tested
only `(repo_root / citation).exists()`, so a `..` chain resolved outside the repository
and "validated" against the host filesystem, while a bare directory name passed as
though it were a file. Both are now resolved and required to sit beneath the repository
root and to be a file. A cross-model review panel found both.
