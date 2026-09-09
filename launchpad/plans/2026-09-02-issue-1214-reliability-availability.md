Issue #1214 — task: document operations/reliability/availability.md
Stated size: none stated  →  cap: 5 steps (set by the batch dispatch brief for Feature
#618: one hand-authored reference document per issue, against conventions already
settled by earlier corpus batches, not the first node in the corpus)

Target file: `launchpad/docs/corpus/operations/reliability/availability.md`
Node id: `operations-reliability-availability` (assigned by the issue brief; permanent)
Base branch: `origin/launchpad`

ALREADY TRUE  (verified against git at 473205a7457b208455f188847bfb27b01aa83cac, not notes)
  Worktree `/home/serina/Launchpad/buzz/__worktrees/task-1214-reliability-availability`
    exists on branch `task/1214-reliability-availability`, tracking `origin/launchpad`,
    working tree clean.
  `test -e launchpad/docs/corpus/operations/reliability/availability.md` fails — the
    target file does not exist yet, and no `operations/` directory exists anywhere
    under `launchpad/docs/corpus/` yet either.
  `launchpad/docs/corpus/templates/reference.md` (id `corpus-template-reference`) is
    merged and is this task's assigned template.
  Seven already-merged nodes cover most of the underlying mechanism this reference
    synthesizes: `architecture-deployment-kubernetes`,
    `architecture-deployment-single-relay`, `architecture-deployment-multi-relay`,
    `layers-observability-readiness`, `layers-observability-liveness`,
    `layers-observability-health-checks`, `layers-lifecycle-graceful-shutdown`.
  Five sibling `operations/reliability/*` tasks (database-failure #1215,
    disaster-recovery #1216, graceful-shutdown #1217, object-storage-failure #1218,
    redis-failure #1219) are being authored in parallel in this same batch; none of
    their node ids exist on `origin/launchpad` yet.
  `node.schema.json` requires id, type, status, origin, audiences, evidence; permits
    `relationships`; `additionalProperties: false` rejects everything else.

STEP 1  Read the issue DoD and the governing corpus documents          [independent]
        Read issue #1214's Definition of Done via `gh issue view`, then
        `launchpad/docs/corpus/AGENTS.md`, `launchpad/docs/corpus/templates/reference.md`,
        `launchpad/docs/corpus/schema/node.schema.json`, and the linking/naming/
        code-references standards, to fix the required sections and evidence rules
        before drafting.
        done when: the template's Required Sections list and the issue's DoD bullets
                   are both enumerated, and the seven relationship targets above are
                   confirmed present in `<SCRATCH>/existing-node-ids.txt`.

STEP 2  Gather evidence by opening primary sources                     [needs 1]
        Open (not grep-only) the seven merged corpus nodes above, the Helm chart's
        replica/HA templates and README (`deploy/charts/buzz/README.md`,
        `templates/_helpers.tpl`, `templates/service.yaml`), `crates/buzz-relay/src/config.rs`,
        `crates/buzz-relay-mesh/src/registry.rs`, and `docs/multi-tenant-relay.md`'s
        Conformance section (the NIP-98 replay/sticky-routing tension). Record which
        claims are already covered by a merged node (link, do not restate) versus
        which are new findings sourced directly from code/chart/docs.
        done when: every planned evidence-ledger claim has a source that was actually
                   opened, and the boundary against the five unmerged siblings is
                   drawn in prose only.

STEP 3  Write the node                                        [needs 2]  ← RUNS HERE
        Write `launchpad/docs/corpus/operations/reliability/availability.md` following
        `reference.md`'s Required Sections: a reference-description paragraph, a
        structured-entries table ordered by concern (replica topology → probes →
        dependency coupling → rolling update/shutdown → mesh/session → SLO), a
        Boundary statement naming the concept/how-to/API-Reference exclusions plus the
        five unmerged siblings, Relationships (references only, to the seven merged
        nodes), and Scope and omissions naming both what is excluded and what could
        not be verified (including a repository-wide search confirming no availability
        SLO/SLA exists).
        done when: the file exists with schema-valid front matter and every table row
                   in the body has a matching `evidence` entry in the ledger.

STEP 4  Validate and check the plan                                    [needs 3]
        Run `python3 launchpad/project-intelligence/corpus/validate.py` (expect exit 0,
        only non-fatal `UNVERIFIED` notices for the commit-only provenance entry and
        one tool-result search citation) and re-run
        `bash /home/serina/.claude/skills/plan-issue/check-plan.sh launchpad/plans/2026-09-02-issue-1214-reliability-availability.md`,
        fixing anything either reports.
        done when: `validate.py` exits 0 and the plan checker's mechanical checks are
                   clean.

STEP 5  Earn the commit gate and commit                                [needs 4]
        Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        as the sole command in its own Bash call (not piped, not chained with a `cd`
        in the same call), confirm `OK`, then in a separate call
        `git add -A && git commit -s -m "docs(corpus): document operations/reliability/availability reference (#1214)"`.
        done when: the commit exists locally with `-s` (DCO), and the verify-gate stamp
                   is accepted (or, if refused, reported as a finding rather than
                   routed around).

PARALLEL  None. All five steps edit the same document (plus this plan file), and the
          skill's own rule is that steps touching one file are sequential regardless
          of how unrelated they look. The issue's Definition of Done caps this task at
          exactly one hand-authored document.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
          `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
          must report `OK`, run alone in its own Bash call so the verify-gate stamp
          resolves correctly. The repository-wide file-size gate (1000 lines) must
          pass — this document is far under that at roughly 265 lines.

BUDGET    STEP 2 and STEP 3 together. Most of the underlying mechanism is already
          documented by seven merged sibling nodes; the work is in synthesizing a
          cross-cutting availability view that links rather than restates them, while
          still sourcing the genuinely new claims (the mesh ready-registry semantics,
          the absent Service session affinity, the NIP-98 sticky-routing conformance
          gap, and the absence of any availability SLO) from primary sources actually
          opened rather than from the merged nodes' own summaries.

OPEN      Whether a future `operations/reliability` overview or index node should
          declare `part-of` toward this one, once more siblings merge. Not decided
          here; left for a later pass per this corpus's own "declared once the set has
          landed" convention.

LEFT OUT  Any `relationships` edge to the five unmerged `operations/reliability/*`
          siblings (database-failure, disaster-recovery, graceful-shutdown,
          object-storage-failure, redis-failure). Named in prose only, per the batch
          dispatch brief's explicit instruction not to declare relationships to
          unmerged siblings — an id that resolves only in this worktree would become a
          hard CI failure the moment this node merges ahead of them.

          Per-dependency failure-mode narrative (what a request does when Postgres,
          Redis, or object storage specifically degrades mid-operation). That is the
          unmerged siblings' subject, not this cross-cutting node's.

          Disaster-recovery procedure and an operations-facing graceful-shutdown
          runbook. Same reason — separate, not-yet-merged sibling tasks in this batch.
