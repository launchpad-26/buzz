# Plan: issue #1177 — document layers/security/security-model.md

Parent: Feature #607 ("identity tenancy authentication authorization and security
corpus exists"), parent PRD #602.

## ALREADY TRUE

- `launchpad/docs/corpus/layers/security/security-model.md` does not exist yet, and no
  `layers/` node of any kind is merged on `origin/launchpad` (confirmed via
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`).
- Three merged corpus nodes already document adjacent security invariants in detail:
  `architecture-principles-community-is-security-boundary`,
  `architecture-principles-fail-closed-boundaries`,
  `architecture-principles-signed-events`.
- ARCHITECTURE.md §7 ("Security Model") and SECURITY.md already state the codebase's
  own summary of its security design; both are real, openable files.
- No corpus template fits a hand-authored composition/overview node; the closest
  candidate, `templates/threat-model.md`, is explicitly for an atomic, single-system
  STRIDE analysis (the shape issue #1180's sibling node will use), not this node.
- Fourteen sibling tasks (#1168-#1182, minus #1177 itself) are filed under Feature #607
  targeting the rest of `layers/security/`; none are merged.

## STEP 1 — Confirm scope and gather evidence

Read the issue DoD, `AGENTS.md`, `node.schema.json`, `templates/threat-model.md`,
`standards/taxonomy.md`, `standards/atomicity.md`, `standards/documentation-standard.md`,
and the three merged `architecture/principles/*.md` nodes. Read ARCHITECTURE.md §7 and
SECURITY.md in full, and verify a sample of their claims against real source
(`bind_community`, `is_private_ip` call site, admin `authorize()`, `buzz-auth` module
list, frame-size constant). Done when: evidence ledger entries are backed by opened
sources, not paraphrase.

## STEP 2 — Draft the node

Write `layers/security/security-model.md` directly against `node.schema.json` (no
template): `id: layers-security-security-model`, `type: layers`, `status: draft`,
composition-level trust-boundary diagram, a per-area table pointing to merged nodes and
future sibling paths, a STRIDE-orientation table, mitigations/verification links, and a
residual-risks section grounded in verified claims (including the rate-limiting gap and
the frame-size documentation-drift finding). Declare `references` only to the three
already-merged nodes. Done when: the file satisfies every DoD bullet in #1177 and does
not duplicate any sibling node's future canonical content.

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo root.
Done when: exit 0.

## STEP 4 — Earn the commit gate and commit

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` as a lone command; confirm `OK`. Then `git commit -s`. Done when: commit
succeeds without touching the stamp file or `--no-verify`.

## STEP 5 — Open the draft PR

Push the branch and open a draft PR against `launchpad`, body stating `Closes #1177`,
that `validate.py` and the unittest suite passed, that review was self-review only, and
the deferred-review line. Done when: PR URL exists and issue/PR numbers are reported
back.

## GATES

- `validate.py` exits 0 before commit.
- The corpus unittest suite passes as the sole command in its own tool call, immediately
  before commit.
- Exactly one hand-authored canonical document created:
  `layers/security/security-model.md`.

## OPEN

- Whether the fourteen sibling tasks will land with the exact filenames/ids assumed
  here — tracked as an explicit gap in the node's own scope-and-omissions section.
- The ARCHITECTURE.md frame-size documentation drift found during authoring is noted in
  the node but not filed or fixed separately (out of scope for a documentation-only
  corpus task).

## LEFT OUT

- Building or fixing anything in ARCHITECTURE.md, SECURITY.md, or the rate-limiter gap
  itself — this is a documentation task, not an implementation one.
- Any of the fourteen sibling `layers/security/*.md` documents — each is its own task.
