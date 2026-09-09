# Issue #977 — corpus node: interfaces/http/admin.md

Stated size: no Size field on this task-template issue; the dispatching task brief caps this single-document corpus task at 5 steps -> cap: 5 steps

ALREADY TRUE: Worktree `__worktrees/task-977-interfaces-http-admin` exists on branch
`task/977-interfaces-http-admin`, based on `origin/launchpad` at commit
`650354eab8d41ab6ce1a71de079a6c6d95c69052`.
`launchpad/docs/corpus/interfaces/http/admin.md` does not exist yet (verified with
`test -f`). `node.schema.json`'s `type` enum has no value named `interface`; the
applicable value for an interface-shaped node is the combined `interfaces-events`
member (confirmed in `node.schema.json`, corroborated by
`launchpad/docs/corpus/standards/taxonomy.md:139` and
`launchpad/docs/corpus/templates/interface.md`'s own "A note on `type`" section).
`launchpad/docs/corpus/templates/interface.md` (id `corpus-template-interface`,
status `active`) already exists on `origin/launchpad` and is the template this
node's shape follows (Interface description, Operations, Contract and stability,
Boundary, Relationships, Scope and omissions) — the task brief's instruction to
treat `AGENTS.md`/`node.schema.json` as the only guidance because "no template
exists yet" is stale against the actual checked-out `origin/launchpad` tree, and
`AGENTS.md` itself says a corpus standard wins over conflicting prose when the two
disagree. The admin HTTP surface is
`crates/buzz-relay/src/api/admin/{mod.rs,auth.rs,error.rs}`, mounted only when
`config.admin.is_some()` (`BUZZ_ADMIN_HOST` configured), nested at `/api/admin/v1`
in `crates/buzz-relay/src/router.rs`. It is a private deployment-moderation API —
distinct from `crates/buzz-admin` (an offline Nostr membership-list CLI, unrelated)
and from `crates/buzz-relay/src/api/operator.rs` (community-provisioning routes for
a different "operator" concept). Sibling interface nodes for
count/events/git/health/hooks/invites/media/operator/query (issues #978-986) are
not merged to `origin/launchpad`, so no relationship may target them yet. Confirmed
present on `origin/launchpad` and relevant as relationship targets:
`architecture-containers-relay` (the relay container this interface is a
constituent piece of) and `architecture-principles-fail-closed-boundaries` (the
admin API's own deny-by-default design — no fall-through role, replay guard fails
closed on Redis error, config-backed pubkeys immutable, last-operator invariant —
is a direct instance of that principle).
`architecture-principles-host-selects-community` was considered and rejected as a
target: its subject is per-community tenant binding via `bind_community`, a
different mechanism from the admin API's single fixed-host gate (`is_admin_host`),
and citing it would overstate the connection.

STEP 1 [independent] Draft `launchpad/docs/corpus/interfaces/http/admin.md`
following `corpus-template-interface`'s required sections, satisfying every
Definition-of-done bullet in issue #977: front matter (`id:
interfaces-http-admin`, `type: interfaces-events`, `status: draft`, `origin:
launchpad`, `audiences`, `evidence`), inputs/outputs/errors, authentication and
authorization (NIP-98 kind:27235, Host/Origin checks, Operator vs Moderator role
resolution, disabled-mode read-only fallback), versioning (the `/api/admin/v1`
path segment), ordering/idempotency (`request_id` on reopen/enforcement actions,
`action_id` CAS fencing on cancel), and at least one valid and one failure example.
Cite only source paths/symbols actually opened during research
(`crates/buzz-relay/src/api/admin/mod.rs`, `auth.rs`, `error.rs`,
`crates/buzz-relay/src/config.rs`, `crates/buzz-relay/src/router.rs`,
`crates/buzz-relay/src/nip11.rs`). RUNS HERE.
done when: the file exists, its front matter parses as valid YAML with all seven
schema-legal keys populated correctly, and every DoD bullet above has a
corresponding section in the body.

STEP 2 [needs 1] Run `python3 launchpad/project-intelligence/corpus/validate.py`
from the repo root. Fix any `FAIL` line named against the new node (or any
pre-existing `FAIL`, since the task brief states the prior #1951 baseline has been
resolved and none should remain) and re-run until clean.
done when: the command exits 0 with no `FAIL` lines (`UNVERIFIED` notices are
acceptable).

STEP 3 [needs 2] Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"`.
done when: the command's output includes the literal marker `OK` with zero
failures or errors reported.

STEP 4 [needs 3] In a separate tool call, stage exactly
`launchpad/docs/corpus/interfaces/http/admin.md` and this plan file, then run
`git commit -s -m "docs(corpus): document HTTP admin interface (#977)"`. If the
commit is rejected for a missing gate stamp, do not touch any stamp file and do
not use `--no-verify` — report it as a blocker instead.
done when: `git log -1` shows the new commit with a `Signed-off-by` trailer, on
branch `task/977-interfaces-http-admin`.

STEP 5 [needs 4] Re-read the committed diff against issue #977's
Definition-of-done line by line; re-open every cited source to confirm each
evidence entry actually supports its claim; confirm no second hand-authored
canonical corpus document was created; re-run `validate.py` to confirm it still
exits 0.
done when: every DoD bullet is checked off against the actual diff and
`validate.py` exits 0 on the final tree.

PARALLEL: none — single-document task, five strictly sequential steps, nothing to
run concurrently.

GATES: `launchpad/project-intelligence/corpus/validate.py` must exit 0 (Step 2,
re-checked Step 5). `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print `OK` (Step
3), run alone in its own tool call per the task brief. The repository's commit gate
(`Signed-off-by` trailer via `git commit -s`, plus whatever local gate stamp the
commit hook checks) must pass without `--no-verify`.

BUDGET: one corpus node (~150-250 lines of Markdown) plus this plan file. No code
changes, no dependency changes, no other files touched.

OPEN: Whether `is_admin_host`'s single-fixed-host gate deserves its own corpus
principle node distinct from `architecture-principles-host-selects-community` is
not this task's call — noted as a gap in the new node's Scope and omissions rather
than resolved here. Whether NIP-98 kind:27235 itself gets a future
`interfaces-events` (event-kind-template) sibling node is out of scope; this node
cites the NIP and the verifying code rather than re-describing the event shape.

LEFT OUT: Documenting `crates/buzz-admin` (the offline Nostr membership CLI) —
different subject, no HTTP surface, would violate one-idea-per-node. Documenting
`crates/buzz-relay/src/api/operator.rs` (community provisioning/archive/transfer
routes) — a different "operator" concept (deployment operator managing multiple
communities, not the admin-moderation API's Operator/Moderator roles); a separate
corpus task if one does not already exist. Field-by-field parameter cataloguing
for every request/response DTO — the template's own Boundary section excludes
domain-expert-depth API-reference cataloguing (`#1346`/`#1532`); this node points
at the code symbols instead of restating them. Relationships to the nine sibling
HTTP interface nodes (#978-986) — none are merged to `origin/launchpad` yet.
