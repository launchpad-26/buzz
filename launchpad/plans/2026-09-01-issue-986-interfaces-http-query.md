Issue #986: interfaces/http/query.md — document the relay's POST /query HTTP interface

Stated size: issue body carries no explicit Size line, task instructions cap this plan explicitly at 5 steps -> cap: 5 steps

ALREADY TRUE

- Worktree `__worktrees/task-986-interfaces-http-query` exists, branch
  `task/986-interfaces-http-query` checked out from `origin/launchpad`, HEAD at
  `650354eab8d41ab6ce1a71de079a6c6d95c69052` (`git rev-parse HEAD`).
- `launchpad/docs/corpus/interfaces/http/query.md` does not exist
  (`test -f` returned "does not exist").
- `launchpad/docs/corpus/interfaces/` does not exist as a directory at all yet —
  no sibling HTTP interface node (`events.md`, `count.md`) has merged to
  `origin/launchpad`, confirmed by `find launchpad/docs/corpus -name '*.md'`.
- `node.schema.json`'s `type` enum has 13 members and the single interface-shaped
  value is `interfaces-events` (PRD #602's combined "interfaces/events" surface,
  confirmed in `launchpad/docs/corpus/templates/interface.md`'s own evidence
  ledger, itself a `type: governance` node).
- `launchpad/docs/corpus/templates/interface.md` (id `corpus-template-interface`)
  already exists on `origin/launchpad` with a concrete required-sections skeleton
  (Interface description / Operations / Contract and stability / Boundary /
  Relationships / Scope and omissions) — contradicts the task instruction's
  premise that "no template exists yet"; this plan follows the real template
  found in the repo rather than the stale premise.
- `POST /query` is registered at `crates/buzz-relay/src/router.rs:73` to
  `api::bridge::query_events` (`crates/buzz-relay/src/api/bridge.rs:973`).
  Verified by direct read: NIP-98/X-Pubkey auth (`verify_bridge_auth`), rate
  limiting (`enforce_http_admission`), replay guard (`check_nip98_replay`),
  relay-membership enforcement, then `query_events_authed`
  (`bridge.rs:1040`) which parses a JSON array of NIP-01 filters, applies the
  p-gate (`p_gated_filters_authorized`, `req.rs:1182`), the engram gate, the
  author-only gate, then branches to NIP-50 FTS search
  (`handle_bridge_search`/`buzz-search`'s `query.rs`) or the general
  catch-all filter path, returning `Json(Value::Array(events))` — a bare JSON
  array of full signed Nostr events (not sig-stripped, unlike `buzz-cli`'s
  contract).
- Error envelope is `{"error": "<msg>"}` (`crates/buzz-relay/src/api/mod.rs:21`,
  `api_error`); observed status codes in the read code path: 404 (unmapped
  host), 401 (`UNAUTHORIZED` — auth failures/replay), 429/503 (admission),
  400 (`BAD_REQUEST` — invalid filter JSON, too many channels, mixed
  search/non-search filters, malformed `before_id`), 403 (`FORBIDDEN` —
  p-gate/engram/author-only), 500 (`internal_error`, DB failures).
- `python3 launchpad/project-intelligence/corpus/validate.py` and
  `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  are the two gates this task must pass before commit, per the task's own step 4/5.

STEP 1 [independent] <- RUNS HERE

Create `launchpad/docs/corpus/interfaces/http/query.md`, front matter
`id: interfaces-http-query`, `type: interfaces-events`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, reviewer]`, one `evidence`
entry per substantive claim (commit citation for the recorded revision,
FACT entries citing `router.rs`, `bridge.rs`, `req.rs`, `query.rs`, `mod.rs` line
ranges actually opened this session, INFERENCE entries with `confidence` where
reasoned, TEAM_KNOWLEDGE only if an issue/PR is the sole source). Body follows
`corpus-template-interface`'s required sections (Interface description /
Operations / Contract and stability / Boundary / Relationships / Scope and
omissions) and additionally satisfies every bullet of issue #986's own
Definition-of-done checklist: request/response shape, error/rejection codes,
auth (NIP-98/X-Pubkey), versioning/compatibility (none declared — note as a gap
if true), ordering (`created_at DESC, id ASC` where applicable), a link to
NIP-01 (filters) and NIP-50 (search) as the authoritative spec, one valid
example (a general filter query) and one failure example (mixed search/non-search
-> 400, citing the `bridge_detects_mixed_search_and_non_search_filters` test).
No `relationships` entries targeting ids that do not resolve on `origin/launchpad`
(none of this batch's siblings are merged there); optionally add
`implements: corpus-template-interface` only if that id is confirmed present in
the loaded corpus at HEAD (it is, per ALREADY TRUE, since it's a merged node).

done when: the file exists, front matter is schema-shaped per the above, and no
second hand-authored canonical corpus document was created or edited.

STEP 2 [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo
root. Fix any FAIL line naming the new node (UNVERIFIED notices are acceptable).
If a FAIL is not caused by the new node, stop and report it as a finding rather
than editing around it.

done when: the command exits 0.

STEP 3 [needs 2]

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in its own tool call.

done when: the command's output includes `OK` and its exit code is 0.

STEP 4 [needs 3]

Stage exactly the two files (`launchpad/docs/corpus/interfaces/http/query.md`
and this plan file) and commit with `git commit -s -m "docs(corpus): document HTTP query interface (#986)"`.
If the pre-commit/pre-push gate rejects the commit for a missing stamp, do not
touch any stamp file and do not use `--no-verify` — report it as a finding
instead of routing around it.

done when: `git log -1 --format=%H` on the branch shows a new commit containing
both files, signed off (`git log -1` shows `Signed-off-by`).

STEP 5 [needs 4]

Self-review: re-read the committed diff against issue #986's Definition-of-done
checklist line by line; re-open every cited file/line to confirm each evidence
entry actually supports its claim; confirm no second canonical document was
created; re-run `validate.py` and confirm it still exits 0.

done when: every DoD bullet is checked off against the actual diff, and
`validate.py` exits 0 on the final tree.

PARALLEL

None of steps 1-5 are parallelizable — each needs the previous step's file
state (draft, then validated, then tested, then committed, then reviewed).

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
  (step 2).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  must print `OK` (step 3), run as the sole command in its own tool call per
  the task instructions.
- The repository's commit gate (pre-commit/pre-push hooks) must accept the
  commit in step 4 without `--no-verify`.

BUDGET

One corpus Markdown file (~150-250 lines including front matter) plus this
plan file. No code changes, no second corpus node, no PR.

OPEN

- Whether a versioning/compatibility guarantee is actually documented anywhere
  for `POST /query` (distinct from `buzz-cli`'s own documented exit-code
  contract) is not yet confirmed by this plan — step 1 must state plainly
  if none exists rather than inventing one.
- Whether `implements: corpus-template-interface` is the right optional
  self-link (vs. no relationship at all) is a judgment call left to step 1,
  per the template's own "may declare... optional either way" guidance.

LEFT OUT

- Documenting `POST /events` or `POST /count` (siblings in the same
  `bridge.rs` module) — each is presumably its own corpus task; folding them
  in here would violate "one node is one independently maintainable idea."
- Any change to `router.rs`, `bridge.rs`, or relay behavior — this is a
  documentation-only task; a real product change belongs to a separately
  linked implementation issue.
- Opening a PR or merging — the task instructions explicitly say not to.
