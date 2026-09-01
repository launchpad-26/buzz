# Issue #1223 — corpus doc: operations/runbooks/object-storage-unavailable.md

Stated size: issue #1223 has no `Size` line; batch dispatch brief for Feature #618 caps every task at one document  ->  cap: 5 steps

ALREADY TRUE  (verified against git, not notes)
  `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md`, and
  `launchpad/docs/corpus/templates/runbook.md` are merged on `origin/launchpad`
  (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`).
  `launchpad/docs/corpus/operations/runbooks/object-storage-unavailable.md` does not exist
  yet (no `operations/` tree under `launchpad/docs/corpus` at all). `architecture-containers-object-storage`
  (`launchpad/docs/corpus/architecture/containers/object-storage.md`) is already merged and
  describes the container this runbook responds to failures in. Sibling issue #1218
  (`operations/reliability/object-storage-failure.md`) is OPEN/unmerged (`gh issue view 1218`)
  — its node id does not exist on `origin/launchpad`, so it cannot be a relationship target
  and its analysis is not restated here.

STEP 1  gather evidence: buzz-media, git-on-object-storage, readiness/startup, env/deploy  [independent]
        done when: notes exist naming, for each claim the body will make, the exact file
        (and function where relevant) opened to support it. Files: `crates/buzz-media/src/{storage,error,config}.rs`;
        `crates/buzz-relay/src/api/git/{store,transport,hydrate,cas_publish}.rs`;
        `crates/buzz-relay/src/router.rs` (`/_readiness`); `crates/buzz-relay/src/main.rs`
        (git conformance-probe startup gate); `crates/buzz-relay/src/storage_sweep.rs`
        (`buzz_storage_sweep_ok`); `.env.example`; `docker-compose.yml`;
        `deploy/charts/buzz/README.md`; `docs/git-on-object-storage.md`.

STEP 2  write the node's front matter and body                                    [needs 1]
        done when: `launchpad/docs/corpus/operations/runbooks/object-storage-unavailable.md`
        exists with id `operations-runbooks-object-storage-unavailable`, type `operations`,
        status `draft`, origin `launchpad`, audiences `operator`+`developer`+`reviewer`, one
        `implements` relationship to `corpus-template-runbook`, one evidence entry per
        substantive claim, and a body carrying every one of the template's required
        sections (Trigger, Severity and impact, Diagnosis, Mitigation and resolution,
        Escalation, Scope and omissions) under its own heading with real content — naming
        the boundary with sibling #1218 in prose only, no link to its unmerged path.

STEP 3  validate                                                                   [needs 2]
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.

STEP 4  earn the commit-gate stamp                                    [needs 3]  ← RUNS HERE
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
        -p "test_*.py"`, run as the sole command in its own Bash call (no pipe, no chained
        `cd`), prints `OK`.

STEP 5  commit locally only                                                        [needs 4]
        done when: `git log -1 --format=%H` on branch
        `task/1223-runbooks-object-storage-unavailable` names a new signed-off commit
        containing exactly the doc and this plan file, `git status` is clean, and no push
        or PR was made.

PARALLEL: none — one hand-authored file plus this plan file, one worktree, no code
changes; steps are strictly sequential (each needs the previous).

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 (STEP 3).
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
must print `OK`, run alone, before the commit (STEP 4). review-adjudicate and cross-model
final review are deferred to the batch owner, not run in this worktree.

BUDGET: STEP 1 (evidence-gathering across ~10 source files spanning buzz-media, the
git-on-object-storage path, readiness, startup, and deploy docs) is the step most likely
to eat the budget; STEP 2's writing is bounded once STEP 1's notes exist.

OPEN: whether a `references` edge to `architecture-containers-object-storage` (already
merged) belongs on this node, beyond the mandatory `implements` edge to
`corpus-template-runbook`, is a judgement call for STEP 2, not pre-decided here — the
template's own precedent (and every batch-mate's) is to add cross-corpus edges in a
later pass once more siblings land, which this node may or may not follow.

LEFT OUT: no relationship to sibling issue #1218's node — it does not exist on
`origin/launchpad` yet, and even in prose this document does not restate its
failure-mode analysis, only names the boundary. No changes to generated corpus indexes
(none exist to regenerate). No changes to `buzz-media`, `buzz-relay`, or any other
crate — this is documentation only; any code gap discovered while writing (e.g. an
unused connectivity-probe method, or a readiness endpoint that does not cover object
storage) is recorded as a diagnosis/scope note, not fixed here.
