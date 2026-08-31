Issue #929 — task: document implementation/crates/buzz-media.md
Stated size: none given on the issue (no Size label; dispatch brief caps this batch task at 5 steps)  →  cap: 5 steps

ALREADY TRUE  (verified against git and GitHub, not notes)
  `launchpad/docs/corpus/implementation/crates/buzz-media.md` does not exist yet on
    `origin/launchpad` (`ls` in a fresh worktree at HEAD 76a0a4ebbe4bc4d852b0d04362ed768620da34b3
    reports no such file) — this is the first node under `implementation/` in the corpus tree.
  `launchpad/docs/corpus/templates/implementation-reference.md` exists and is read in full;
    it prescribes exactly seven required body sections and states `type: implementation` is
    the default `type` value for this template's nodes.
  Three architecture nodes already exist and already describe buzz-media's role, so they are
    candidate relationship targets, each independently confirmed present on `origin/launchpad`:
    `architecture-containers-object-storage`, `architecture-flows-media-upload`,
    `architecture-flows-media-download` (front matter `id` fields read directly).
  `crates/buzz-media/src/lib.rs` declares the crate a library with no Axum dependency for
    handlers ("Axum handlers live in `buzz-relay`") and re-exports ten modules' public surface.
  `crates/buzz-relay/src/router.rs` registers the only three Blossom HTTP routes buzz-media's
    logic backs: `PUT /upload`, `PUT /media/upload` (legacy alias) → `upload_blob`;
    `GET|HEAD /media/{sha256_ext}` → `get_blob`/`head_blob` — both in `crates/buzz-relay/src/api/media.rs`.
  `buzz_media::MediaStorage`/`MediaConfig` are also consumed outside the Blossom endpoints —
    grep confirms real call sites in `crates/buzz-relay/src/api/git/{manifest,transport,hydrate,store,cas_publish,policy}.rs`,
    `handlers/{imeta,ingest,identity_archive,event,relay_admin}.rs`, `api/{gifs,invites,bridge,operator,admin/mod}.rs`,
    `config.rs`, `main.rs`, `state.rs`, `storage_sweep.rs`, `workflow_sink.rs` — so the crate is the
    shared S3 substrate for git CAS and other subsystems, not solely the media/Blossom surface.
  126 `#[test]`/`#[tokio::test]` functions exist directly under `crates/buzz-media/src/*.rs`
    (grep count), plus two `#[ignore]`-gated live-MinIO integration test files
    (`tests/static_creds_minio.rs`, `tests/versioned_minio.rs`, 13 tests) documented as run via
    `cargo test -p buzz-media --test <name> -- --ignored` against docker-compose MinIO.
  Repository revision for all citations: `git rev-parse HEAD` = `76a0a4ebbe4bc4d852b0d04362ed768620da34b3`,
    confirmed matching `origin/launchpad` at worktree creation time.

STEP 1  [independent] ← RUNS HERE Write
        `launchpad/docs/corpus/implementation/crates/buzz-media.md` with front matter
        (`id: implementation-crates-buzz-media`, `type: implementation`, `status: draft`,
        `origin: launchpad`, `audiences: [agent, developer, reviewer]`) and an `evidence` ledger
        with one `FACT` entry per substantive claim in the body, each citing a real path or
        symbol actually opened during investigation (auth.rs, config.rs, storage.rs,
        bucket_index.rs, upload.rs, validation.rs, error.rs, types.rs, upload_record.rs,
        thumbnail.rs, lib.rs, router.rs, api/media.rs, plus the crate's Cargo.toml and test
        files) and a commit citation for the recorded revision. Body follows the template's
        seven required sections: Realization statement, Target, Implementation surface (a
        table of module/symbol → what it's responsible for), Divergences, Verification,
        Relationships, Scope and omissions. Declare `implements` toward
        `architecture-containers-object-storage` (buzz-media is the concrete crate realizing
        that architectural container) and `references` toward
        `architecture-flows-media-upload`/`architecture-flows-media-download` (supporting
        context on how the crate's logic is invoked over HTTP, no ownership implied).
        done when: the file exists at that path with all seven required sections present and
        every `relationships[].target` naming one of the three ids confirmed to exist above.

STEP 2  [needs 1] Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
        worktree root. If it reports any FAIL for the new node, fix front matter/citations and
        re-run until clean; confirm any remaining FAILs are the pre-existing ~21-failure
        baseline already on `origin/launchpad` (diff the failing node ids against a
        `git stash`-applied run without this file, or check the failure list names no node id
        this file introduces).
        done when: `validate.py` reports zero FAIL entries whose node id is
        `implementation-crates-buzz-media`.

STEP 3  [needs 2] Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in its own tool call, confirming `OK`.
        done when: the suite reports `OK` with no failures or errors.

STEP 4  [needs 3] Stage and commit the two new files
        (`launchpad/docs/corpus/implementation/crates/buzz-media.md`,
        `launchpad/plans/2026-09-01-issue-929-buzz-media.md`) with `git commit -s`, using a
        commit message referencing issue #929. Do not push and do not open a PR — this batch's
        37 documents integrate into one Feature-level draft PR later.
        done when: `git log -1` shows the new commit on `task/929-buzz-media` containing exactly
        those two files, signed off, and `git status` is clean.

PARALLEL
  None of steps 1–4 can run concurrently — each step's `done when` gates the next.

GATES
  `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 (or its only remaining
    FAILs match the documented pre-existing baseline, not this node).
  `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
    reports `OK`.
  Commit gate: `git commit -s` succeeds (no `--no-verify`); if it refuses with no stamp found,
    stop and report BLOCKED rather than bypassing it.

BUDGET
  One corpus node (~150-250 lines of Markdown) plus this plan file. No source code changes.
  Investigation is already done (see ALREADY TRUE); steps 1–4 are drafting and verification only.

OPEN
  Whether `architecture-containers-object-storage` is the best `implements` target versus
    `part-of` was decided during step 1 drafting using `relationships.schema.json`'s stated
    directionality (`implements`: "source is the concrete realization of target") — a builder
    should not silently pick `part-of` instead without checking that directionality note first.

LEFT OUT
  No `implements`/`part-of` edge to a NIP/BUD specification document (e.g. BUD-01/BUD-11 for
    Blossom) is declared, because no such document carries a corpus node id yet — per
    `AGENTS.md`'s rule, an edge to a nonexistent id is a hard validation error, not a soft
    placeholder. The *Target* section names the real BUD specs in prose instead.
  No second corpus node is created for git-CAS's reuse of buzz-media's S3 client — that is
    scope for whatever node documents git storage, not this one; buzz-media's *Scope and
    omissions* section names it as owned elsewhere.
  No changes to `crates/buzz-media` source, tests, or any other crate — this is a docs-only
    corpus task per the issue's Out of scope section.
