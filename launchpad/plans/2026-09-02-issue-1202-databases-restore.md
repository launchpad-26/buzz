Issue #1202 — task: document operations/databases/restore.md
Stated size: none stated  →  cap: 5 steps (one hand-authored reference document, per
the batch dispatch brief for Feature #618)

Target file: `launchpad/docs/corpus/operations/databases/restore.md`
Node id: `operations-databases-restore` (assigned by the issue brief; permanent)
Template: `launchpad/docs/corpus/templates/reference.md`
Base branch: `origin/launchpad`

ALREADY TRUE  (verified against git at 473205a7457b208455f188847bfb27b01aa83cac, not notes)
  `git status --short` in this worktree reports nothing tracked yet for this task; only
    this plan file is new.
  `launchpad/docs/corpus/operations/` does not exist. This task creates
    `operations/databases/restore.md` as the first file in that subtree.
  No id starting `operations-` appears in `<SCRATCH>/existing-node-ids.txt` (204 ids,
    grep count 0), so `operations-databases-restore` is free and no sibling
    `operations/**` node exists yet to link.
  `architecture-deployment-single-relay`, `architecture-containers-postgres`,
    `architecture-containers-redis`, and `architecture-containers-object-storage` are
    all present in `<SCRATCH>/existing-node-ids.txt`, so a `references` edge to any of
    them resolves against `origin/launchpad` today.
  The repository ships no restore command anywhere: `deploy/compose/run.sh` defines
    `start|stop|restart|pull|upgrade|logs|status|config|backup-hint|add-member|
    remove-member|list-members` and nothing named restore; `backup_hint()` only prints a
    checklist. `Justfile` has no backup/restore/dump recipe (`grep -in
    "backup\|restore\|pg_dump\|pg_restore" Justfile` — no matches).
  Git repository content is not durably on local disk: `crates/buzz-db/src/store/
    git_repo.rs`'s module doc states the relay holds no persistent per-repo filesystem
    state and hydrates an ephemeral bare repo from object storage per request, backed by
    `docs/git-on-object-storage.md`'s manifest-pointer CAS protocol; the code it
    describes (`hydrate_for_read`/`hydrate_for_write`/`cas_publish`/`finalize_push`/
    `run_conformance_probe`) exists in `crates/buzz-relay/src/api/git/`.
  Production Postgres/Redis/object-storage state is only durable via `deploy/compose/
    compose.yml`'s four named volumes (`buzz-postgres-data`, `buzz-redis-data` with
    `--appendonly yes`, `buzz-minio-data`, `buzz-git-data`); the root `docker-compose.yml`
    used for local dev has no Redis volume at all, and `scripts/dev-reset.sh` states
    outright that "Redis data is ephemeral and always wiped on restart."
  Two independent schema-creation paths exist and neither is framed by the repository as
    a restore tool: `schema/schema.sql` + `./bin/pgschema apply` +
    `scripts/reconcile-schema-after-pgschema.sql` (used by CI and the local/test-relay
    scripts to converge a fresh database), and the embedded `sqlx::migrate!` in
    `crates/buzz-db/src/runtime/migration.rs` run via `buzz-admin migrate` or
    `BUZZ_AUTO_MIGRATE` (used by real deployments per
    `architecture-deployment-single-relay`'s own evidence).

STEP 1  Reference description, structured entries table, and Commands   [independent]
        Create the file with schema-valid front matter (`id:
        operations-databases-restore`, `type: operations`, `status: draft`, `origin:
        launchpad`, `audiences: [operator, developer, reviewer]`) and the template's
        first three required sections: a Reference description paragraph naming what
        the node catalogues (what a restore of this system's persistent state has to
        put back, in what order, with what tooling) and how it relates to the sibling
        backup (#1197) and disaster-recovery (#1216) nodes without restating them; a
        structured-entries table, one row per store (Postgres schema, Postgres data,
        object storage / media, object storage / git CAS, the `buzz-git-data` working
        volume, Redis, the relay signing key and other `deploy/compose/.env` secrets),
        each row stating what must come back and what tooling this repository provides
        for it, cited to the evidence gathered before drafting; and an optional Commands
        section listing the schema-bootstrap and migration commands that exist
        (`pgschema apply` + the reconcile script, `buzz-admin migrate`) with a citation
        for each, explicit that none of them is a restore command.
        done when: `cd <worktree> && python3 launchpad/project-intelligence/corpus/
                   validate.py` exits 0 with the new file on disk, and
                   `git cat-file -e 473205a7457b208455f188847bfb27b01aa83cac` exits 0,
                   which is what makes the provenance ledger entry a FACT rather than an
                   UNVERIFIED assertion.

STEP 2  Order and the cross-store consistency traps          [needs 1]  ← RUNS HERE
        Write the restore-ordering guidance the tables in step 1 depend on (secrets/key
        before anything that authenticates with them; object storage before Postgres is
        made live, because Postgres rows and git manifests point into it) and the
        cross-store consistency traps named in the dispatch brief: an event or git
        manifest row surviving in a Postgres snapshot while the object-storage blob it
        names does not (or the reverse — a blob restored from an older/newer snapshot
        than Postgres), grounded in `crates/buzz-media/src/storage.rs`'s `delete`/
        `delete_objects` existing (so blobs are not append-only, unlike git's
        content-addressed packs) and in the git-on-object-storage spec's no-deletion
        rule for packs/manifests. Classify each claim honestly — the ordering
        conclusions are INFERENCE with a stated confidence; what tooling exists is FACT.
        done when: validator exits 0; every ordering and consistency-trap claim in the
                   body has a matching `evidence` entry, checked by re-reading the
                   ledger against the body section; and no entry rests only on an
                   UNVERIFIED commit citation.

STEP 3  Boundary statement and Relationships                            [needs 2]
        Write the template's Boundary section (not backup's own content per #1197; not
        the whole-site disaster-recovery case per #1216; not the in-app community
        deletion/recovery control plane in migrations 0029-0030, which is a soft-delete
        undo, not an infrastructure restore) and declare `references` edges to the four
        already-merged nodes confirmed in ALREADY TRUE, with the one sentence each edge
        needs per `launchpad/docs/corpus/standards/linking.md`'s MUST 6 (prose plus edge,
        not either alone).
        done when: validator exits 0; each declared relationship target is one of the
                   four confirmed ids (`grep -A1 "type: references" launchpad/docs/
                   corpus/operations/databases/restore.md` printed and checked by eye);
                   and the boundary paragraph names #1197, #1216, and the community-
                   deletion migrations by number.

