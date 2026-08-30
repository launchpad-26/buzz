# Issue #1086: docs(corpus) — layers/data/postgres/push-tables.md

Stated size: issue has no explicit Size line, so it defaults to the batch's own 5-step cap for a single corpus document -> cap: 4 steps

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and
`launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad`
(HEAD `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`); the target file
`launchpad/docs/corpus/layers/data/postgres/push-tables.md` does not exist yet, and no
`launchpad/docs/corpus/layers/**` path exists on `origin/launchpad` at all (checked via
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`). Two directly
relevant sibling nodes already exist and validate on `origin/launchpad`:
`architecture-containers-push-gateway` (`architecture/containers/push-gateway.md`) and
`architecture-flows-push-notification` (`architecture/flows/push-notification.md`), plus
`architecture-containers-postgres` (`architecture/containers/postgres.md`). Prior batches
of this same run established the precedent that every `layers/data/...` document uses
`type: layers`, not the type its chosen template's own worked example would suggest for
a real instance (`data-entity`'s own reasoning points to `type: implementation`).
`crates/buzz-push-gateway` has its own separate Postgres migration set
(`crates/buzz-push-gateway/migrations/0001_push_gateway_authority.sql`) and its own
`postgres.rs` connection code, confirmed a genuinely separate deployable service/database
from the main relay's own Postgres (`crates/buzz-db/src/migration.rs`'s destructive-lock
test explicitly excludes `buzz-push-gateway/src/postgres.rs` as a distinct migration
runner). The main relay's own `migrations/0015_push_gateway_authority.sql` also creates
byte-identical `push_gateway_*` tables, marked `_operator_global_tables` (deployment-
global, not community-scoped) — a real, named discrepancy, not resolved by this task.

STEP 1 [independent] — gather evidence: read `migrations/0012_push_leases.sql`,
`0013_push_endpoint_state.sql`, `0014_push_lease_fts.sql`, `0018_push_match_queue.sql`,
`0023_push_match_gate.sql` for the three community-scoped push tables (`push_leases`,
`push_wake_outbox`, `push_match_queue`); `crates/buzz-db/src/push.rs` in full for
identity, invariants, and every read/write code path (accept/replace/revoke lease,
enqueue/claim/complete/retry/fail wake, claim/complete/retry match batch, prune, reap);
`crates/buzz-db/src/deletion.rs` for the `EXPECTED_SCOPED_TABLES`/`PURGE_SCOPED_TABLES`
lifecycle entries proving these three tables are community-deletion-scoped and their
FK-safe purge order; `crates/buzz-relay/src/push_runtime.rs` structure for the
matcher/delivery-worker access pattern. Confirm scope boundary: `push_gateway_*` tables
belong to a different concept (the standalone gateway's own authority/session state) and
must not be folded in — cite `architecture-containers-push-gateway` instead of restating
its content.
done when: every migration/source file above has been read in full and its relevant
claims noted for STEP 2's evidence ledger.

STEP 2 [needs 1] — write front matter (id `layers-data-postgres-push-tables`, type
`layers` — explicit precedent override, disclosed in the evidence ledger per
`standards/taxonomy.md`'s disclosure requirement — status `draft`, origin `launchpad`,
audiences `agent`/`developer`/`operator`/`reviewer`) and body, shaped from
`templates/data-entity.md`'s required sections (identity, attributes/shape, invariants,
relationships, provenance, storage pointer) since this document covers three tightly
coupled tables forming one push-notification durable-state entity group, not a single
table's storage mechanics (`templates/datastore.md`'s territory) or a free-standing
procedure. Cover every DoD bullet: identity/key and semantic ownership (community-scoped
composite keys), field summaries by meaning (not restating migration DDL verbatim),
relationships/lifecycle/invariants (community-deletion purge order, generation
monotonicity, active/tombstone CHECK constraint), and links to the authoritative
migrations plus `buzz-db/src/push.rs` read/write paths. Declare `relationships`:
`references` -> `architecture-containers-postgres` (container these tables live in),
`references` -> `architecture-flows-push-notification` (the flow that uses them),
`references` -> `architecture-containers-push-gateway` (explicit boundary: the separate
service/database this document is NOT about) — all three ids confirmed present on
`origin/launchpad`. RUNS HERE.
done when: `launchpad/docs/corpus/layers/data/postgres/push-tables.md` exists with
schema-legal front matter and a body satisfying every DoD bullet in issue #1086.

STEP 3 [needs 2] — validate: `python3 launchpad/project-intelligence/corpus/validate.py`
must exit 0 against the full corpus tree including the new file. Fix and re-run until
clean.
done when: the validator command's exit code is 0.

STEP 4 [needs 3] — commit: run the corpus unittest suite as the sole command in its own
tool call to earn the verification stamp, confirm `OK`, then in a separate tool call
stage and commit the plan file and the new document with `git commit -s`.
done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
-p "test_*.py"` reports OK and a signed-off commit exists on this branch containing both
files.

PARALLEL: none — single file, single task, no dependency on sibling batch documents
(none of which exist on `origin/launchpad` yet, so none are valid relationship targets).

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` must report OK to earn the commit hook's verification stamp.
`review-adjudicate` and the cross-model review pass are deferred to the batch owner's
review before merge — not run here, per this batch's own throughput tradeoff.

BUDGET: single document, ~1-2 hours of agent time; no code changes, no test changes,
no PR opened (isolate/plan/build/verify/commit only, per this task's own scope).

OPEN: whether the main relay's own `push_gateway_*` "operator global" tables
(`migrations/0015_push_gateway_authority.sql`) are a live, load-bearing duplicate of
`buzz-push-gateway`'s separately migrated copy, or historical drift left over from an
earlier co-located architecture, was not resolved here — named as a real discrepancy in
the document's scope-and-omissions section rather than silently picked either way,
matching the boundary this document must not cross into. Also open: whether a
`corpus-standard-taxonomy`-style override note is the expected disclosure shape for the
`type: layers` precedent override, versus a differently-worded convention — followed the
pattern of naming the override plainly in an `INFERENCE`/`FACT` evidence entry, absent a
single canonical example of this exact override in a merged sibling.

LEFT OUT: no runtime/product code change; no second canonical document (push_gateway_*
tables are explicitly out of scope, covered instead by the existing
`architecture-containers-push-gateway` node); no new relationship target invented beyond
the three confirmed-merged ids above; no per-type `layers`-category template (none
exists — `data-entity.md`/`datastore.md` are the closest fits per the issue's own DoD
bullets, used as a structural guide only, with the `type` field overridden per batch
precedent); no PR opened.
