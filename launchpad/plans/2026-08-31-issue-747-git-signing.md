# Plan: issue #747 — document capabilities/git/git-signing.md

Parent: Feature #613 (batch corpus authoring). Task: create exactly one canonical
corpus node, `launchpad/docs/corpus/capabilities/git/git-signing.md`, documenting
NIP-GS git object signing with Nostr keys as a capability.

## ALREADY TRUE

- Repo revision: `git rev-parse HEAD` = `cad6c375f...` (worktree branched from
  `origin/launchpad` at commit `cad6c375f9...`, merge of PR #1945).
- `launchpad/docs/corpus/capabilities/` does not exist yet — this is the first
  node under `capabilities/`, and the first node in the corpus overall (per
  `templates/capability.md`'s own evidence ledger, only 4 procedural/meta nodes
  are merged: `corpus-agents`, `corpus-readme`,
  `corpus-standard-confidence`, `corpus-standard-decision-references` — none
  capability-shaped). `architecture-flows-git-push` (type: architecture) is
  also merged and already names NIP-GS signing as an explicitly out-of-scope,
  related concern in its own Scope and omissions table.
- The capability: `crates/git-sign-nostr` implements NIP-GS
  (`docs/nips/NIP-GS.md`) — a pluggable git signing program
  (`gpg.x509.program`) that signs/verifies commits and tags with BIP-340
  Schnorr signatures using a Nostr secp256k1 keypair, with optional NIP-OA
  owner-attestation embedding. Shipped via merged PRs #455 (NIP), #459
  (implementation), #528 (agent auto-signing wiring), #708 (dep migration).
  `VISION_PROJECTS.md`'s Status table lists "Git hosting (smart HTTP +
  NIP-34)" as its own shipped row but has no separate row for object signing —
  maturity for this node rests on code/commit evidence, not a VISION status
  marker.
- `node.schema.json`'s `type` enum includes `capabilities` (not `capability`).
  `templates/capability.md` is the governing template: required sections are
  Capability statement, Maturity, Boundary, Relationships, Scope and
  omissions.
- No existing corpus node targets `capabilities-git-git-signing`; no
  relationship target currently resolves except `architecture-flows-git-push`
  (merged, already references NIP-GS as a boundary item) and
  `corpus-template-capability` (merged template, optional `implements` edge).

## STEP 1 — Draft the node

Write `launchpad/docs/corpus/capabilities/git/git-signing.md` against
`templates/capability.md`'s skeleton:
- Capability statement: "Nostr-signed git commits and tags" — a human or
  agent's existing Nostr identity cryptographically signs their git history,
  with no separate GPG/SSH key needed.
- Maturity: shipped, cited to `crates/git-sign-nostr` (lib.rs, README.md,
  Cargo.toml) and the NIP-GS spec doc, plus the merge commits that shipped it.
- Boundary: not architecture (references `architecture-flows-git-push` for the
  transport/push flow this is orthogonal to); not an interface node (none
  exists yet for git-sign-nostr's CLI surface); not a flow node (#1338, not
  drafted); not operations.
- Relationships: `references` → `architecture-flows-git-push` (merged,
  resolves); optionally `implements` → `corpus-template-capability`.
- Scope and omissions: NIP-OA owner-attestation mechanics live primarily in
  NIP-OA itself (out of this node's depth); key zeroization/unsafe-code
  details are implementation, not capability, and are left to a future
  implementation-reference node if one is written.

Done when: file exists, front matter has all required fields, no invented
enum values, every FACT claim cites an opened source.

## STEP 2 — Validate structurally

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo
root. Fix anything it names. Confirm zero new FAIL entries beyond the 21
pre-existing ones tracked in #1951 (none of which are in this new file, since
it didn't exist before).

Done when: validator output shows this file passing and the pre-existing
FAIL count on other files is unchanged.

## STEP 3 — Self-review against DoD

Re-read #747's checklist line by line against the drafted file. Re-open every
cited source (lib.rs doc comment, README.md, Cargo.toml, NIP-GS.md, the merge
commits) to confirm each FACT claim is actually supported, not just citing a
real path. Confirm exactly one hand-authored file was added (plus this plan).

Done when: every checklist bullet has a concrete answer, not "N/A".

## STEP 4 — Earn the commit gate

Run, as the sole command in its own tool call:
```
python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"
```
Confirm `OK`. Then, in a separate call, `git add` the new doc + this plan and
`git commit -s`.

Done when: commit exists on `task/747-git-signing`, nothing pushed.

## GATES

- `validate.py` exits 0 with no new FAIL entries.
- `unittest discover` on corpus tests prints `OK`.
- Every FACT evidence entry cites a path actually opened during drafting.

## BUDGET

Single node, ~1 file. No code changes. Capped effort: this is a documentation
task, not an implementation task.

## OPEN

- Whether a future `implementation-reference` node should cover
  `git-sign-nostr`'s internals (zeroization, unsafe fd handling, ecosystem
  constraints) — left for a separate task if one is filed; this node stays at
  capability altitude per the template's Boundary section.

## LEFT OUT

- Any second corpus document (interface node for the CLI surface, flow node
  for sign/verify sequencing) — out of scope per #747's own DoD and the
  template's one-idea-per-node rule.
- Editing `architecture-flows-git-push` to add a reciprocal relationship —
  that node's own relationships are its author's to manage; this node adds a
  one-directional `references` edge only, which the schema permits.
