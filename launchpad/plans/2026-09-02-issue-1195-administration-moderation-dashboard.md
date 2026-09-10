Issue #1195 — document operations/administration/moderation-dashboard.md

ALREADY TRUE

- The worktree and branch already exist: `/home/serina/Launchpad/buzz/__worktrees/task-1195-administration-moderation-dashboard`
  on `task/1195-administration-moderation-dashboard`, based on `origin/launchpad`
  at commit `473205a7457b208455f188847bfb27b01aa83cac` (`git rev-parse HEAD`).
- The target file `launchpad/docs/corpus/operations/administration/moderation-dashboard.md`
  did not exist before this work — confirmed by `ls launchpad/docs/corpus/operations`
  reporting "No such file or directory" prior to creating the directory.
- `launchpad/docs/corpus/templates/procedure.md` (`corpus-template-procedure`) is
  merged on `origin/launchpad` and is the assigned template.
- `capabilities-moderation-operator-dashboard`, `capabilities-moderation-moderation`,
  `capabilities-moderation-moderation-command` and `architecture-context-relay-operator`
  are merged on `origin/launchpad` (confirmed against
  `<SCRATCH>/existing-node-ids.txt`), so relationships to them are legal.
- No corpus node of `type: operations` exists on `origin/launchpad` yet — this is
  the first, and the first node authored from `corpus-template-procedure`.

Stated size: not stated in issue #1195 -> cap: 5 steps (per the dispatch brief: one hand-authored document, 5-step maximum)

STEP 1 [independent]
Gather evidence before drafting: record `git rev-parse HEAD`; open the CLI
(`crates/buzz-cli/src/lib.rs`, `crates/buzz-cli/src/commands/moderation.rs`,
`messages.rs`, `channels.rs`), the desktop UI
(`ModerationQueueCard.tsx`, `SettingsPanels.tsx`, `moderationQueue.ts`,
`shared/api/moderation.ts`), the relay (`moderation_authz.rs`,
`moderation_commands.rs`, `api/bridge.rs`, `router.rs`), the schema
(`migrations/0006_moderation.sql`), the kind registry (`buzz-core/src/kind.rs`),
the relay-operator's own CLI (`buzz-admin/src/main.rs`), and
`VISION_MODERATION.md`; confirm by targeted search that no mobile moderation
surface and no moderation subcommand in `buzz-admin` exist.
done when: every citation later used in the drafted node's evidence ledger
names a file actually opened during this step, and the commit SHA above is
recorded as the provenance entry.

STEP 2 [needs 1]
Draft `launchpad/docs/corpus/operations/administration/moderation-dashboard.md`
front matter and body against `corpus/templates/procedure.md`'s required
sections, using only evidence gathered in STEP 1 — including the
operationally significant finding that a 9044 resolve call does not itself
enforce a ban/timeout/delete/kick, so a CLI operator must issue the paired
enforcement command separately (the desktop UI automates this ordering).
done when: the file exists at the assigned path with schema-legal front
matter (`id: operations-administration-moderation-dashboard`,
`type: operations`, `status: draft`, `origin: launchpad`) and a body
containing Overview, Before you start, at least one numbered task sequence,
See also, Boundary, Relationships, and Scope and omissions sections.

STEP 3 [needs 2]
Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
repository root and fix any reported error, re-running until clean.
done when: the command's exit status is 0.

STEP 4 [needs 3] <- RUNS HERE
Run the corpus test suite
(`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`)
as the sole command in its own Bash call, confirm `OK`, then in a separate
tool call commit with
`git add -A && git commit -s -m "docs(corpus): document the moderation dashboard operating procedure (#1195)"`.
done when: the test suite reports `OK` and `git log -1` on the branch shows a
new commit carrying a `Signed-off-by` trailer that touches only the new
corpus document and this plan file.

STEP 5 [needs 4]
Self-review the diff against issue #1195's Definition of Done, bullet by
bullet, and produce the final report in the shape the dispatch brief's
section 8 specifies (issue number, branch, worktree, commit SHA, file
path/line count, DoD bullets satisfied/not, anything expected but
unverifiable, any second concept discovered).
done when: every DoD bullet is checked against a concrete section of the
drafted body and the report has been produced in that exact shape.

PARALLEL

None. This is a single hand-authored document with no independent work
streams — each step depends on the previous step's output existing on disk,
and only one document is being produced.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
  before committing (STEP 3).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  must report `OK`, run as the sole command in its own Bash call, before
  committing (STEP 4).
- The commit must carry `-s` (DCO); `--no-verify` is never used, and if the
  verify gate refuses for any other reason that is reported, not routed
  around.

BUDGET

One hand-authored corpus document (~330 lines) plus this plan file. No code
changes, no other corpus files touched, no second corpus document.

OPEN

- Whether a broader `operations`-typed parent node should eventually declare
  a `part-of` edge back to this one — deferred; no such node exists on
  `origin/launchpad` at the recorded revision.
- Whether `buzz-agent` or another automated harness in this repository
  invokes `buzz moderation` commands programmatically on its own judgment —
  not checked; named as a gap in the drafted node's Scope and omissions
  rather than assumed either way.

LEFT OUT

- Re-deriving the moderation capability's authorization matrix, wire
  contract, or maturity narrative — already owned by the merged
  `capabilities-moderation-*` nodes and linked from this node, not restated.
- Executing these exact CLI/desktop steps against a live relay and Postgres
  instance — named honestly as unverified in the drafted node's Scope and
  omissions rather than silently assumed as tested.
- A second hand-authored corpus document. None was discovered mid-draft that
  warranted its own task; if the desktop app later adds a one-click timeout
  resolution, that is a future edit to this same node, not a new one.
