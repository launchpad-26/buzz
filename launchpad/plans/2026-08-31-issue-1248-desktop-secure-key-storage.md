# Plan: issue #1248 — platforms/desktop/secure-key-storage.md

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/desktop/secure-key-storage.md` does not exist yet
  (confirmed against this worktree, checked out from `origin/launchpad`).
- The desktop secure-key-storage implementation is real and already reviewed-in:
  `desktop/src-tauri/src/secret_store.rs` (OS keyring blob store, per-platform
  backend, interprocess advisory lock, legacy migration), `desktop/src-tauri/src/
  app_state.rs` (identity resolution/generation/migration state machine,
  `0o600` file fallback), `desktop/src-tauri/src/identity_storage.rs`
  (`IdentityStorage` enum), `desktop/src-tauri/src/commands/identity.rs`
  (`import_identity`, `persist_current_identity` Tauri commands), and
  `desktop/src-tauri/src/reset.rs` (sign-out keychain wipe + verification).
  `desktop/src-tauri/src/managed_agents/storage.rs` reuses the same
  `SecretStore` for per-agent nsecs.
- `architecture-containers-desktop` (`launchpad/docs/corpus/architecture/
  containers/desktop.md`) is already merged on `origin/launchpad` and already
  summarizes key storage at container level (one evidence bullet, four file
  citations) — a real, existing `part-of` relationship target for this
  component-level node, avoiding duplication of its content.
- No `platforms/` node exists yet anywhere in the merged corpus tree, so there
  is no established sibling to match structurally; `component.md`'s document
  *shape* (purpose, responsibility/interface, dependencies, boundary,
  relationships, scope-and-omissions) is the closest-fitting existing template
  even though its own front matter recommends `type: implementation` for a
  generic standalone component — this node's `type` is `platforms` instead,
  per `standards/taxonomy.md`'s own instruction to pick by subject (a single
  runtime platform's implementation-facing behavior) and per Feature #614's
  own framing ("desktop ... documented as atomic implementation-facing system
  views").

## STEP 1 — Confirm scope and non-duplication

Re-read `architecture-containers-desktop`'s key-storage bullet to ensure the
new node goes deeper (backend selection, migration state machine, wipe/verify
path) rather than restating its one summary sentence.

## STEP 2 — Draft the node

Write `launchpad/docs/corpus/platforms/desktop/secure-key-storage.md` with:
`id: platforms-desktop-secure-key-storage`, `type: platforms`,
`status: draft`, `origin: launchpad`, `audiences: [developer, operator,
reviewer, agent]`, an evidence ledger citing only sources actually opened
(`secret_store.rs`, `app_state.rs`, `identity_storage.rs`, `commands/
identity.rs`, `reset.rs`, `managed_agents/storage.rs`, `Cargo.toml`), and one
`relationships: [{type: part-of, target: architecture-containers-desktop}]`
edge (verified present on `origin/launchpad`). Body: responsibility, backend
selection matrix (macOS/Windows/Linux), the blob format and interprocess
lock, the identity resolution/migration state machine, the `0o600` file
fallback, sign-out wipe/verify, dependents (managed agent keys), boundary,
scope-and-omissions.

## STEP 3 — Validate isolation

Stash the new file, run `validate.py`, confirm the pre-existing 21-FAIL
baseline is unchanged, restore the file, re-run and confirm no *new* FAIL
lines (only the expected `UNVERIFIED` provenance/commit notice).

## STEP 4 — Earn the commit gate

Run the corpus unittest discovery command as the sole content of its own
Bash call, then commit with `-s` in a separate call.

## STEP 5 — Verify against the issue DoD

Re-read the diff against issue #1248's Definition of Done checklist line by
line; confirm exactly one hand-authored file; confirm every citation was
actually opened; confirm the node stays component-scoped (does not restate
the whole desktop container).

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` — zero new FAIL
  lines vs. the pre-existing 21-FAIL baseline.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
  -p "test_*.py"` — must report `OK`, run alone in its own Bash call.

## OPEN

- Whether `type: platforms` will later be reconciled once a per-`platforms`
  standard or template lands (none exists yet at this revision) — flagged in
  the node's own scope-and-omissions rather than resolved here.

## LEFT OUT

- Documenting agent-key storage (`managed_agents/storage.rs`) as its own
  concept in depth — named only as a dependent/consumer of the same
  `SecretStore`, per the one-node-one-idea rule; a deeper agent-key node is a
  separate task if wanted.
- Any change to runtime behavior. Documentation only.
