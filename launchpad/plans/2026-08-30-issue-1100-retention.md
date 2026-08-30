# Issue #1100 — layers/data/retention.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and `launchpad/docs/corpus/AGENTS.md` are
merged on `origin/launchpad`, along with `architecture/containers/{postgres,redis,object-storage}.md`
(ids `architecture-containers-postgres`, `architecture-containers-redis`,
`architecture-containers-object-storage`) and `templates/{reference,datastore}.md`. No `layers/` directory
exists yet on `origin/launchpad` (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`
lists none), so `launchpad/docs/corpus/layers/data/retention.md` does not exist. Two sibling
retention/lifecycle documents exist only on **unmerged** batch branches — `layers/data/object-storage/retention.md`
(#1072, id `layers-data-object-storage-retention`, PR #1874, scoped to the object-storage bucket's own
retention mechanism) and `layers/data/data-lifecycle.md` (#1062, id `layers-data-data-lifecycle`, PR #1872,
scoped to the phase structure an individual event/channel/community passes through) — both read in full
this session. Neither is a legal `relationships` target (not on `origin/launchpad`), and neither is
restated here.

STEP 1  [independent, done this session] Evidence gathered: `templates/reference.md` fits this issue's DoD better than
`templates/datastore.md` — datastore.md is explicitly scoped to *one* running datastore instance, but this
issue is a cross-cutting synthesis spanning Postgres, Redis, and object storage. Real retention mechanisms
found and cited: Postgres — soft-delete tombstones retained indefinitely by default (`crates/buzz-db/src/event.rs`),
two narrow hard-purge exceptions for `kind:30078`/`kind:30003` (`migrations/0007_nip_rs_retention.sql`,
`migrations/0019_mesh_status_retention.sql`), ephemeral-channel TTL archival not deletion
(`migrations/0022_event_ttl_refresh.sql`, `migrations/0024_event_ttl_refresh_shared_lock.sql`,
`crates/buzz-db/src/channel.rs`), append-only audit log purged only by whole-community deletion
(`crates/buzz-audit/src/service.rs`). Redis — every key is either TTL-bound (`crates/buzz-pubsub/src/presence.rs`
180s, `crates/buzz-pubsub/src/rate_limiter.rs` EXPIRE, `crates/buzz-pubsub/src/cache_invalidation.rs` 10s
fallback, `crates/buzz-auth/src/nip98_replay.rs` 120s floor) or rebuilt on demand — nothing in Redis is a
durable system of record. Object storage — no per-object TTL exists in this codebase (confirmed independently
in #1072's own evidence, not restated). Whole-community deletion (`crates/buzz-db/src/deletion.rs`,
`crates/buzz-deletion/src/lib.rs`) is the one mechanism that actually removes retained data across all
three, ending in Postgres physical purge + Redis `SCAN`/`UNLINK` namespace purge + tenant-owned object-storage
binding removal — shared CAS bytes are never removed by any code path here (per #1072).

STEP 2  [needs 1] ← RUNS HERE. Write front matter: id `layers-data-retention`, `type: layers` (an INFERENCE-disclosed
override of `templates/datastore.md`'s own `type: architecture` suggestion for a real instance node, per the
same precedent #1072/#1062 already recorded and disclosed for this exact `layers/data/**` subtree), `status:
draft`, `origin: launchpad`, `audiences: [agent, developer, operator, reviewer]`, `evidence` per the FACT/
INFERENCE/TEAM_KNOWLEDGE contract, and `relationships: [references → architecture-containers-postgres,
references → architecture-containers-redis, references → architecture-containers-object-storage]` (all three
merged on `origin/launchpad`; `references`' directionality — "source cites target as supporting context" —
fits a cross-cutting retention synthesis pointing at each container's own existence-level document). Write
the body on `templates/reference.md`'s shape: Reference description (one-sentence definition + scope),
structured entries (one row per datastore: mechanism, default duration, what actually removes data),
Boundary (not #1072's object-storage-internals-depth, not #1062's per-event lifecycle-phase detail — named
in prose, no relationship edge since both are unmerged), Relationships, Scope and omissions.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until it
exits 0.

STEP 4  [needs 3] Run the corpus unittest suite (`python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"`) as the sole command in its own call to earn the
verification stamp, then commit the plan + document in a separate call. No push, no PR — the batch owner
bundles this branch with sibling #1101 afterward.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. The corpus unittest suite
must report OK, run bare and unpiped. `review-adjudicate` and the cross-model final review pass are deferred
to the batch owner's later review — not run here. `check-plan.sh` was attempted (see OPEN below).

BUDGET: small — one document, no code changes; evidence gathering scoped to ~15 source/migration files
already read this session plus two sibling unmerged corpus documents read for scope-boundary purposes only.

OPEN: `check-plan.sh` was searched for at `/home/serina/.claude/skills/plan-issue/check-plan.sh` and via
`find ~/.claude/skills ~/.claude/plugins -iname check-plan.sh` — not found anywhere on this machine, so it
could not be run at all (not merely a format mismatch). Proceeding by hand, per the task brief's own
instruction that a mechanical checker/format mismatch (or, here, absence) should not distort a lightweight
corpus-doc plan's actual content. — Whether `type: layers` versus `templates/datastore.md`'s own
`type: architecture` suggestion is the durably correct choice for this subtree remains unsettled corpus-wide
(same open question #1072/#1062 already recorded); this plan follows the established local precedent for
`layers/data/**` rather than re-litigating it.

LEFT OUT: No restatement of #1072's object-storage retention detail (bucket key-shape table, deletion-pipeline
audit trail) or #1062's per-event lifecycle-phase detail (soft-delete/tombstone mechanics, the two hard-purge
kinds' full reasoning, whole-community deletion's full stage machine) — both are named in prose with no
relationship edge, since neither is merged. No new relationship edges beyond the three `references` to merged
architecture-container nodes — no edge to `corpus-template-reference` (optional per that template, skipped
for the same reason sibling nodes in this batch skip it: the node's own shape already shows which template it
followed). No code or configuration changes — this task is documentation-only.

CHECKER NOTE: `check-plan.sh` (found at `/home/serina/.claude/skills/plan-issue/check-plan.sh`) was run
against this plan and against a merged precedent plan
(`launchpad/plans/2026-08-28-issue-698-corpus-doc.md`) for comparison. Both fail identically on "no cap
found — expected 'Stated size: ... -> cap: N steps'" and "no `done when:`" — issue #1100's own body carries
no Size line to derive a cap from (this corpus-doc issue shape never has one), and per-step `done when:`
lines are not part of how any merged corpus-doc plan in this batch is written. Per the task brief's own
instruction, this mechanical mismatch is disclosed rather than used to distort the plan's actual content;
the plan otherwise passes every structural section check and reports exactly one RUNS HERE marker.
