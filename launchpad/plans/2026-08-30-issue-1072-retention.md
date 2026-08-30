Issue #1072 — task: document layers/data/object-storage/retention.md

Stated size: issue #1072 has no explicit Size line; the task brief driving this plan explicitly caps it for "one small document" -> cap: 5 steps

ALREADY TRUE

- Repository revision for this plan: `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5` (origin/launchpad tip at fetch time; matches this worktree's `git rev-parse HEAD`).
- Target path `launchpad/docs/corpus/layers/data/object-storage/retention.md` does not exist; the `layers/` directory does not exist anywhere in this worktree's corpus tree at all (`find launchpad/docs/corpus -maxdepth 2` lists no `layers/*` entry) — the two sibling object-storage documents named in the task brief (`blossom-storage.md`, `git-objects.md`) exist only on unmerged sibling task branches (`task/1067-...`, `task/1069-git-objects`, confirmed present as local commits in this shared `.git` but `git merge-base --is-ancestor <sha> origin/launchpad` returns false for both), not on `origin/launchpad` itself.
- Issue #1072's body confirms the target path via its own `corpus-plan:v2 alias:DOC:layers/data/object-storage/retention.md` header comment and its Objective sentence, matching the task brief's guess exactly.
- Because the sibling docs are unmerged, **their ids are not legal `relationships[].target`s for this node** per `AGENTS.md` step 9 (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` must resolve every target). The only object-storage-adjacent id that does resolve on `origin/launchpad` is `architecture-containers-object-storage` (confirmed present at `launchpad/docs/corpus/architecture/containers/object-storage.md`, `id: architecture-containers-object-storage`).
- `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum is `architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion` — `layers` is a real member. Per the batch precedent named in the task brief (#1067, #1069 both chose `layers`, disclosing the tension against `templates/datastore.md`'s own `architecture` suggestion), this node follows the same choice for consistency rather than re-deciding it.
- `launchpad/docs/corpus/templates/datastore.md`'s required sections are the assigned shape; issue #1072's own DoD bullets ("authoritative, derived, cache or transport"; "owned data, key access patterns, lifecycle/retention and consistency"; "tenancy/security boundaries and failure behavior"; "link schema/migrations/code/tests") map onto them, same as the two sibling tasks.
- **This node's actual subject, found by reading source rather than assumed from the filename:** the object-storage layer's retention/lifecycle policy is a real, atomic, well-evidenced concept distinct from either sibling datastore's own internal shape — confirmed by reading `crates/buzz-media/src/bucket_index.rs` and `crates/buzz-deletion/src/lib.rs` this session, not by paraphrasing the sibling docs:
  - `crates/buzz-media/src/bucket_index.rs::tenant_prefixes`'s own doc comment states verbatim: "shared immutable CAS/thumb/probe data is deliberately outside them (fleet-wide physical GC is a separate retention phase)."
  - `crates/buzz-media/src/bucket_index.rs::is_tenant_owned_key` returns `false` for `KeyClass::Blob` and `KeyClass::Thumb` unconditionally — whole-community deletion never targets shared content-addressed blob/thumbnail bytes, only community-scoped sidecar/auxiliary/git-pointer bindings.
  - `crates/buzz-db/src/deletion.rs`'s `DeletionStage` enum has a terminal `RetentionPending` variant, documented as "Logical deletion complete; shared CAS physical expiry is deferred," with `next()` returning `None` for it (no further transition exists in this codebase).
  - `crates/buzz-deletion/src/lib.rs`'s `execute_stage` match arm for `DeletionStage::LogicallyVerified` calls `mark_retention_pending` with a literal recorded policy string: `"member-erasure and fleet-wide shared-CAS GC are out of V1 scope"`.
  - `crates/buzz-media/src/bucket_index.rs::sweep_bucket_taxonomy`, invoked by `crates/buzz-deletion/src/lib.rs` under the operator-invoked `Command::Sweep` (`buzz-admin`'s `deletions.rs` calls `buzz_deletion::run`), is purely observational — its own doc comment states deletion stages "gate on a recent clean sweep instead of re-listing the whole bucket per request," and `Command::Sweep`'s own doc comment states it "never gates submission or destructive progress."
  - `docs/git-on-object-storage.md` (root design doc, lines ~153-157, ~308, ~375) independently states "physical pruning of unreachable packs is a backend retention concern outside this proof boundary" and "object-store deletion remains a separate retention concern outside this proof boundary" — the same no-GC posture, for the git-CAS half of the same bucket.
  - `crates/buzz-relay/src/storage_sweep.rs`'s module doc comment describes an hourly, single-flight, cache-only usage-metrics task, disableable via `BUZZ_STORAGE_METRICS=off`; it has no deletion or expiry side effect and is a different mechanism from `buzz-deletion`'s operator-invoked `Sweep` command (different crate, different trigger, different purpose — usage gauges versus taxonomy-safety evidence).
- This scope is genuinely one independently maintainable idea (what is retained forever vs. what is ever deleted, and why), not a re-description of either sibling datastore's own schema/access-pattern shape — satisfying `AGENTS.md`'s one-node-one-idea rule and avoiding the "second hand-authored canonical document" trap the issue's own DoD warns against.

STEP 1 [independent] <- RUNS HERE — draft front matter and Purpose/Technology sections

Create `launchpad/docs/corpus/layers/data/object-storage/retention.md` with:
- `id: layers-data-object-storage-retention`, `type: layers`, `status: draft`, `origin: launchpad`, `audiences: [agent, developer, operator, reviewer]`.
- Evidence entries for: recorded revision (commit citation); the `type: layers` choice (INFERENCE, disclosing `datastore.md`'s own contrary suggestion, following the #1067/#1069 batch precedent); the no-relationship-to-unmerged-siblings constraint (TEAM_KNOWLEDGE or FACT per how it's framed); the core retention facts found in `bucket_index.rs` and `deletion.rs` above.
- Body: Purpose & scope statement naming this as the retention/lifecycle policy for the *whole* shared object-storage bucket (both the Blossom/media and git-CAS halves), zooming into `architecture-containers-object-storage`, and stating explicitly that it does not restate either sibling datastore's own schema/namespace/access-pattern shape (out of scope, owned by those nodes once merged). Technology & attachment profile section, kept brief (shared `BUZZ_S3_*` config, already owned by the container node).

done when: front-matter parses as YAML; `id` matches path-derived kebab-case; `type` is a legal enum member.

STEP 2 [needs 1] — schema/namespace inventory (retention-relevant only), access-pattern summary

- Namespace inventory kept narrow: which key classes are shared/immutable-forever (`blob`, `thumb`, `packs/`, `manifests/`, `idx/`) versus which are tenant-owned and deletable (`_meta/{community}/`, `_uploads/{community}/`, `repos/{community}/.../pointer`) — cites `tenant_prefixes`, `is_tenant_owned_key`, `is_known_git_shared_key`, `git_pointer_community` in `bucket_index.rs`.
- Access-pattern summary: `crates/buzz-deletion` (whole-community teardown, operator-invoked via `buzz-admin`), `crates/buzz-relay/src/storage_sweep.rs` (hourly read-only usage metrics, no deletion), `sweep_bucket_taxonomy` / `Command::Sweep` (operator-invoked, observational fleet-taxonomy safety evidence, never destructive).

done when: every row cites a real path/symbol inspected this session; the doc is explicit that this is not the sibling docs' full namespace inventory, only the retention-relevant subset.

STEP 3 [needs 2] — operational characteristics (the core of this node): what is retained forever, what is deleted, and why

- No per-object TTL or scheduled expiry anywhere in this codebase, for either the media or git-CAS half.
- Whole-community deletion (`buzz-deletion`) removes only tenant-owned bindings (sidecars, upload records, git pointers) after a write-drain fence; it explicitly never targets shared CAS blob/thumb/pack/manifest bytes.
- `DeletionStage::RetentionPending` is the pipeline's terminal state after `LogicallyVerified`; `mark_retention_pending`'s own recorded policy string states fleet-wide shared-CAS GC is out of V1 scope — this is a deliberate, named non-implementation, not silence.
- `docs/git-on-object-storage.md`'s independent axiom states the same posture for git packs specifically (no writer removes packs; any future pruning sweep must honor a retention window longer than the max hydrate duration).
- The observational `sweep_bucket_taxonomy` / `Command::Sweep` path records evidence and never deletes or expires anything itself.
- Distinguish this from `storage_sweep.rs`'s hourly usage-metrics sweep (a different, non-destructive, cadence-driven task) to head off the natural misreading that "sweep" implies cleanup.

done when: DoD bullets "Describes owned data, key access patterns, lifecycle/retention and consistency semantics" and "States whether the store is authoritative, derived, cache or transport" are each satisfied by a specific, cited sentence, framed for the retention/lifecycle axis specifically (not a restatement of either sibling's full operational-characteristics section).

STEP 4 [needs 3] — tenancy/security boundaries, failure behavior, relationships, evidence-class audit, scope-and-omissions

- Tenancy: retention/deletion is community-scoped for bindings only; shared CAS bytes carry no tenant boundary at all (by design — content-addressed and potentially shared across communities).
- Failure behavior: `bucket_versioning_detected` preflight + post-delete `versioned_keys` check both fail whole-community deletion permanently on a versioned bucket, because delete markers cannot prove logical absence; `sweep_bucket_taxonomy`'s `SweepError::CapExceeded`/`MalformedPage` fail closed rather than silently truncate.
- `relationships: [{type: part-of, target: architecture-containers-object-storage}]` only — no edge to `blossom-storage`/`git-objects` ids, named explicitly as a scope-and-omissions gap (unmerged at authoring time) rather than silently omitted.
- Re-read every evidence entry: FACT only where the cited source was opened this session; INFERENCE for the `type: layers` choice; TEAM_KNOWLEDGE for issue-body-sourced DoD claims.
- Scope-and-omissions: link out to `architecture-containers-object-storage` (container existence/technology), `docs/git-on-object-storage.md` (git-CAS retention axiom, root doc), the not-yet-merged `blossom-storage`/`git-objects` sibling nodes (named as a forward gap to revisit once they merge), and name anything expected-but-unverified (e.g., whether a future fleet-wide GC sweep is planned/scheduled anywhere outside this checkout).

done when: no relationship target is unresolved against `origin/launchpad`; no evidence entry rests only on an `UNVERIFIED` citation shape while classed `FACT`.

STEP 5 [needs 4] — validate, test-gate, commit

- Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until exit 0.
- Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in its own tool call; confirm OK.
- `git add` the plan and the target file; `git commit -s`.

done when: validator exits 0; unittest suite reports OK; exactly one new commit ahead of `origin/launchpad` (or a second small follow-up commit only if forced by a post-commit fix, never an amend).

PARALLEL

None. All five steps edit the same single file sequentially (front matter, then
each body section, then relationships/audit, then validate+commit) and each
depends on the text the previous step wrote, so `[needs N]` chains 1->2->3->4->5
with no independent branch to parallelize.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before commit.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report OK before commit, run alone in its own tool call.
- No second hand-authored canonical corpus document created in this change.
- No `relationships[].target` naming `blossom-storage`/`git-objects` ids, since neither resolves against `origin/launchpad` at this revision.

BUDGET

One document (~200-320 lines including front matter), five steps, single commit. No code changes — corpus content only.

OPEN

- Whether `type: layers` or `type: architecture` is the better long-run fit is not settled anywhere in the corpus today. Resolved by following the #1067/#1069 batch precedent (`layers`, matching the issue's own directory placement) and disclosing the tension in the node's evidence ledger, per `standards/taxonomy.md`'s step-4 disclosure rule. Revisable later without an id change.
- Whether a fleet-wide shared-CAS GC sweep is planned or scheduled anywhere outside this checkout (a private ops repo, a future issue) is not established — named as a gap, not resolved.
- Whether `blossom-storage`/`git-objects` will actually merge with the ids assumed here (`layers-data-object-storage-blossom-storage`, `layers-data-object-storage-git-objects`) is not verified from this worktree — the reference to them in scope-and-omissions is prose only, not a schema-checked relationship, precisely because it cannot be checked yet.

LEFT OUT

- Any edit to `architecture-containers-object-storage.md`, the not-yet-merged `blossom-storage.md`/`git-objects.md`, or `docs/git-on-object-storage.md` — this task only adds the new retention-level node and links out.
- The full schema/namespace inventory or access-pattern summary of either sibling datastore — owned by those nodes, referenced narrowly here only for the retention-relevant subset.
- Any runtime/product code change — this is documentation-only, per the issue's own Out-of-scope section.
