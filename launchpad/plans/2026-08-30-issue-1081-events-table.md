# Issue #1081 — corpus node: layers/data/postgres/events-table.md

Stated size: issue #1081 has no explicit Size label (labels: type:task, area:docs, by:agent); overnight corpus-batch-author dispatch brief sets this task's cap -> cap: 5 steps.

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`,
`launchpad/docs/corpus/AGENTS.md`, `launchpad/docs/corpus/templates/data-entity.md`
and `launchpad/docs/corpus/templates/datastore.md` are merged on `origin/launchpad`;
the target file `launchpad/docs/corpus/layers/data/postgres/events-table.md` does not
exist yet. `launchpad/docs/corpus/architecture/containers/postgres.md`
(id `architecture-containers-postgres`) is merged and is a valid `part-of` target.
Issue #1060's sibling node `layers-data-authoritative-data` is NOT a valid
`relationships` target: its PR (#1872) is open/unmerged
(`gh pr view 1872 --repo launchpad-26/buzz` -> `state: OPEN`, `mergedAt: null`), and
a full walk of the checked-out tree at `origin/launchpad` HEAD
`338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5` carries no `layers/` subtree at all yet.

STEP 1 [independent] — Gather evidence. Read `migrations/0001_initial_schema.sql`'s
`events` table definition (range-partitioned by `created_at`, composite PK
`(community_id, created_at, id)`, its 8 indexes, the generated `search_tsv` column
and its privacy-kind exclusion list); `crates/buzz-db/src/event.rs` (`insert_event`'s
`ON CONFLICT DO NOTHING` dedup, `soft_delete_event` /
`soft_delete_by_coordinate` / `soft_delete_event_and_update_thread`'s `deleted_at`
soft-delete, the file header's "AUTH events never stored / ephemeral events never
stored" rule); `crates/buzz-db/src/lib.rs` (`replace_addressable_event`,
`replace_parameterized_event`); `crates/buzz-core/src/kind.rs` (`KIND_AUTH`,
`is_ephemeral`, `is_replaceable`, `is_parameterized_replaceable`);
`crates/buzz-core/src/event.rs` (`StoredEvent`, the relay-side wrapper — cited only
to draw the boundary against the table's own row shape). <- RUNS HERE
done when: every cited symbol/path above has been opened and its relevant lines
recorded for use as an evidence-ledger citation in STEP 3.

STEP 2 [needs 1] — Write front matter: id `layers-data-postgres-events-table` (the
target path's components joined by hyphens, minus `.md`), `type: layers` (this
batch's disclosed override — the data-entity template's own worked reasoning says a
real instance "most plausibly takes `type: implementation`"; this node deliberately
follows the earlier `layers/data/...` batch precedent instead, and states the
override in its own scope-and-omissions section per `standards/taxonomy.md`'s
"say so" rule), `status: draft`, `origin: launchpad`, `audiences: [agent, developer,
reviewer]`, a commit-pinned provenance FACT for `338b4d0cf2dd76cc43964bb717ce9f0a94a
9c7a5`, and exactly one `relationships` entry: `part-of` ->
`architecture-containers-postgres`. No edge to `layers-data-authoritative-data`,
per `AGENTS.md` step 9's merge-target rule.
done when: `launchpad/docs/corpus/layers/data/postgres/events-table.md` exists with
front matter that parses as YAML and contains exactly the fields named above.

STEP 3 [needs 2] — Write the body using the `data-entity` template's six required
sections (Identity, Attributes and shape, Invariants, Relationships to other
entities, Provenance, Storage pointer) applied to the `events` table specifically —
not the `datastore` template, because issue #1081's own DoD bullets ("Defines
identity/key and semantic ownership," "Summarizes fields by meaning," "Defines
relationships, lifecycle and invariants," "Links authoritative migration/schema and
read/write code paths") name exactly the data-entity template's section list, and the
`events` table is Buzz's single central domain entity, not a cross-cutting
storage-technology profile. Every substantive claim gets one `evidence` entry,
classified FACT (source opened) or INFERENCE (with `confidence`). Scope-and-omissions
names: the `type: layers` override, the two unmerged/nonexistent sibling nodes
(`layers-data-authoritative-data`, and any future Postgres datastore node) this node
defers to instead of duplicating, and anything left unverified.
done when: the body contains all six required sections, every claim in it has a
matching `evidence` array entry, and no column type, index, or partitioning detail
already owned by a future datastore node is restated in full.

STEP 4 [needs 3] — Run `python3 launchpad/project-intelligence/corpus/validate.py`
from the worktree root; fix whatever it reports and re-run.
done when: the command exits 0.

STEP 5 [needs 4] — Run `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole, unpiped
command; confirm `OK` in its output. Then, in a separate call, `git add` the plan
file and the corpus node and `git commit -s`. Do not push, do not open a PR — this
task ends at a committed, reviewed worktree.
done when: the unittest run's own output contains `OK`, and `git log -1` on the
worktree branch shows a new commit containing both files.

PARALLEL: none — single file, single worktree, no dependency on sibling batch tasks
beyond the merged-target checks already performed in ALREADY TRUE.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` must report OK before commit. `review-adjudicate` and cross-model final
review are deferred to the batch orchestration step that bundles this branch with its
siblings — not run in this session.

BUDGET: single document, one sitting — no multi-hour scope expected.

OPEN: whether `layers-data-authoritative-data` should later gain a `references` edge
from this node, once its PR (#1872) merges, is left for a follow-up edit — declaring
it now would validate in this worktree but hard-fail against `origin/launchpad`, per
`AGENTS.md` step 9. A builder must not add that edge preemptively.

LEFT OUT: no edge to any datastore node for Postgres's own internal shape (none is
merged yet — `architecture-containers-postgres` is a container-level node, one layer
up, per the datastore template's own boundary section); no attempt to document
`event_mentions` or `thread_metadata` as their own entities (out of scope per issue
#1081's "Out of scope: Creating or materially editing a second hand-authored canonical
corpus document" — named only as related mechanisms, not documented in full); no
resolution of the `.env.example` Typesense-versus-Postgres-FTS discrepancy the
datastore template already recorded as a known gap elsewhere — not this node's
subject.
