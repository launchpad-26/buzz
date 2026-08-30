Issue #1088 — row-level-security corpus document

Stated size: issue #1088 has no explicit Size line; corpus-batch-author's own loop caps a single-document task -> cap: 5 steps

ALREADY TRUE

- `launchpad/docs/corpus/layers/data/postgres/row-level-security.md` does not exist
  (`test -f` confirmed in the worktree, fresh off `origin/launchpad`).
- `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum has no `data` or
  `postgres` member. Per precedent from earlier batches of this run, `layers/data/...`
  documents use `type: layers` — disclosed as an override of whatever the chosen
  template's own worked example suggests.
- `launchpad/docs/corpus/architecture/containers/postgres.md` (id
  `architecture-containers-postgres`) is merged on `origin/launchpad` and already
  documents Postgres's container-level boundary, including one paragraph naming
  `community_id` as "the security-relevant boundary the container exists to hold."
  It explicitly defers table-by-table schema contents and the multi-tenant
  conformance contract to `migrations/0001_initial_schema.sql` and
  `docs/multi-tenant-conformance.md` — this task's actual gap to fill.
- No sibling `layers/data/postgres/*` document exists on `origin/launchpad` yet, so
  no `relationships` may target one.
- RLS does not exist in this codebase today. Grep across all of `migrations/` (31
  files) and every `.rs`/`.sql` file in the repository finds zero occurrences of
  `CREATE POLICY`, `ENABLE ROW LEVEL SECURITY`, or `FORCE ROW LEVEL SECURITY`. The
  only two files mentioning RLS at all are `docs/multi-tenant-conformance.md`
  (lists "every tenant-scoped table has `community_id`, RLS policy, ..." as an
  unbuilt future migration gate) and `docs/multi-tenant-relay.md` (a `draft`-tagged
  formal specification stating RLS as an axiom — A-RLS-1..5 — its safety proof
  would rely on if a multi-tenant architecture ships; its own conformance tests in
  `crates/buzz-test-client/tests/conformance_multitenant.rs` are `todo!()`-stubbed
  and `#[ignore]`d pending "the lane it depends on lands on the integration
  branch"). Today's actual mechanism is query-level: every tenant-scoped table
  carries `NOT NULL community_id` (`migrations/0001_initial_schema.sql`), composite
  primary keys and indexes lead with `community_id`, `buzz-db`'s query construction
  binds `community_id` on every read/write (`crates/buzz-db/src/event.rs` and
  siblings), and `crates/buzz-relay/src/tenant.rs` resolves `community_id`
  server-side from the connection's `Host` header before any handler runs, never
  trusting client input.
- `launchpad/docs/corpus/templates/datastore.md` (full running-instance profile)
  and `launchpad/docs/corpus/templates/reference.md` (Diátaxis Reference form —
  information-oriented catalogue of "the machinery and how it operates") are both
  read in full. Row-level security / tenant isolation is a cross-cutting mechanism
  spanning many tables, not a full datastore profile and not one domain entity, so
  `reference.md`'s shape fits the actual subject better than re-profiling the whole
  datastore.

STEP 1 [independent]
Choose the template shape and disclose the scope decision in the evidence ledger:
use `templates/reference.md` because the issue's DoD bullets ("owned data, key
access patterns, lifecycle/retention and consistency semantics"; "tenancy/security
boundaries and failure behavior"; "links schema/migrations/code/tests rather than
copying DDL") describe cataloguing an existing mechanism's facts, not authoring a
full datastore instance profile or a single-table domain model. Disclose two
things explicitly: (a) `type: layers` overrides the template's own worked example
per this batch's precedent, and (b) the issue is titled "row-level-security" but
the document's honest subject is "how Buzz enforces tenant isolation in Postgres
today," because RLS itself is not implemented.
done when: a written note (folded into this plan, above) states both disclosures
and will carry into the node's evidence ledger and boundary section.

STEP 2 [needs 1] <- RUNS HERE
Draft the front matter and evidence ledger at
`launchpad/docs/corpus/layers/data/postgres/row-level-security.md`: `id:
layers-data-postgres-row-level-security`, `type: layers`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, operator, reviewer]`. One
evidence entry per substantive claim: FACT for the provenance revision, the
`community_id NOT NULL`/composite-key schema facts, the query-level filtering
pattern, the host-derived resolution, the absence of any RLS statement, and the
`docs/multi-tenant-relay.md` draft/axiom/stubbed-test status; INFERENCE with
confidence for anything reasoned rather than directly read; TEAM_KNOWLEDGE for
anything attributed to the issue's own DoD text rather than a source opened this
session.
done when: every claim later written into the body has a matching ledger entry,
and no FACT rests only on an UNVERIFIED-shape citation.

STEP 3 [needs 2]
Write the body per `templates/reference.md`'s required sections: Reference
description; structured entries (a table of enforcement point / mechanism /
evidence — host binding, schema discriminator + composite keys, query-level
filter, conformance harness/spec status); Commands section omitted (no CLI
surface for this mechanism); Boundary statement (not the full Postgres datastore
profile, not a how-to for adding a new tenant-scoped table); Relationships
(`part-of` targeting `architecture-containers-postgres`, confirmed merged); Scope
and omissions (naming the RLS gap explicitly, per the issue's own DoD requirement
to name tenancy/security boundaries and failure behavior honestly).
done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.

STEP 4 [needs 3]
Earn the commit gate: run `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in
its own tool call and confirm `OK`. Then, in a separate tool call, `git add` the
plan and the target document and `git commit -s`.
done when: a commit exists, one commit ahead of `origin/launchpad`, and the prior
`unittest discover` run reported `OK` before that commit was made.

STEP 5 [needs 4]
Self-review: re-read `git diff origin/launchpad -- .` against every issue DoD
bullet line by line; re-check each evidence entry actually supports its claim;
confirm no second canonical document exists; re-run `validate.py`.
done when: every DoD bullet is either satisfied or its mismatch (RLS doesn't
exist) is named explicitly in the document rather than silently resolved, and
`validate.py` still exits 0.

PARALLEL

None of steps 2-5 can run in parallel with each other — each depends on the
previous step's file state (front matter before body, body before validation,
validation before commit, commit before self-review). Step 1 is a pure decision
step with no file writes, so nothing else is available to overlap it with in a
single-document task.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 (step 3, and
  re-checked in step 5).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
  "test_*.py"` reports `OK`, run bare/unpiped as its own tool call, before commit
  (step 4).

BUDGET

5 steps, at the cap declared above for a single-document corpus task.

OPEN

- The issue's own DoD assumes RLS exists ("row-level-security" is the issue's
  title and the target filename), but this codebase's actual mechanism is
  query-level discriminator-column filtering; RLS is documented only as an unbuilt
  future migration gate (`docs/multi-tenant-conformance.md`) and as an axiom in a
  `draft` formal specification with stubbed/ignored tests
  (`docs/multi-tenant-relay.md`). The document names this mismatch explicitly in
  its scope-and-omissions section rather than fabricating RLS usage — a deliberate,
  disclosed scope decision, not an oversight, and not a builder's call to silently
  resolve either way.
- Whether `crates/buzz-relay/src/conformance/mod.rs`'s tracer is wired into the
  current single-community deployment path or only exercised by the future
  multi-tenant integration branch was not fully resolved; it is recorded as an
  INFERENCE with confidence, not asserted as settled FACT.

LEFT OUT

- Re-profiling the whole Postgres datastore (schema inventory, migration
  mechanism, full access-pattern summary) — that is `datastore.md`-shaped future
  work for a `layers/data/postgres/*` overview document, not this task, because
  duplicating `architecture-containers-postgres`'s existing content would violate
  the "one independently maintainable idea" rule.
- Judging or completing the `docs/multi-tenant-relay.md` formal proof or its
  Tamarin/TLA+ models — out of scope for a corpus reference document; only their
  current draft/stubbed status is recorded as fact.
- Deciding whether Postgres RLS *should* be added — a design decision for whoever
  next works the multi-tenant-relay lane, not this document's call.