STEP 4  Scope and omissions, plus the template-used evidence entry      [needs 3]
        Write the Scope and omissions section carrying the two distinct things
        AGENTS.md's step 8 requires: what this node does not cover and who owns it
        (separate from step 3's boundary, which is about neighboring *concepts*, not
        gaps), and, separately, what was expected but could not be verified while
        drafting (e.g., no live restore was actually performed against a real backup;
        Docker Compose's own default `stop_grace_period` was not independently checked
        here either, consistent with the gap `architecture-deployment-single-relay`
        already names). Add the final evidence entry naming
        `launchpad/docs/corpus/templates/reference.md` as the template this node was
        built from.
        done when: validator exits 0 and the ledger's last entry cites
                   `launchpad/docs/corpus/templates/reference.md`.

STEP 5  Audit the finished node against its own ledger and the DoD      [needs 4]
        Re-read the whole file against issue #1202's Definition of Done bullet by
        bullet, and against its own ledger: every body claim has an entry, every entry
        backs a body claim, exactly one commit-only FACT exists, every FACT's cited
        source was actually opened (re-open each one), and no repository path was cited
        without having been read. Fix anything the audit finds.
        done when: `cd <worktree> && python3 launchpad/project-intelligence/corpus/
                   validate.py` exits 0; run, as the sole command in its own tool call,
                   `python3 -m unittest discover -s launchpad/project-intelligence/
                   corpus/tests -p "test_*.py"` and confirm `OK`; and
                   `grep -c "commit 473205a7457b208455f188847bfb27b01aa83cac"
                   launchpad/docs/corpus/operations/databases/restore.md` prints exactly
                   `1`.

PARALLEL  None. All five steps edit the same single file; the skill's own rule is that
          two steps touching one file are sequential regardless of how unrelated they
          look. There is no second artefact to fan out to — the issue's out-of-scope
          list forbids a second hand-authored corpus document.

GATES     `review-plan` on this plan before STEP 1 — self-run, therefore not
          independent, and the report says so. `review-code` on the finished diff after
          STEP 5, focused on whether every citation actually supports its statement
          (structural validation cannot check this). `review-tests` does not apply: the
          diff adds one Markdown node and this plan file, and touches no test file (STEP
          5 runs the existing corpus suite unmodified). `qa` explore mode does not
          apply: no runtime interface changes; `validate.py` is the only executable
          surface and it is exercised as every step's own done-when.

BUDGET    STEP 2. The ordering and cross-store consistency claims are the part of this
          document with no existing corpus precedent to draw the shape from — the
          merged `architecture-deployment-single-relay` node documents the backup
          checklist and the git-on-object-storage design document proves the CAS
          protocol, but neither states a restore order or names the trap of a Postgres
          row outliving its object-storage blob (or vice versa). Deriving that
          correctly, and keeping each conclusion honestly classed as INFERENCE rather
          than dressed up as FACT, is where the time goes.

OPEN      Whether `developer` belongs in `audiences` alongside `operator` and
          `reviewer`. Resolved here as yes: a developer debugging a broken local
          environment (`just reset`, `./scripts/dev-reset.sh`) hits the same
          store-recreation facts an operator restoring production does, and the
          evidence gathered (dev-reset.sh, dev-setup.sh) is dev-environment tooling a
          developer would use directly.

          Whether to name the object-storage bucket's lack of a documented retention/GC
          policy as a restore-relevant gap or leave it to the object-storage container
          node. Resolved here as: mention it only insofar as it bears on restore
          ordering (an older bucket snapshot cannot 404 on a manifest a newer Postgres
          snapshot expects, because the CAS protocol never deletes packs/manifests
          under normal operation), and link the object-storage node for the rest rather
          than re-deriving its ownership boundary.

LEFT OUT  A live restore rehearsal against a real backup. None exists to restore from in
          this environment, and one is not part of this issue's Definition of Done —
          recorded instead as an "expected but not verified" gap in step 4.

          Editing `architecture-deployment-single-relay`, `docs/git-on-object-storage.md`,
          or any other existing document to add a pointer back to this node. The issue's
          out-of-scope list forbids broad "while here" documentation cleanup; a
          follow-up edge, if wanted, is a separate change.

          A second hand-authored corpus document of any kind — including a template for
          "operations" nodes in general, or a restatement of backup's (#1197) or
          disaster-recovery's (#1216) content. The issue's out-of-scope list forbids it
          explicitly.
