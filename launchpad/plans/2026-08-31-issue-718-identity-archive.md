# Plan: issue #718 — document capabilities/archive/identity-archive.md

Parent: Feature #613 (corpus batch). DoD is the issue's own checklist; this plan
exists to scope the work, not to restate the schema.

## ALREADY TRUE

- `launchpad/docs/corpus/templates/capability.md` exists and gives the required
  body shape for a `type: capabilities` node: capability statement, maturity,
  boundary, relationships, scope-and-omissions.
- `node.schema.json`'s `type` enum member is `capabilities` (plural), not
  `capability`.
- `origin/launchpad`'s corpus tree has no `capabilities/` subtree yet — this
  will be the first node of that type. No capability, interface, or flow node
  exists for identity archival to `references`.
- A sibling, *not yet merged*, node already exists for the same subject at a
  different path and type: `launchpad/docs/corpus/layers/identity/identity-archive.md`
  (open PR #1812, issue #1107, `type: layers`) — a protocol-level concept node
  for NIP-IA. It explicitly names issue #718 as a distinct capability-shaped
  node at a distinct path. Since it is unmerged, it is not a valid
  `relationships` target (must resolve against `origin/launchpad`).
- Target file `launchpad/docs/corpus/capabilities/archive/identity-archive.md`
  does not exist.
- NIP-IA (`docs/nips/NIP-IA.md`), the relay handler
  (`crates/buzz-relay/src/handlers/identity_archive.rs`), the DB module
  (`crates/buzz-db/src/store/archived_identities.rs`), the desktop commands
  (`desktop/src-tauri/src/commands/identity_archive.rs` +
  `desktop/src/features/identity-archive/hooks.ts`), the CLI subcommands
  (`crates/buzz-cli/src/commands/agents.rs`: `archive`/`unarchive`/`archived`),
  and two Playwright specs (`desktop/tests/e2e/identity-archive.spec.ts`,
  `identity-archive-hide.spec.ts`) were opened directly at HEAD
  `cad6c375fdcc590158c1456c9fc7875f0f84a844` to ground every FACT claim (paths
  differ from the unmerged sibling node's citations in two cases — the DB
  module moved to `store/`, the predicate hook lives in
  `features/identity-archive/hooks.ts` — confirmed at current HEAD, not copied).

## STEP 1 — Write the node

Create `launchpad/docs/corpus/capabilities/archive/identity-archive.md`,
`type: capabilities`, `id: capabilities-archive-identity-archive`, following
the template skeleton: capability statement (naming the product-level thing —
"a relay can retire a stale identity from active-member/autocomplete UI
without deleting its history or banning it"), a dedicated behavioral
rules/constraints/variants section (three consent paths, anti-shadowban
self-unarchive, composability with NIP-43 removal), maturity (shipped, cited
to relay/db/desktop/cli code + tests), boundary (not the NIP-IA protocol
concept itself — that is #1107/layers — not architecture, not a flow), links
to major flows/interfaces/data/platform surfaces via prose + evidence
citations (no schema `relationships` since no valid targets exist), and
scope-and-omissions.

Done when: file exists, front matter is schema-shaped, every evidence entry
cites a source actually opened in this session.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo
root. Done when: exit 0, and diffing the error/warning set against the known
21 pre-existing FAIL baseline (issue #1951) shows zero new FAIL entries
attributable to the new node.

## STEP 3 — Earn the gate and commit

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in its own call; confirm `OK`. Then, in a separate call,
`git add` the node + this plan and commit with `-s`.

## GATES

- `validate.py` exit 0, zero new FAIL vs. baseline.
- `unittest discover` on corpus tests: `OK`.

## BUDGET

Single step of substantive writing (Step 1); capped well under 5 steps.

## OPEN

- Whether `layers-identity-identity-archive` (once #1812 merges) should later
  gain a `references`/`part-of` edge from this node — left for a follow-up
  edit once that id resolves in `origin/launchpad`, per `AGENTS.md`'s rule
  against targeting unmerged ids.

## LEFT OUT

- Any edit to the sibling `layers/identity/identity-archive.md` node — it is
  a different, currently-open task (#1107) and not this task's file to touch.
- A `references`/`part-of` relationship to any capability/interface/flow node
  — none exist yet in `origin/launchpad` for this subject.
