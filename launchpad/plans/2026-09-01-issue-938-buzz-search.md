Issue #938 — task: implementation reference for buzz-search
Stated size: no `Size` line  →  cap: 5 steps (batch-author's own brief, not asked per-issue)

ALREADY TRUE  (verified against git and code, not notes)
  Worktree `__worktrees/task-938-buzz-search` is on branch `task/938-buzz-search`,
    based on `origin/launchpad`, HEAD `76a0a4ebbe4bc4d852b0d04362ed768620da34b3`,
    working tree clean except this plan file.
  `launchpad/docs/corpus/implementation/crates/buzz-search.md` does NOT exist yet.
  `launchpad/docs/corpus/templates/implementation-reference.md` is the required
    template: realization statement, target, implementation surface table,
    divergences, verification, relationships, scope-and-omissions, all mandatory.
  `git ls-tree -r --name-only HEAD -- launchpad/docs/corpus` lists 0 nodes under
    `implementation/` — this is the corpus's first implementation-reference node,
    so no `part-of` target exists and no `implements` target with a corpus id exists.
  Two merged nodes are real `references` candidates: `architecture-flows-search-query`
    (the NIP-50 request→response flow across both transports) and
    `architecture-containers-postgres` (the Postgres container, which already names
    buzz-search's own search pool as one of Postgres's callers).
  `crates/buzz-search/` is four files: `Cargo.toml`, `src/lib.rs`, `src/error.rs`,
    `src/query.rs`, plus `tests/fts_integration.rs`. No `README.md`.
  `src/lib.rs`'s crate doc states the crate's boundary explicitly: it is the
    **query** side only (indexing is the SQL row insert, owned by `buzz-db`), and
    it names `docs/multi-tenant-conformance.md` "conformance row 50" as the spec
    it's checked against for the community-scoping invariant — confirmed by reading
    row 50 of that file directly (`Search / FTS`, line 50).
  `SearchService::search` is the one public entry point (`crates/buzz-search/src/lib.rs`
    + `src/query.rs::search`); `buzz-relay` is the only caller, wired at two call
    sites: `crates/buzz-relay/src/api/bridge.rs` (HTTP `POST /query`, supports
    `SearchMode::Prefix` via `extract_search_mode`) and
    `crates/buzz-relay/src/handlers/req.rs` (`handle_search_req`, WS `REQ`,
    hardcodes `SearchMode::FullText` — never passes `Prefix` — a real, citable
    divergence between the two transports' capability, not a target mismatch).
  `crates/buzz-search/tests/fts_integration.rs` is the representative test file:
    18 `#[ignore = "requires Postgres"]` tests covering community isolation,
    channel scoping (all four `ChannelScope` variants), soft-delete exclusion,
    pagination/clamping, NUL-byte sanitization, and three storage-level privacy
    tripwires (`excluded_kinds_are_storage_level_unsearchable`,
    `author_only_kinds_are_storage_level_unsearchable`,
    `p_gated_persistent_kinds_have_storage_null_tsvector`). `src/query.rs` also
    carries 3 unit tests for `normalized_search_text`.

STEP 1  [independent]  ← RUNS HERE  Create the file with schema-valid front matter
        only: `id: implementation-crates-buzz-search`, `type: implementation`,
        `status: draft`, `origin: launchpad`, `audiences: [agent, developer,
        reviewer]`, an `evidence` ledger seeded with the commit-`76a0a4e…`
        provenance entry, and a `relationships` array declaring exactly two
        `references` edges (`architecture-flows-search-query`,
        `architecture-containers-postgres`) — both already merged on
        `origin/launchpad`, so both resolve. No `implements`/`part-of` edges: no
        merged node carries a corpus id for `docs/multi-tenant-conformance.md`,
        NIP-50, or any broader implementation node, per the template's rule
        against inventing an edge to an id that does not exist.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py`
        exits 0 with the new file present and no relationship errors reported
        for it.

STEP 2  [needs 1]  Write the evidence ledger: one entry per substantive claim
        about the crate's boundary (query-side only, not indexing), its public
        surface (`SearchService::new`/`search`, `SearchQuery`, `ChannelScope`'s
        four variants, `SearchMode`), the community-scoping fence
        (`community_id = $ctx` as the first, non-optional predicate), the
        WS-vs-HTTP `SearchMode::Prefix` asymmetry, and the relay wiring at both
        call sites — classified FACT (crate source, `bridge.rs`, `req.rs`,
        `main.rs` opened directly) or, for the row-50 conformance claim, cited
        to `docs/multi-tenant-conformance.md` directly (also FACT, since it was
        opened).
        done when: every evidence entry cites a path actually read in this
        session (`crates/buzz-search/src/{lib,query,error}.rs`,
        `crates/buzz-search/tests/fts_integration.rs`,
        `crates/buzz-relay/src/api/bridge.rs`,
        `crates/buzz-relay/src/handlers/req.rs`,
        `crates/buzz-relay/src/main.rs`, `docs/multi-tenant-conformance.md`) and
        `validate.py` still exits 0.

STEP 3  [needs 2]  Write the body against the template's required sections in
        order: realization statement, target (`docs/multi-tenant-conformance.md`
        row 50 — no corpus id yet, stated plainly), implementation surface table
        (component/file/symbol → what it satisfies), divergences (the WS
        `SearchMode::Prefix` gap is the one real divergence found; state
        explicitly what else was checked and found aligned), verification (cite
        the 18 ignored integration tests + 3 unit tests by name), relationships
        (restate the two `references` edges and why no `implements`/`part-of`),
        scope and omissions (this node does not cover `buzz-db`'s write-side
        indexing, the relay's per-hit re-authorization gate already owned by the
        flow node, or the HTTP/WS transport contracts already owned by their own
        nodes).
        done when: `validate.py` exits 0 and every `##` section the template
        requires is present, in the template's order.

STEP 4  [needs 3]  Self-audit: re-read the diff against issue #938's Definition
        of Done line by line (one hand-authored node; schema-valid front matter;
        one independently maintainable idea; every claim traceable and
        classified; links without duplicating; checked against the recorded
        revision; validator passes; states responsibility and non-ownership;
        names public interfaces/dependencies; links owned paths and tests;
        avoids restating canonical claims already in the flow/container nodes).
        Attempt `corpus-review` skill if reachable in this session; if not,
        record that the self-review substituted for it.
        done when: a written line-by-line DoD mapping exists (in the report,
        not committed) and `validate.py` exits 0 with zero FAIL entries whose
        node is `implementation-crates-buzz-search` — confirmed against the
        pre-existing ~21-failure baseline via `git stash`/diff, not assumed.

STEP 5  [needs 4]  Earn the commit gate and commit locally — no push, no PR.
        done when: `python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports
        `OK` as the sole command in its own tool call, then `git add` the two
        files and `git commit -s` succeeds with a `Signed-off-by:` trailer in
        `git log --format=%B -1`.

PARALLEL  None. Steps 1-3 all build the same single file
          (`launchpad/docs/corpus/implementation/crates/buzz-search.md`) and are
          strictly sequential; front matter must exist before the ledger, and
          the ledger before the body cites it. No step is dispatched as a
          parallel subagent.

GATES     `corpus-review` in STEP 4 if reachable; otherwise a documented manual
          self-review substitutes, stated plainly in the final report per this
          task's own instructions. `review-code`/`review-tests` do not apply —
          this is a docs-only corpus node, not an implementation diff.
          `qa` explore mode does not apply: no runtime interface exists to
          exercise; the only executable surface touched is `validate.py`, which
          this change calls but does not modify.

BUDGET    STEP 3's divergences section. The template treats an empty divergence
          section as an unverified claim, not a clean bill of health — the WS/HTTP
          `SearchMode::Prefix` asymmetry is the one concrete divergence this
          investigation found; naming it honestly, and naming what else was
          checked and found aligned, needs more care than the other sections.

OPEN      Whether `docs/multi-tenant-conformance.md` should eventually get its
          own corpus node that this node could `implements` toward. Not this
          task's to create (its own DoD forbids a second authored document);
          left named in *Target* and *Scope and omissions* as a gap, not solved.

LEFT OUT  An `implements` edge to any spec/decision. No merged corpus node
          represents NIP-50, `docs/multi-tenant-conformance.md`, or any other
          target buzz-search realizes — inventing one would be a hard validation
          error against `origin/launchpad`, and the template forbids inventing
          an id-shaped placeholder.
          A `part-of` edge toward a broader crate-family implementation node —
          none exists yet; this is the first implementation-reference instance,
          exactly as the template's own note anticipates.
          Editing `crates/buzz-search/` itself, even where its missing
          `README.md` would help future readers — out of scope for a docs-only
          corpus task, and not requested by #938.
          Documenting the write side (`buzz-db`'s `insert_event`/generated
          `search_tsv` column) or the relay's per-hit re-authorization gate in
          full — both already owned by `architecture-containers-postgres` and
          `architecture-flows-search-query` respectively; restating them here
          would violate AGENTS.md's "avoid duplicating canonical content" rule.
