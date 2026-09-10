# Plan: issue #1270 — document platforms/relay/git-api.md

Parent: Feature #614 ("runtime platform corpus exists"). Target file:
`launchpad/docs/corpus/platforms/relay/git-api.md`. This document stops at a
local commit — no push, no PR (batch integrates later into one PR).

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/relay/git-api.md` does not exist on
  `origin/launchpad` (nor does any `platforms/` directory yet — this is the
  first node under that surface).
- `launchpad/docs/corpus/architecture/flows/git-push.md`
  (`id: architecture-flows-git-push`) already exists, merged, and
  exhaustively documents the `git push` / `git-receive-pack` transport,
  authentication (NIP-98 + NIP-43), the pre-receive policy callback and its
  role/ref-update permission matrix, and the CAS-publish → kind:30618
  sequence. It explicitly scopes out `git clone`/`git fetch`
  (`info/refs`, `git-upload-pack`) as "a read flow with its own
  authorization surface, sharing only `GitAuth` and repo/tenant resolution
  with this one."
- No `platforms`-specific template exists in `launchpad/docs/corpus/templates/`.
  Per a prior batch's settled convention (not independently re-derived here),
  sibling `platforms/**` nodes use `type: platforms` and borrow
  `templates/component.md`'s section shape (Responsibility, Public interface,
  Dependencies, Boundary, Relationships, Scope and omissions) since no
  platforms-specific template is merged yet.
- The actual git smart-HTTP module lives at `crates/buzz-relay/src/api/git/`
  (`mod.rs`, `transport.rs`, `hook.rs`, `policy.rs`, `binding.rs`,
  `hydrate.rs`, `manifest.rs`, `manifest_event.rs`, `pack_cache.rs`,
  `store.rs`, `cas_publish.rs`). Its own module doc (`mod.rs`) states:
  "Git hosting — Smart HTTP transport, permission hooks, and policy engine."
- `git_router` (in `transport.rs`) mounts three public endpoints under
  `/git/{owner}/{repo}/...`: `GET info/refs`, `POST git-upload-pack`,
  `POST git-receive-pack`, all behind one `RequestBodyLimitLayer` sized from
  `state.config.git_max_pack_bytes`. A separate `git_policy_router` mounts
  `POST /internal/git/policy` behind a loopback-only middleware and a 1 MB
  body limit — this is the pre-receive hook's callback target, already
  covered in depth by `architecture-flows-git-push`.
- The **read path** (`info_refs`, `upload_pack`) is not covered by
  `architecture-flows-git-push` and has its own, simpler authorization model
  (`authorize_git_read` / `read_role_allows`: any current, recognized channel
  membership role — no push-style permission-matrix tiering), a "Track C"
  fast path that serves the clone advertisement directly from the published
  manifest with no hydrate/subprocess/permit for branches-only repos, and a
  streamed (not buffered) `git-upload-pack` response.
- `git-credential-nostr` (NIP-98 credential helper) and `git-sign-nostr`
  (NIP-GS commit/tag signing) are separate client-side crates that interop
  with this API surface but are not part of the relay's own dependency graph.

## STEP 1 — Confirm scope boundary against git-push.md

Read `architecture-flows-git-push.md` in full (done) to fix the exact line
between what it already owns (push transport, auth, policy, CAS, kind:30618)
and what remains undocumented (the API surface as a whole: routing/mounting,
body limits, the read path, the shared `GitAuth` extractor, client-side
interop crates). Write this node to cover the latter and `references`
(not duplicate) the former for push-specific detail.

## STEP 2 — Gather evidence from the read path and router assembly

Read `crates/buzz-relay/src/api/git/mod.rs` (module structure/responsibility),
`transport.rs` (`git_router`, `git_policy_router`, `GitAuth`, `info_refs`,
`info_refs_subprocess`, `upload_pack`, `authorize_git_read`,
`read_role_allows`, `decode_git_request_body`), and confirm dependency edges
via `crates/buzz-relay/Cargo.toml` (`buzz-auth`, `buzz-core`, `buzz-db`,
`tower-http`, `async-compression`). Identify representative unit tests
(`read_gate_allows_current_member_denies_removed_and_owner_bypass`,
`fast_path_eligible_branches_only`, `upload_pack_stream_*`) that exercise
this surface without live infrastructure.

## STEP 3 — Draft the node

Write `launchpad/docs/corpus/platforms/relay/git-api.md` with `type:
platforms`, `status: draft`, `origin: launchpad`, following
`templates/component.md`'s section shape (stated explicitly as a borrowed
convention, since no `platforms` template is merged). Cover: responsibility,
the four HTTP endpoints (public interface), dependencies (both crate-level
and client-side interop), the read-path authorization model and streaming
behavior, an explicit boundary naming everything `architecture-flows-git-push`
already owns, a `references` relationship to `architecture-flows-git-push`,
and a scope-and-omissions section naming what was expected but not verified
(no live e2e run; hook/policy/CAS internals deliberately not re-derived here).

## STEP 4 — Validate isolation

Temporarily move the new file aside, run `validate.py`, confirm the FAIL set
is byte-identical to the pre-existing baseline, then restore the file and
re-run to confirm it adds zero new FAILs.

## STEP 5 — Earn the commit gate

Run the corpus unittest discovery command as the sole content of one Bash
call, then stage and commit (`git commit -s`) as a second, separate call.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` — new node
  contributes zero new FAIL lines versus the pre-existing baseline.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` — must report `OK`, run as the sole content of its Bash call.
- Every evidence citation opened and read directly from this worktree; every
  cited path is a real file, not a bare directory.
- Every DoD checklist bullet in issue #1270 satisfied.

## OPEN

- Whether `platforms/relay/git-api.md` will later gain a `part-of` or sibling
  edge once other `platforms/relay/*` nodes land — left for a later pass,
  since none exist yet on `origin/launchpad`.
- Whether a `platforms`-specific template eventually reshapes this node's
  structure (per `AGENTS.md`'s own stated expectation for nodes written
  before their type's template exists).

## LEFT OUT

- Re-documenting push transport, NIP-98/NIP-43 authentication detail, the
  pre-receive policy callback, the permission matrix, or the CAS-publish /
  kind:30618 sequence — all already owned by `architecture-flows-git-push`
  and referenced, not duplicated.
- `git-sign-nostr`'s NIP-GS signing mechanics and `git-credential-nostr`'s
  internals — named as related client-side interop tooling only, since
  neither is part of the relay's own API surface.
- Deep internals of `hydrate.rs`, `manifest.rs`, `store.rs`, `pack_cache.rs`,
  `cas_publish.rs` (object-store hydration/publish machinery) — out of scope
  for a component-level API-surface node; cited only at the granularity the
  HTTP handlers observe them.
