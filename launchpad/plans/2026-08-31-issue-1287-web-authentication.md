# Plan: issue #1287 — platforms/web/authentication corpus node

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/web/authentication.md` does not exist yet (no
  `platforms/` directory exists in the corpus at all yet).
- `launchpad/docs/corpus/schema/node.schema.json` requires `id`, `type`, `status`,
  `origin`, `audiences`, `evidence`; `type` is a closed 13-value enum that includes
  `platforms`; `relationships` is optional and must resolve against whatever the
  corpus tree looks like on the branch being merged into.
- No `platforms`-typed node exists yet anywhere in this checkout to copy front matter
  from directly, but sibling batches (per dispatch brief) have already settled
  `type: platforms` as the convention for `platforms/**` docs, borrowing
  `templates/component.md`'s section shape (Responsibility / Public interface /
  Dependencies / Boundary / Relationships / Scope and omissions) since no
  platforms-specific template exists yet.
- `architecture-containers-web` (`launchpad/docs/corpus/architecture/containers/web.md`)
  already documents the web container's high-level security posture (NIP-98 for git +
  invite-claim, NIP-42 for relay queries, same-origin default) at a container-summary
  level; this node goes one level deeper into the web client's own auth *mechanics*
  (the actual TS modules, call sites, and fallback behavior) without restating that
  container-level prose.
- `architecture-flows-websocket-authentication` already documents the relay-side NIP-42
  challenge/response protocol in full (challenge generation, `verify_nip42_event`,
  `AuthState`, timeout enforcement). This node's own NIP-42 section only needs to cover
  the web client's own call site (`nostr-client.ts`'s `queryEvents`) and reference that
  node for the server side, not re-derive it.
- `architecture-flows-http-event-submission` already documents the relay's generic
  NIP-98 HTTP bridge (`verify_bridge_auth_with_options` / `buzz_auth::verify_nip98_event`)
  used by `POST /events`, `/query`, `/count` — and, confirmed by reading
  `crates/buzz-relay/src/api/invites.rs`'s own `authenticate()` helper, the exact same
  bridge is what `POST /api/invites/claim` calls. This node references that flow node
  for the server-side verification path instead of re-describing `verify_nip98_event`.
- `architecture-flows-git-push` documents the git HTTP `GitAuth` NIP-98 gate, but its own
  scope table explicitly excludes `git clone`/`git fetch`, stating fetch "shar[es] only
  `GitAuth` and repo/tenant resolution" with the push flow. Confirmed by reading
  `crates/buzz-relay/src/api/git/transport.rs` that `info_refs` and `upload_pack` (the
  read/fetch path the web client's `git-client.ts` uses) both take the same `GitAuth`
  extractor as `receive_pack`. This node references `architecture-flows-git-push` for
  that shared server-side gate rather than re-describing `GitAuth`.
- Web client source read directly: `web/src/shared/lib/nostr-signer.ts`,
  `web/src/shared/lib/nip98.ts`, `web/src/shared/lib/nostr-client.ts`,
  `web/src/shared/lib/relay-url.ts`, `web/src/shared/lib/pubkey.ts`,
  `web/src/features/repos/git-client.ts`, `web/src/features/invite/invite-api.ts`,
  `web/src/features/repos/ui/ConnectButton.tsx`, `web/tests/e2e/smoke.spec.ts`.
- Repository revision for this node: `46eb901e5aa928aa147fdaef9a509b636218653f`.

## STEP 1 — Write front matter

`id: platforms-web-authentication`, `type: platforms`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, reviewer]`. One evidence entry per
substantive claim, each `FACT` citing a file actually opened above, plus the provenance
commit entry. `relationships`: `references` toward `architecture-containers-web`,
`architecture-flows-websocket-authentication`, `architecture-flows-http-event-submission`,
and `architecture-flows-git-push` — all four confirmed present in this worktree, which
was freshly checked out from `origin/launchpad`.

## STEP 2 — Write the body

Sections: purpose/scope statement; NIP-07-first signing with ephemeral fallback
(`nostr-signer.ts`); NIP-42 relay auth call site (`nostr-client.ts`'s `queryEvents`),
referencing the websocket-authentication node for the server side; NIP-98 HTTP auth
header construction (`nip98.ts`) and its two call sites — git smart HTTP
(`git-client.ts`, always signs `method: "GET"` regardless of the actual HTTP verb,
referencing git-push for why the relay doesn't check method on git routes) and the
invite-claim POST (`invite-api.ts`, `requireNip07: true`, referencing
http-event-submission for the server-side bridge); same-origin URL derivation
(`relay-url.ts`); boundary statement; scope-and-omissions.

## STEP 3 — Validate isolation of new FAILs

Run `validate.py` with the new file present, then with it temporarily moved out, diff
the FAIL sets, confirm identical, restore the file.

## STEP 4 — Commit gate

Run the corpus unittest suite as the sole content of one Bash call, then stage + commit
as the sole content of the next Bash call, both `cd`-prefixed to the worktree.

## STEP 5 — Verify

Re-read the diff against every DoD bullet in #1287; re-open every cited file/line one
more time; confirm the FAIL-set diff from Step 3 is still empty.

## GATES

- Zero new `validate.py` FAIL lines versus the clean `origin/launchpad` baseline.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → `OK`.
- Every relationship target resolves against `origin/launchpad` as checked out in this
  worktree.
- Every FACT evidence entry cites a file this session actually opened.

## OPEN

- Whether a `platforms`-specific template will later replace the `component.md`-shaped
  convention this node (and its siblings) currently borrow — not this task's call to
  make; flagged in the node's own Scope and omissions.
- IndexedDB/LightningFS credential or clone-cache lifecycle is out of scope for an
  *authentication* node specifically (it's already flagged as unverified in the web
  container node) and is not re-litigated here.

## LEFT OUT

- Any edit to `architecture-containers-web`, `architecture-flows-websocket-authentication`,
  `architecture-flows-http-event-submission`, or `architecture-flows-git-push` — this task
  references them, it does not touch them.
- Server-side implementation detail beyond what's needed to point at the right existing
  node (`verify_nip42_event`, `verify_nip98_event`, `GitAuth`, `bind_community`, etc. are
  all already documented elsewhere and are cited by reference, not re-derived).
- Desktop/mobile/CLI authentication — separate containers, no existing corpus nodes for
  them were found, out of scope for a web-scoped node.
