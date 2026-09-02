# Issue #644 — agents/corpus-usage.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md`
(id `corpus-agents`), and sibling `launchpad/docs/corpus/agents/invariants.md` (id
`agents-invariants`) are merged on `origin/launchpad`. `launchpad/docs/corpus/templates/procedure.md`
(id `corpus-template-procedure`) and `launchpad/docs/corpus/templates/reference.md`
(id `corpus-template-reference`) are merged there too — both confirmed by `git show
origin/launchpad:launchpad/docs/corpus/templates/<file>.md`. `launchpad/docs/corpus/agents/corpus-usage.md`
does not exist yet (confirmed by `test -f`). None of the other 30 sibling `agents/*.md` /
`ingestion/*.md` tasks under Feature #620 are merged — `git ls-tree -r --name-only
origin/launchpad -- launchpad/docs/corpus` lists only `AGENTS.md`, `README.md`,
`agents/invariants.md`, `architecture/**`, `schema/**` (excluded from validation),
`standards/*.md`, `templates/*.md` — so no sibling task is a valid `relationships` target.
Sibling #650 (`agents/repository-navigation.md`) is unbuilt; only its title is known.

STEP 1  Gather evidence: re-read `AGENTS.md`'s "Creating a node" step 2 (check nothing
already covers it) and its own note that "There was nothing to point at" is a false
justification once a second node exists; read `templates/procedure.md` in full (already
done) for required sections, industry model (Diátaxis how-to + Good Docs Project), and its
explicit boundary against reference/runbook/tutorial/concept. Actually exercise RepoQL's
`explore`, `query`, and `read` tools against `launchpad/docs/corpus/**` in this same session
to record what each verb really does with this corpus (ranking, headings, glob/SELECT over
corpus files, the separate `concept:///` repo-memory scheme backed by `.repoql/concepts/**`)
— including any tool failure encountered, cited honestly rather than assumed working. ← RUNS HERE

STEP 2  [needs 1] Write front matter (schema-valid: id `agents-corpus-usage`, type `agent`
— same reasoning as `agents-invariants`: this node's subject is the same corpus surface
`AGENTS.md` itself documents, not the `standards/`/`templates/` governance family; status
`draft`; origin `launchpad`; audiences `[agent, developer, reviewer]`; relationships
`references: corpus-agents`, `implements: corpus-template-procedure` — both resolve on
`origin/launchpad`) and the body as a `templates/procedure.md`-shaped how-to: Overview:
finding whether a subject is covered and traversing a question to a node's cited
implementation/verification evidence, as the reader-facing complement to `AGENTS.md`'s
step-2 authoring instruction, not a restatement of it. Task 1: search-before-create steps
(enumerate the real tree, check id/title overlap, when to conclude "update" vs "create").
Task 2: question-to-node-to-evidence traversal (locate a candidate node, read its evidence
ledger, open every cited source, follow `relationships`). A short tools note (not a full
reference table) on what `explore`/`query`/`read` actually did in STEP 1, and the
`concept:///` vs corpus-node distinction, cited to the real tool calls and to
`.repoql/concepts/README.md`. Boundary section naming: not repository/codebase navigation
(#650's title, distinguished explicitly since its content is unread), not authoring/
updating/retiring (`AGENTS.md`), not the invariants list (`agents-invariants`), not a
reference-shaped tool catalog (no such node exists in this Feature; keep it proportionate
and cite the primary docs instead of cataloguing every RepoQL verb).

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and
re-run until exit 0.

STEP 4  [needs 3] Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
-p "test_*.py"` as the sole command to earn the verification stamp, confirm `OK`, then
commit in a separate call. Self-review the diff against the issue's DoD line by line (no
`review-code`/`check-plan.sh` found in this worktree — see OPEN). No push, no PR.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. The
unittest discovery command must print `OK` before the commit. `review-adjudicate` and the
cross-model final review pass are deferred to the batch owner's later review, per the
sibling #698 plan's own precedent — not run here.

BUDGET: small — one document, no code changes. Evidence gathering scoped to `AGENTS.md`,
`templates/procedure.md`, `templates/reference.md`, `templates/runbook.md` (to rule it
out), `agents/invariants.md`, the real `origin/launchpad` corpus tree listing, Feature
#620's and issue #644's live bodies, sibling issue titles (#640-#643, #645-#648, #650-#651)
for boundary-drawing, and a handful of live RepoQL tool calls against this repo.

OPEN: No `.claude/skills/plan-issue/check-plan.sh` (or any `check-plan*` file) exists
anywhere in this worktree or the main checkout — proceeding without it, per the task
brief's own fallback instruction, and reporting this in the final summary. RepoQL's `read`
and `query`'s `search()` function returned a fatal "database was invalidated by an earlier
fatal failure" error partway through STEP 1's tool testing, after `explore` and a plain
`SELECT ... FROM glob_files(...)` had already succeeded in the same session — this is
reported in the node as an honestly-timestamped observation (a tool result citation, the
same shape `corpus-agents.md`'s own ledger uses for `git_diff_name_only(...)`), not
smoothed over or silently retried past, and no `host restart` is issued from this task since
that is a shared side-effect outside this document's scope. The DoD tail on issue #644 is
runbook/how-to-shaped boilerplate ("states goal, prerequisites...", "success verification
and rollback/cleanup") rather than the policy-shaped boilerplate seen on `#649`/`#1345`/
`#1346` — read against Feature #620's real acceptance criteria per the task brief, not
followed as a literal checklist, since this subject is chosen-schedule usage guidance, not
an alert-triggered response (ruling out `templates/runbook.md`).

STEP 3 findings: `validate.py` initially FAILed on two citations — a bare-path citation to
`.repoql/concepts/README.md` (that directory is excluded by a global gitignore rule,
`**/.repoql/`, confirmed via `git check-ignore`, so it is absent from this fresh worktree
and cannot resolve as a repo-relative path; reclassified as a `read(...) -> ...`
tool-result-shaped citation instead, and the gitignore fact itself became a stronger,
independently-cited claim in the node), and a `https://github.com/.../issues/650`-style
citation malformed as a bare title string with no recognized shape (reformatted as the
real issue URL, which lands `UNVERIFIED` — the correct outcome per `AGENTS.md`'s own
stated handling for an issue-only source). Both fixed; `validate.py` now exits 0 with 604
non-fatal `UNVERIFIED` notices corpus-wide, none newly introduced by this node beyond the
expected ones (commit citations, tool-result citations, external URLs).

LEFT OUT: No relationships to any unmerged sibling `agents/*.md` or `ingestion/*.md` node
(none exist on `origin/launchpad` yet) — including no edge to `#650`
(`agents/repository-navigation.md`), whose content cannot be read and whose title alone is
used only to draw this node's boundary statement, not to infer or duplicate its scope. No
attempt to build a full reference-style catalog of every RepoQL tool or every `read`
modifier — that would drift into `templates/reference.md`'s territory per `procedure.md`'s
own boundary, and no such reference node is a task in this Feature. No fix to the RepoQL
host's fatal DB state — reported, not resolved, here.
