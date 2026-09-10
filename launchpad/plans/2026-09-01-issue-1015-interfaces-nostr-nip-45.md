Issue #1015: document interfaces/nostr/nip-45.md
Stated size: small (single-document corpus task, dispatching instructions cap it explicitly)  ->  cap: 5 steps

ALREADY TRUE

- Worktree `__worktrees/task-1015-interfaces-nostr-nip-45` created off
  `origin/launchpad` on branch `task/1015-interfaces-nostr-nip-45`, HEAD at
  `c34e62d16781dac3fa45cdedf0f09d4e1d8bbe8f`.
- Issue #1015's body read via `gh issue view`. It targets
  `launchpad/docs/corpus/interfaces/nostr/nip-45.md` and its Definition of
  done requires: exactly one hand-authored canonical document; schema-valid
  front matter with stable id/type/status/origin/audiences/evidence/typed
  relationships; one independently maintainable node; every substantive
  claim traceable to code/test/spec/decision/config/GitHub evidence with
  FACT/INFERENCE/TEAM_KNOWLEDGE not conflated; links to implementation,
  verification, spec/decision and neighboring nodes without duplicating
  them; checked against the recorded revision; `validate.py` clean; and
  inputs/outputs/errors, auth, versioning, ordering, a spec link, and one
  valid + one failure example. Confirmed via directory listing that
  `launchpad/docs/corpus/interfaces/` does not exist yet in this
  worktree — nothing to update, this is a create.
- `launchpad/docs/corpus/AGENTS.md` and
  `launchpad/docs/corpus/schema/node.schema.json` read. `type` enum has 13
  members (architecture, layers, capabilities, platforms, implementation,
  interfaces-events, verification, operations, development, release,
  governance, agent, ingestion); the correct value for an interface-shaped
  node is `interfaces-events` (the single enum member PRD #602 uses to
  combine "interfaces" and "events" as one corpus surface).
