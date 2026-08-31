# Issue #801: document capabilities/pairing/pairing-cli.md

Parent: Feature #613 (corpus batch). Worktree: `__worktrees/task-801-pairing-cli`,
branch `task/801-pairing-cli`, base `origin/launchpad` @ `cad6c375fdcc590158c1456c9fc7875f0f84a844`.

## ALREADY TRUE

- `crates/buzz-pairing-cli` exists: a `buzz-pair` binary crate (Cargo.toml,
  README.md, src/main.rs — 623 lines, no `#[cfg(test)]`), described in its own
  `Cargo.toml` as "CLI tool for NIP-AB device pairing interop testing".
- The crate implements `source`, `target`, and `test-vectors` subcommands
  exercising `buzz_core::pairing::session::PairingSession` over a live Nostr
  relay via `tokio-tungstenite`, using event kind `KIND_PAIRING` (24134,
  `crates/buzz-core/src/kind.rs:465`).
- `launchpad/docs/corpus/capabilities/` does not exist yet on `origin/launchpad`
  — this is the first node under `capabilities/`, and no `pairing-*` sibling
  node (#800 device-pairing, #802 pairing-relay, #803 pairing-session) is
  merged, so no `relationships` targets currently resolve.
- The `capability` template (`launchpad/docs/corpus/templates/capability.md`)
  is the authority for required sections (Capability statement, Maturity,
  Boundary, Relationships, Scope and omissions) and for citing real,
  repo-relative paths rather than `#symbol=`/`#line=` fragments.

## STEP 1 — Draft the node

Write `launchpad/docs/corpus/capabilities/pairing/pairing-cli.md` with:
- Front matter: `id: capabilities-pairing-pairing-cli`, `type: capabilities`,
  `status: draft`, `origin: launchpad`, `audiences: [developer, agent]`,
  `evidence` citing `crates/buzz-pairing-cli/Cargo.toml`,
  `crates/buzz-pairing-cli/README.md`, `crates/buzz-pairing-cli/src/main.rs`
  (bare paths / line ranges, no `#symbol=`), plus the provenance commit entry.
  No `relationships` (nothing resolvable is merged yet — verified above).
- Body: capability statement (interop-testing CLI for NIP-AB pairing),
  maturity (shipped — cites the crate + its Cargo workspace membership),
  boundary (not the protocol spec itself, not the relay-side pairing sidecar,
  not the session state machine, not a production pairing UI), relationships
  section explicitly noting none resolve yet, scope/omissions table.

Done-when: file exists, front matter matches schema, every DoD bullet from
issue #801 addressed line by line.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo
root. Done-when: exit 0, and diffing FAIL count against the known 21
pre-existing baseline (issue #1951) shows zero new FAIL entries attributable
to this node.

## STEP 3 — Earn the commit gate

Run, as the sole command in its own call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
Done-when: `OK`.

## STEP 4 — Commit

`git add` the new doc + this plan file; `git commit -s -m "docs(corpus): document capabilities/pairing/pairing-cli (#801)"`.
Done-when: commit created, no push, no PR.

## GATES

- `validate.py` exit 0, zero new FAIL entries.
- `unittest discover` on corpus tests: OK.
- Signed-off commit (`-s`).

## BUDGET

Single file + this plan. No code changes.

## OPEN

- Sibling capability nodes (#800/#802/#803) are being authored in parallel;
  this node deliberately declares no relationships to them since none are
  merged, per the template's own precedent for parallel batch authoring.

## LEFT OUT

- Any relationships to `#800`/`#802`/`#803` (device-pairing, pairing-relay,
  pairing-session) — add once those nodes merge to `origin/launchpad`.
- Any edit to `crates/buzz-pairing-cli` itself — documentation only.
