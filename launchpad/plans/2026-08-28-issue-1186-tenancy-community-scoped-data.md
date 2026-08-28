Issue #1186 — task: document layers/tenancy/community-scoped-data.md

ALREADY TRUE  node.schema.json is merged on origin/launchpad (revision
  338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5); 25 templates are merged under
  launchpad/docs/corpus/templates/, none named layers or tenancy, all of them
  meta-documents (type: governance) about a structural shape rather than a
  per-surface template keyed to node.schema.json's `type` enum; no
  launchpad/docs/corpus/layers/ directory exists anywhere in this worktree or
  on origin/launchpad, so launchpad/docs/corpus/layers/tenancy/
  community-scoped-data.md does not exist yet; sibling #1185
  (community-scoped-cache.md, Redis/in-memory scoping) is also unwritten, so
  no relationship target exists there either; templates/invariant.md is
  merged and its own front matter states a node built from it "chooses type
  by the subject matter the invariant concerns," so type: layers (per this
  task's own instructions, matching the node's directory) does not conflict
  with using its structural skeleton.

STEP 1  Gather evidence for the Postgres-level data-scoping invariant: read
        migrations/0001_initial_schema.sql (header design statement, the
        `communities`/`channels`/`channel_members`/`users`/`events`/
        `event_mentions` table definitions, the `_operator_global_tables`
        allowlist registry), crates/buzz-db/src/event.rs
        (`EventQuery::for_community`'s no-default construction, the
        `WHERE community_id = $1` pattern across get/soft-delete/upsert),
        crates/buzz-db/src/migration.rs's migration-lint test module (the
        `all_non_operator_global_tables_have_not_null_community_id` and
        `scoped_primary_key_unique_and_foreign_key_constraints_lead_with_
        community_id` lints, run against the real embedded migration SQL —
        run `cargo test -p buzz-db --lib migration::` to confirm both pass
        at the recorded revision, not merely read the assertion text),
        crates/buzz-db/src/lib.rs's BUG-5 regression comment and
        `reactions_are_scoped_to_community` test (a real historical
        cross-tenant leak from an `add_reaction` call site that omitted
        `community_id`) and `routed_reads_are_confined_to_the_requested_
        community` (an `#[ignore = "requires Postgres"]` A/B isolation
        test), crates/buzz-core/src/tenant.rs (`CommunityId`'s no-client-
        parse constructor), and docs/multi-tenant-conformance.md's storage-
        layer conformance rows. Read
        launchpad/docs/corpus/architecture/principles/community-is-security-
        boundary.md and launchpad/docs/corpus/templates/invariant.md in
        full for structure and the correct relationship direction to the
        existing security-boundary node.
        done when: every claim in the finished document has a citation to a
        file actually opened above, and the two migration-lint tests were
        actually run and observed passing this session.

STEP 2  Write the front matter (id: layers-tenancy-community-scoped-data,
        type: layers, status: draft, origin: launchpad, audiences: [agent,
        developer, reviewer], relationships: [{depends-on,
        architecture-principles-community-is-security-boundary}] — the
        data-layer scoping claim only holds because TenantContext/
        CommunityId is correctly bound upstream, and that id is present on
        origin/launchpad) and the body, following templates/invariant.md's
        skeleton: one-sentence invariant statement, scope (which tables/
        queries/call paths it binds and the explicit operator-global
        exceptions), enforcement today (named honestly by tier: DB
        NOT NULL/composite-key/trigger constraints plus the migration-lint
        test suite — not claimed as a compiler-level guarantee), consequence
        of violation (grounded in the BUG-5 regression, not assumed),
        boundary (distinct from sibling #1185's Redis/cache scoping and from
        the security-boundary node's request-binding claim), relationships,
        and a scope-and-omissions section naming the `#[ignore]`-gated A/B
        test as unexecuted this session.
        done when: the file exists and is schema-shaped.        [RUNS HERE]

STEP 3  Validate: `python3 launchpad/project-intelligence/corpus/validate.py`
        must exit 0 against the full corpus tree including the new file.
        done when: exit 0.

STEP 4  Earn the commit-verification stamp with
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        (run alone, in its own tool call), then commit the plan and the
        document together and open a draft PR against launchpad.
        done when: unittest reports OK, commit succeeds, PR is opened as
        draft.

PARALLEL  None — one document, one plan file, strictly sequential.

GATES     python3 launchpad/project-intelligence/corpus/validate.py (must
          exit 0). review-adjudicate and the cross-model final pass are
          explicitly deferred to the batch owner's review of the whole
          batch — not run here.

BUDGET    Evidence-gathering (STEP 1) is the step most likely to take the
          most time: the claim spans schema design intent, concrete table
          DDL, query-construction code, and a real regression test, and
          every FACT needs an opened source plus (for the enforcement claim)
          an actually-executed test, not a plausible-sounding one.

OPEN      Whether `depends-on` or `references` is the corpus-wide convention
          for a data-layer invariant citing the request-binding invariant it
          builds on is not settled by any merged standard; this task picks
          `depends-on` per relationships.schema.json's own directionality
          ("source requires target to be true/current for source's own
          claims to hold") since data-layer scoping is meaningless if
          `community_id` values were not already trustworthy, and says so
          in the node's Relationships section rather than presenting the
          choice as settled corpus-wide.

LEFT OUT  Standing up Postgres to execute `routed_reads_are_confined_to_the_
          requested_community` or `reactions_are_scoped_to_community`
          (`#[ignore]`-gated, needs a live database). Any second
          hand-authored corpus document, including #1185's cache-scoping
          node. Editing AGENTS.md, node.schema.json, or templates/
          invariant.md. Auditing every table in
          docs/multi-tenant-conformance.md's full obligation table for
          implementation-vs-aspirational status — only the storage-layer
          row and the tables this task's evidence actually opened are
          claimed.