- `launchpad/docs/corpus/templates/interface.md` (id
  `corpus-template-interface`) read in full. Confirmed merged on
  `origin/launchpad` via `git ls-tree -r --name-only origin/launchpad --
  launchpad/docs/corpus/templates/interface.md`. It prescribes the required
  body sections (Interface description, Operations, Contract and
  stability, Boundary, Relationships, Scope and omissions), states this
  template's `type: interfaces-events` framing, and names `implements:
  corpus-template-interface` as its preferred optional self-link.
- Sibling status confirmed with `git branch --contains` and `git ls-tree -r
  --name-only origin/launchpad -- launchpad/docs/corpus`: the HTTP-count
  sibling (`launchpad/docs/corpus/interfaces/http/count.md`, issue #978,
  id would be `interfaces-http-count`) exists only on the unmerged branch
  `task/978-interfaces-http-count`, not on `origin/launchpad`. The
  WebSocket-count sibling (issue #1020) has no node anywhere in the corpus
  tree yet. `origin/launchpad`'s corpus tree (123 files under
  `launchpad/docs/corpus`) contains zero nodes with `type: interfaces-events`
  today, so this will be the corpus's first merged interface-shaped instance
  node. Per `AGENTS.md`'s relationship rule (resolve against the merge
  target, not the author's own worktree), neither sibling is a valid
  `relationships[].target` — they will be mentioned in prose by filename
  only, never as a typed edge.
- Primary source read directly to ground every planned evidence claim:
  `crates/buzz-relay/src/handlers/count.rs` (the whole file — `handle_count`:
  auth requirement, p-gated/engram/author-only filter checks, channel-access
  narrowing, per-filter fast-path vs. fallback counting, final
  `RelayMessage::count` send), `crates/buzz-relay/src/protocol.rs`
  (`ClientMessage::Count` parse arm lines 108-145 — sub_id/filter validation
  errors; `RelayMessage::count` lines 213-216), `crates/buzz-relay/src/
  connection.rs` (dispatch of `ClientMessage::Count` lines 618-638 —
  semaphore-based rate limiting via `RelayMessage::notice`; `
  enforce_ws_admission` lines 652-669 treats COUNT like REQ for admission),
  `crates/buzz-relay/src/nip11.rs` (`SUPPORTED_NIPS` line 15 — notably does
  **not** list 45 despite COUNT being implemented; `relay_limitation`
  lines 124-139 — `max_filters: 10`, `max_subid_length: 256`, `
  auth_required: true` documented as unconditional for REQ/EVENT/COUNT),
  `crates/buzz-relay/src/handlers/req.rs` (`COUNT_FALLBACK_CANDIDATE_LIMIT
  = 5_000` line 828, `apply_count_fallback_limit`/`count_fallback_exceeded`
  lines 831-840 — the fallback-path row cap that produces the
  `restricted: count filter requires narrower constraints` CLOSED message),
  `crates/buzz-relay/src/router.rs` line 74 (`POST /count` HTTP bridge
  route, for boundary/contrast only) and `crates/buzz-relay/src/api/
  bridge.rs` (`count_events`/`count_events_authed`, NIP-98 auth, for the
  same boundary contrast).

STEP 1 [independent]
Draft `launchpad/docs/corpus/interfaces/nostr/nip-45.md`: front matter
(`id: interfaces-nostr-nip-45`, `type: interfaces-events`, `status: draft`,
`origin: launchpad`, `audiences`, an `evidence` ledger with one commit
citation for this worktree's HEAD plus one entry per substantive claim,
classified honestly, and one `relationships` entry `implements:
corpus-template-interface`) plus a body following the template's required
sections (Interface description, Operations, Contract and stability,
Boundary, Relationships, Scope and omissions), covering every
Definition-of-done bullet from issue #1015: the COUNT message's
inputs/messages (sub_id + filters, `["COUNT", sub_id, filter...]`),
outputs/responses (`["COUNT", sub_id, {"count": N}]`), and
error/rejection behavior (CLOSED with reason strings, invalid-message
parse errors, rate-limit NOTICE); authentication/authorization (NIP-42
auth required, p-gated/engram/author-only/shared-gated/result-gated
channel and kind access enforcement); versioning/compatibility (`
SUPPORTED_NIPS` gap noted as a FACT, not glossed over); ordering/idempotency
(COUNT has no delivery order to guarantee — it returns one aggregate, note
this explicitly rather than leaving the bullet silently unaddressed); a
link to the authoritative NIP-45 text on nostr-protocol/nips; one valid
example (a filter that hits the fast SQL-pushdown count path) and one
failure example (a rejection path, e.g. the fallback-candidate-limit CLOSED
message or an unauthenticated COUNT). Mention the HTTP-count
(`interfaces/http/count.md`, issue #978) and WebSocket-count (issue #1020)
siblings by filename in prose only, per the ALREADY-TRUE finding that
neither resolves as a relationship target on `origin/launchpad` today.
done when: `test -f launchpad/docs/corpus/interfaces/nostr/nip-45.md` exits 0
and the file's front matter parses as valid YAML with `id:
interfaces-nostr-nip-45`.

STEP 2 [needs 1] <- RUNS HERE
Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo
root and fix anything it reports until it exits 0. UNVERIFIED notices are
acceptable; FAIL lines are not, whether from this new node or pre-existing.
done when: the command's exit status is 0 and its output contains no FAIL
line.

STEP 3 [needs 2]
Run, as the sole command in its own tool call,
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
done when: the command's output contains `OK` and its exit status is 0.

STEP 4 [needs 3]
Stage exactly the two files (the new node and this plan) and commit with
`git commit -s -m "docs(corpus): document NIP-45 interface (#1015)"`.
If the commit is rejected for a missing gate stamp, do not create the stamp
and do not pass `--no-verify` — stop and report it as a finding instead.
done when: `git log -1 --name-only` shows a new commit whose file list
includes `launchpad/docs/corpus/interfaces/nostr/nip-45.md` and
`launchpad/plans/2026-09-01-issue-1015-interfaces-nostr-nip-45.md`, OR the
commit was rejected for a gate-stamp reason and that reason is recorded in
the final report.

STEP 5 [needs 4]
Re-read the committed diff against every bullet of issue #1015's own
Definition-of-done checklist, one line at a time, confirming each evidence
entry's cited source was actually opened and that no second hand-authored
canonical corpus document was created.
done when: every DoD bullet has been checked off against the actual diff text
and `python3 launchpad/project-intelligence/corpus/validate.py` still exits 0
when re-run.

PARALLEL

None. This is a single new file with a strictly sequential draft -> validate
-> test -> commit -> review chain; each step's done-when consumes the
artifact the previous step produced, so there is no independent second track
to run alongside it.

GATES

- `validate.py` must exit 0 with no FAIL line before committing (STEP 2).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  must print `OK` before committing (STEP 3), run alone in its own tool call
  per the dispatching instructions.
- The commit must carry `Signed-off-by` (`git commit -s`); if a separate
  pre-commit gate-stamp check rejects the commit, that is reported as a
  finding, never bypassed with `--no-verify`.

BUDGET

One new Markdown file (`launchpad/docs/corpus/interfaces/nostr/nip-45.md`,
expected ~150-250 lines) plus this plan file. No source code, no generated
corpus indexes, no second hand-authored document.

OPEN

- Whether COUNT's absence from `SUPPORTED_NIPS` (line 15 of `nip11.rs`,
  despite `handlers/count.rs` fully implementing it) is an intentional
  omission or a drift bug is a product question outside this task's scope;
  the drafted node reports the fact as a FACT, not a recommendation to fix
  it.

LEFT OUT

- Fixing the `SUPPORTED_NIPS` gap — a runtime change, not documentation, and
  no linked implementation issue authorizes it.
- Documenting the HTTP `/count` bridge endpoint (issue #978) or a future
  WebSocket-count node (issue #1020) as part of this node — each is its own
  task; this node cites `crates/buzz-relay/src/router.rs`/`api/bridge.rs`
  for boundary contrast only, never duplicating their contract.
- Relationships to `interfaces-http-count` or any websocket-count sibling
  id — neither resolves on `origin/launchpad` yet (confirmed by `git
  ls-tree`/`git branch --contains`), so no edge to either is safe to
  declare.
- Broad edits to `node.schema.json`, `relationships.schema.json`, or the
  `corpus-template-interface` template itself.
