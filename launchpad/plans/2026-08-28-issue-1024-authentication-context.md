# Plan: issue #1024 — document `layers/authentication/authentication-context.md`

Parent PRD: #607 (F04-IDENTITY-SECURITY). Batch owner review is deferred; this PR is
opened as a draft per the batch's process.

## ALREADY TRUE

- `launchpad/docs/corpus/layers/authentication/authentication-context.md` does not
  exist (`layers/` is not present under `launchpad/docs/corpus/` on `origin/launchpad`
  or in this worktree — confirmed via `git ls-tree -r origin/launchpad -- launchpad/docs/corpus`).
- The `concept.md` template is merged on `origin/launchpad`
  (`launchpad/docs/corpus/templates/concept.md`) and its required-sections list
  (Definition, Use cases, optional Comparison/Background/Related resources, Scope and
  omissions) matches issue #1024's document-type-specific DoD tail almost verbatim
  (one-sentence definition, boundaries/non-goals, links to related concepts/
  implementation/verification, examples only clarify — never a second concept).
- `crates/buzz-auth/src/lib.rs` defines `AuthContext` (pubkey, scopes, channel_ids,
  auth_method, agent_owner_pubkey) — the connection-scoped authentication context
  produced by NIP-42 verification, per its own module doc: "All paths produce an
  `AuthContext` bound to the connection."
- `crates/buzz-relay/src/handlers/ingest.rs` defines a second, transport-neutral
  `IngestAuth` enum (`Nip42 { .. }` / `Http { .. }`) used by the shared WS+HTTP
  event-ingestion pipeline — constructed from `AuthContext`'s fields at
  `crates/buzz-relay/src/handlers/event.rs:754` (WS) and
  `crates/buzz-relay/src/api/bridge.rs:833` (HTTP `POST /events`).
- `launchpad/docs/corpus/architecture/flows/websocket-authentication.md`
  (id `architecture-flows-websocket-authentication`) is already merged on
  `origin/launchpad` and documents in detail *how* an `AuthContext` gets produced
  (the NIP-42 challenge/response flow); it does not itself define what the concept
  *is*, its boundary against `AuthState`/`TenantContext`, or its `IngestAuth`
  sibling — this task's node fills that gap and can `references` it.

## STEP 1 — Confirm no in-flight duplicate

Re-check `launchpad/docs/corpus/layers/` is absent and search open PRs for a branch
already targeting this path/issue. Done-when: confirmed absent, no competing PR found.

## STEP 2 — Draft the node

Hand-author
`launchpad/docs/corpus/layers/authentication/authentication-context.md` against
`node.schema.json` and the `concept.md` template (front matter:
`id: layers-authentication-authentication-context`, `type: layers`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer]`). Definition
section states the concept in one sentence and names both concrete Rust
manifestations (`buzz_auth::AuthContext`, `handlers::ingest::IngestAuth`). Boundary
section distinguishes it from `AuthState` (the enum that *contains* one once
authenticated), `TenantContext` (community scoping, resolved independently), and
session/token auth (module doc's explicit invariant: no JWT, no token, no IdP).
Comparison section tables `AuthContext` vs `IngestAuth`. One `references`
relationship to `architecture-flows-websocket-authentication` (confirmed present on
`origin/launchpad`). Every claim gets one evidence entry, classified honestly.
Done-when: file written, every DoD bullet from #1024 addressed in the body.

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root.
Done-when: exit 0.

## STEP 4 — Earn the verify-gate and commit

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` as the sole command in its own tool call; confirm `OK`. Then commit with
`git commit -s`. Done-when: suite reports OK, commit created (or a blocked-commit
finding reported without touching any stamp file).

## STEP 5 — Push and open the draft PR

Push the branch and open a draft PR against `launchpad`, body stating `Closes #1024`,
that `validate.py` and the corpus unittest suite passed, that verification was
self-review only (no `review-code` skill — this is a subagent), and the deferred
cross-model review line. Done-when: PR URL in hand.

## GATES

- `validate.py` exits 0 before every claim of completion.
- The commit-suite command above must actually report `OK` before committing.
- Exactly one hand-authored corpus document is created.

## OPEN

- Whether a sibling task will later cover NIP-98's own dedicated flow node (the
  websocket-authentication.md node names this as a gap it doesn't cover either) —
  out of scope here; not filed by this task since it is PRD #607's/#602's territory,
  not this node's second-concept discovery.

## LEFT OUT

- No relationships beyond the one `references` edge to the existing flow node —
  no other in-scope corpus node target was confirmed present on `origin/launchpad`
  at the recorded revision.
- No edits to any file other than the one target document (plus this plan file).
