Issue #1216 — task: document operations/reliability/disaster-recovery.md
Stated size: no `Size` line  →  cap: 5 steps (set by the Feature #618 batch dispatch brief)

ALREADY TRUE  (verified against git and the repository, not notes)
  Worktree `__worktrees/task-1216-reliability-disaster-recovery` is on branch
    `task/1216-reliability-disaster-recovery`, based on `origin/launchpad`,
    HEAD `473205a7457b208455f188847bfb27b01aa83cac`, working tree clean.
  `launchpad/docs/corpus/operations/` does not exist on this branch at all — confirmed
    with `ls`, exit 2. This is (at minimum) among the first `operations`-typed nodes in
    the corpus; no sibling `operations/reliability/*` file exists to conflict or update.
  `launchpad/docs/corpus/operations/reliability/disaster-recovery.md` does not exist
    (confirmed the same way) — this is a create, not an update.
  204 node ids resolve on `origin/launchpad` per `<SCRATCH>/existing-node-ids.txt`; none
    is `operations`-typed and none lives under `operations/`.
  `launchpad/docs/corpus/templates/reference.md` (id `corpus-template-reference`) is
    merged and is this task's assigned template — three required content sections
    (Reference description / Structured entries / optional Commands) plus Boundary,
    Relationships, and Scope-and-omissions.
  Read and confirmed by opening the source, not by trusting a prior agent's summary:
    - `deploy/compose/run.sh`'s `backup_hint()` function (lines 38-51) only `cat`s a
      checklist to stdout; it calls no backup command (no `pg_dump`, no `mc mirror`, no
      snapshot API). No other script under `deploy/`, `scripts/`, or `crates/buzz-admin`
      performs a backup or restore action — `buzz-admin` has no such subcommand.
    - `deploy/charts/buzz/templates/NOTES.txt` prints the identical five-item "Backups —
      save these" checklist (relay key, Postgres, S3 bucket, Git PVC, owner key) at
      `helm install` time; it is also print-only.
    - `launchpad/deploy/runbooks/hardening-spec.md` Part E states this outright:
      "`run.sh backup-hint` prints a correct checklist and automates nothing. Turn it
      into a role." — a proposal document, not shipped tooling.
    So: no backup or restore tooling ships in this repository. Verified directly, not
    inherited from the two sibling agents' prior claim.
  Read and confirmed: `crates/buzz-relay/src/api/git/hydrate.rs`'s own module doc states
    "object storage remains authoritative" over cached pack/index pairs, and
    `crates/buzz-relay/src/config.rs` builds `git_repo_path`/`git_pack_cache_path` as
    self-bootstrapping scratch directories (`ensure_git_repo_path` creates them if
    missing); `transport.rs` uses `git_repo_path` only as a `NamedTempFile` scratch dir.
    `launchpad/docs/corpus/architecture/containers/object-storage.md` (merged,
    `architecture-containers-object-storage`) independently states git ref/object state
    is "entirely object-store-backed" and each replica needs only ephemeral
    `ReadWriteOnce` storage. This confirms the brief's framing: object storage is the
    git source of truth; the on-disk git path is a disposable hydration/pack cache —
    even though `deploy/compose/compose.yml` and the Helm chart still provision it as a
    named, persistent volume (`buzz-git-data` / a PVC). That is an infrastructure
    convenience (avoids re-hydrating every repo from cold on every container restart),
    not a durability requirement, and the document states this as a discrepancy rather
    than silently picking one source.
  Read and confirmed: `crates/buzz-relay/src/router.rs`'s `readiness_handler` (line 410)
    checks only Postgres (`state.db.ping()`), Redis (`state.redis_pool.get()`), and the
    deletion-serving catalog — never S3/object storage. `main.rs` hard-fails process
    startup on a Postgres connection error (line 187-190) but does not synchronously
    probe S3 reachability at boot.
  Read and confirmed: `.env.example`'s Relay section states `BUZZ_RELAY_PRIVATE_KEY` is
    the "Stable relay signing key (required)" and instructs "Preserve that value across
    restarts and backups." `crates/buzz-relay/src/main.rs`'s `relay_keypair_from_config`
    hard-fails startup when the key is absent (message: "BUZZ_RELAY_PRIVATE_KEY must be
    set..."), gated as described in the merged `layers-configuration-secrets` node.
  Read and confirmed: `deploy/compose/compose.yml`'s production Redis service runs with
    `--appendonly yes` against a named `buzz-redis-data` volume — i.e. this repository's
    own production Compose bundle does persist Redis to disk. This does not contradict
    the "Redis is disposable" framing: the merged `architecture-containers-redis` node's
    own evidence ledger establishes every key `buzz-pubsub` writes is TTL-bound or a
    transient pub/sub message with a durable Postgres-backed fallback described in the
    code's own comments; the persistent volume is an operational nicety against a cold
    cache stampede, not a recovery requirement — the document states both facts and
    draws that distinction explicitly rather than picking the volume as sole evidence.
  Merged corpus nodes usable as `references` relationship targets today (checked against
    `<SCRATCH>/existing-node-ids.txt`, all four present): `architecture-containers-postgres`,
    `architecture-containers-redis`, `architecture-containers-object-storage`,
    `layers-configuration-secrets`.
  Sibling tasks named in the dispatch brief — backup (#1197) and restore (#1202,
    already-authored on other unmerged branches) and availability (#1214, cross-cutting)
    — are not in `<SCRATCH>/existing-node-ids.txt` and have no corresponding node id to
    target; the plan is to name the boundary in prose only, per the brief's explicit
    instruction not to link paths this Feature has not merged.

STEP 1  [independent]  Write the front matter: `id: operations-reliability-disaster-recovery`,
        `type: operations`, `status: draft`, `origin: launchpad`,
        `audiences: [operator, developer, reviewer]`, and an `evidence` ledger seeded
        with the mandatory single commit-only `FACT` (revision
        `473205a7457b208455f188847bfb27b01aa83cac`) plus one placeholder entry per
        substantive claim identified in ALREADY TRUE above (durable-state inventory,
        no-backup-tooling finding, git-cache-vs-object-storage discrepancy, Redis
        disposability, readiness-probe scope, relay-key startup gate). Declare the four
        `references` relationships named above.
        done when: the file exists at
        `launchpad/docs/corpus/operations/reliability/disaster-recovery.md` with
        schema-shaped front matter (a YAML parse succeeds and reports the five required
        keys plus `relationships`); `id` and `type` match exactly.

STEP 2  [needs 1]  ← RUNS HERE  Write the body against `corpus-template-reference`'s
        required sections: a Reference-description paragraph; a structured-entries table
        (or set of tables) inventorying every durable-state item (Postgres, the shared
        S3-compatible bucket as git-and-media source of truth, `BUZZ_RELAY_PRIVATE_KEY`,
        configuration/secrets, the owner key held outside the relay) and every disposable
        item (Redis, the local git hydration/pack cache) with a one-line reason and a
        citation for each row; a prose subsection stating the dependency order recovery
        would have to follow (Postgres reachable+migrated is a hard startup gate; object
        storage is not readiness-checked and can lag; Redis/local git cache need no
        recovery step at all — they rebuild); an explicit RTO/RPO subsection stating
        that none is defined anywhere in this repository, only the Buzz-specific RPO
        *constraint* named in `launchpad/deploy/runbooks/hardening-spec.md` ("Postgres
        and the object/git state must come from the same maintenance window") — itself
        an unimplemented proposal, not a shipped guarantee; a Boundary subsection naming
        the three template exclusions plus backup (#1197)/restore (#1202)/availability
        (#1214) as named-but-not-linked siblings; the Relationships section; and a
        Scope-and-omissions section carrying (a) what this node does not cover and who
        owns it, and (b) separately, what was expected but could not be verified
        (staging/production object-storage and Postgres topology, owned by the private
        `squareup/block-coder-tf-stacks` repo not present in this checkout).
        done when: every `##` section the template's *Required sections* lists is
        present; every table row and prose claim has a matching `evidence` entry; no
        claim rests only on an `UNVERIFIED`-shaped citation besides the one permitted
        commit-only FACT.

STEP 3  [needs 2]  Run `python3 launchpad/project-intelligence/corpus/validate.py` from
        the worktree root and fix whatever it reports until it exits 0. Re-read the body
        once against the issue's Definition of Done, bullet by bullet, confirming each
        of the two type-specific tail bullets ("structured for lookup," "contains only
        facts supported by current source and labels generated versus authored values")
        is satisfied by a real section, not merely asserted.
        done when: `validate.py` prints no errors and exits 0; a manual bullet-by-bullet
        pass against the DoD (recorded in the report, not in this file) finds no gap.

STEP 4  [needs 3]  Run the corpus test suite as the sole command in its own Bash call
        (verify-gate stamp): `python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py"`. Confirm `OK` in a
        separate call before committing — never chain the test command with `cd` or
        pipe its output.
        done when: the suite reports `OK` and the verify-gate stamps cleanly (no "no
        stamp found" refusal).

STEP 5  [needs 4]  Commit locally with `git add -A && git commit -s -m "docs(corpus):
        <subject> (#1216)"`. Do not push and do not open a PR.
        done when: `git log -1 --format=%B` shows a `Signed-off-by:` trailer and the
        subject references `#1216`; `git status` shows a clean working tree.

PARALLEL  None. Steps 1 and 2 edit the same single new file and are ordered by content
          dependency (front matter before the body it backs); steps 3-5 are strictly
          sequential gates over that one file. No step is dispatched as a parallel
          subagent.

GATES     `validate.py` exit 0 (STEP 3) and the corpus unittest suite `OK` (STEP 4) are
          the two mechanical gates this task owns. No `review-plan`/`review-code`
          dispatch — this is a single hand-authored document produced by one agent in a
          batch run, per the dispatch brief's scope; the orchestrator's own review layer
          runs after batch integration, not per-document.

BUDGET    STEP 2. The hard part is not the inventory table — that is a direct transcription
          of what was verified in ALREADY TRUE — it is stating the git-hydration-cache
          discrepancy (Helm/Compose provision it as durable-looking storage; the code and
          the merged object-storage node both say it is not) honestly, as a documented
          tension rather than silently picking one side or hedging into vagueness.

OPEN      Whether `agent` belongs in `audiences` alongside operator/developer/reviewer.
          Planned choice: leave it out — this node's content (what to snapshot, in what
          order, against what RPO) is operator-facing recovery planning; an agent
          reasoning about the system would more naturally reach the architecture
          container nodes this document references. Stated so a reviewer can overturn
          it cheaply.
          Whether the git-hydration-cache-vs-PVC tension should itself become a filed
          follow-up issue (stale backup-checklist documentation) rather than only being
          named in this node's body. Planned handling: name it in the body's scope
          section as a documented discrepancy and report it in STEP 5's self-review
          rather than filing a new issue unprompted — it is a documentation-accuracy
          observation about existing repo docs, not a second concept this node would be
          folding in.

LEFT OUT  Any `relationships` edge to backup (#1197), restore (#1202), or availability
          (#1214) — none has a resolvable node id on `origin/launchpad` yet (checked
          against `<SCRATCH>/existing-node-ids.txt`), and per `AGENTS.md` step 9 a target
          must resolve on the branch being merged into, not the author's own worktree.
          Named in body prose only, without a path link, per the brief's explicit
          instruction.
          Inventing an RTO/RPO number. None is stated anywhere in this repository; the
          document reports that absence as a fact rather than proposing a target figure,
          which would be exactly the "invented operational procedure" failure mode
          `AGENTS.md` and the dispatch brief both warn against.
          Editing `deploy/compose/run.sh`, the Helm chart, or `hardening-spec.md` to
          resolve the git-PVC-vs-cache documentation tension — out of scope; this task
          documents current repository state, it does not change it.
          A second corpus node for backup procedure or restore procedure — those are
          issues #1197/#1202, already authored elsewhere; this node is reference-shaped
          inventory, not runbook-shaped procedure.
