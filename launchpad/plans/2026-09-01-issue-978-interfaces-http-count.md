Issue #978: document interfaces/http/count.md
Stated size: small (single-document corpus task, dispatching instructions cap it explicitly)  ->  cap: 5 steps

ALREADY TRUE

- Worktree `__worktrees/task-978-interfaces-http-count` created off
  `origin/launchpad` on branch `task/978-interfaces-http-count`, HEAD at
  `650354eab8d41ab6ce1a71de079a6c6d95c69052`.
- Issue #978's body read via `gh issue view`. Target file:
  `launchpad/docs/corpus/interfaces/http/count.md`. Confirmed via `test -f`
  that this path does not exist yet — nothing to update, this is a create.
- `launchpad/docs/corpus/AGENTS.md` and `launchpad/docs/corpus/schema/node.schema.json`
  read. `type` enum has 13 members; the correct value for an interface-shaped
  node is `interfaces-events` (PRD #602 combines interface and event-kind
  surfaces into one enum member).
- `launchpad/docs/corpus/templates/interface.md` (id `corpus-template-interface`,
  already merged to `origin/launchpad`) found and read in full. It prescribes
  required sections (Interface description, Operations, Contract and
  stability, Boundary, Relationships, Scope and omissions) and states this
  will be the corpus's first interface-shaped instance node. It also names
  `implements: corpus-template-interface` as the template's own preferred
  optional self-link now that it is merged.
- `crates/buzz-relay/src/router.rs`, `crates/buzz-relay/src/api/bridge.rs`
  (`count_events`, `count_events_authed`, `verify_bridge_auth`,
  `check_nip98_replay`, `enforce_http_admission`, `api_error`/`internal_error`),
  `crates/buzz-relay/src/handlers/req.rs` (`p_gated_filters_authorized` and
  neighbors), `crates/buzz-relay/src/handlers/count.rs` (the WS NIP-45 COUNT
  sibling, for contrast only), `crates/buzz-relay/src/protocol.rs`
  (`RelayMessage::count`), `crates/buzz-core/src/kind.rs` (`P_GATED_KINDS`,
  `KIND_GIFT_WRAP = 1059`) and `crates/buzz-cli/src/client.rs` (`count()`,
  currently `#[allow(dead_code)]`, not wired to a subcommand) have all been
  read directly to ground every planned evidence claim.
- `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` run;
  118 nodes exist there today, including `architecture-containers-cli`
  (already merged, mentions `/count` in its own evidence ledger) and
  `corpus-template-interface`. No other HTTP-interface sibling node
  (`/query`, `/events`) exists on `origin/launchpad` yet, matching the task's
  warning not to relate to unmerged siblings.

STEP 1 [independent]
Draft `launchpad/docs/corpus/interfaces/http/count.md`: front matter
(`id: interfaces-http-count`, `type: interfaces-events`, `status: draft`,
`origin: launchpad`, `audiences`, `evidence` ledger, one `relationships` entry
`implements: corpus-template-interface`) plus a body following the template's
required sections (Interface description, Operations, Contract and
stability, Boundary, Relationships, Scope and omissions), covering every
Definition-of-done bullet from issue #978: inputs/messages, outputs/responses,
error/rejection behavior, auth/authorization, versioning/compatibility,
ordering/idempotency, the NIP-45 spec link, one valid and one failing example.
done when: `test -f launchpad/docs/corpus/interfaces/http/count.md` exits 0
and the file's front matter parses as valid YAML with `id: interfaces-http-count`.

STEP 2 [needs 1] <- RUNS HERE
Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo
root and fix anything it reports until it exits 0. UNVERIFIED notices are
acceptable; FAIL lines are not, whether from this new node or pre-existing.
done when: the command's exit status is 0 and its output contains no FAIL line.

STEP 3 [needs 2]
Run, as the sole command in its own tool call,
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
done when: the command's output contains `OK` and its exit status is 0.

STEP 4 [needs 3]
Stage exactly the two files (the new node and this plan) and commit with
`git commit -s -m "docs(corpus): document HTTP count interface (#978)"`.
If the commit is rejected for a missing gate stamp, do not create the stamp
and do not pass `--no-verify` — stop and report it as a finding instead.
done when: `git log -1 --name-only` shows a new commit whose file list
includes `launchpad/docs/corpus/interfaces/http/count.md` and
`launchpad/plans/2026-09-01-issue-978-interfaces-http-count.md`, OR the
commit was rejected for a gate-stamp reason and that reason is recorded in
the final report.

STEP 5 [needs 4]
Re-read the committed diff against every bullet of issue #978's own
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

One new Markdown file (`launchpad/docs/corpus/interfaces/http/count.md`,
expected ~150-250 lines) plus this plan file. No source code, no generated
corpus indexes, no second hand-authored document.

OPEN

- Whether `buzz-cli`'s `count()` method (currently `#[allow(dead_code)]`, not
  wired to any subcommand) should ever get a CLI subcommand is a product
  decision outside this task's scope; the drafted node reports the fact,
  not a recommendation.

LEFT OUT

- Wiring `buzz-cli`'s dead-code `count()` method to a subcommand — a runtime
  change, not documentation, and no linked implementation issue authorizes it.
- Documenting the WS NIP-45 COUNT handler (`handlers/count.rs`) as its own
  node — out of scope for this task; it is cited for contrast/shared-logic
  context only, not duplicated.
- Relationships to `/query` or `/events` HTTP interface siblings — none of
  those nodes exist on `origin/launchpad` yet (confirmed by `git ls-tree`),
  so no edge to them is safe to declare.
- Broad edits to `node.schema.json`, `relationships.schema.json`, or the
  `corpus-template-interface` template itself.
