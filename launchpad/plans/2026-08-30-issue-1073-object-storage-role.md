Issue #1073 — task: document layers/data/object-storage/role.md

Stated size: issue #1073 has no explicit Size line; the batch dispatch brief driving this plan caps it explicitly ("this is one small document") -> cap: 5 steps

ALREADY TRUE

- Repository revision for this plan: `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5` (origin/launchpad tip at fetch time, confirmed via `git rev-parse HEAD` in this worktree).
- Target path `launchpad/docs/corpus/layers/data/object-storage/role.md` does not exist; `launchpad/docs/corpus/layers/` does not exist anywhere on `origin/launchpad` yet (`find launchpad/docs/corpus -name "*.md"` in this worktree lists no `layers/*` file at all).
- Issue #1073's body confirms the target path via its own `corpus-plan:v2 alias:DOC:layers/data/object-storage/role.md` header comment and its Objective sentence, matching the batch brief's guess exactly.
- `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum is `architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion` — `layers` is a real member; there is no `data` value, so a node under `layers/` takes `type: layers`.
- Two sibling documents for this same `layers/data/object-storage/` subject exist on the sibling batch branch `origin/task/610-batch-2-data-storage` (not yet merged to `origin/launchpad`): `blossom-storage.md` (id `layers-data-object-storage-blossom-storage`, issue #1067) and `git-objects.md` (id `layers-data-object-storage-git-objects`, issue #1069). Both chose `type: layers` over `templates/datastore.md`'s own `architecture` suggestion and disclosed that tension in their evidence ledgers and scope-and-omissions per `standards/taxonomy.md`'s step-4 rule — this plan follows the same precedent for consistency rather than re-deciding it.
- Both siblings are full per-namespace deep dives (Blossom media vs. git-on-object-storage), each following `templates/datastore.md`'s seven required sections for its own namespace. Neither states the *whole bucket's* role as a single datastore spanning both namespaces — `architecture-containers-object-storage` (the container node) states container-level existence/technology/interfaces only, explicitly deferring datastore-level depth; the two per-namespace siblings each explicitly scope to one namespace only. Issue #1073's own path (`role.md`, not nested under a namespace name) and its DoD checklist — the same four datastore-classification bullets the siblings answered *per namespace* — read as the missing whole-store synthesis: one classification/access/lifecycle/tenancy/failure statement for the object-storage datastore as a whole, linking to (not repeating) the two namespace-level deep dives. This reading is not settled by any authoritative source; it is this plan's own inference from the directory layout and the sibling precedent, and is disclosed as such in the node's own evidence ledger and scope-and-omissions rather than asserted as certain.
- `templates/datastore.md` exists; its "Required sections" (Purpose & scope; Technology & attachment profile; Schema/namespace inventory; Migration/schema-versioning mechanism; Access-pattern summary; Operational characteristics; Scope and omissions) map onto issue #1073's own DoD bullets ("authoritative, derived, cache or transport"; "owned data, key access patterns, lifecycle/retention and consistency"; "tenancy/security boundaries and failure behavior"; "link schema/migrations/code/tests rather than copying DDL") — this is the assigned template, applied at whole-store rather than per-namespace granularity.
- `architecture-containers-object-storage` (type `architecture`, status `draft`) is merged on `origin/launchpad` and is a legal `relationships[].target` per `AGENTS.md` step 9 (confirmed via `find`, not assumed). Its own Scope-and-omissions table does not claim to cover datastore-level classification, so a `part-of` edge from this node does not duplicate it.
- `layers-data-object-storage-blossom-storage`, `layers-data-object-storage-git-objects`, and `layers-data-object-storage-content-addressing` are **not** present on `origin/launchpad` — only on the unmerged `origin/task/610-batch-2-data-storage` branch (confirmed with `git merge-base --is-ancestor <sha> origin/launchpad` returning false for their commits). Per `AGENTS.md` step 9, a `relationships[].target` must resolve against the branch being merged into, not the author's own worktree — so none of the three is a legal relationship target for this node today, even though this node's own prose links to them for a human reader.
- Source verified this session (opened directly, not assumed from the sibling docs' quotes): `crates/buzz-media/src/storage.rs` (`MediaStorage`'s public methods: `put`, `put_file`, `get`, `get_range`, `get_stream`, `head`, `delete`, `head_with_metadata`, `bucket_versioning_detected`, `delete_objects`, `sidecar_key`/`ctx_sidecar_key`, `get_sidecar`/`put_sidecar`, `read_sidecar_mime`, `ping`, `list_page`/`list_prefix_page`); `crates/buzz-media/src/bucket_index.rs` (`KeyClass` enum: `Thumb`, `Blob`, `Sidecar`, `Auxiliary`, `Unknown`, and `classify_key`'s doc comment stating `Unknown` is deliberate, never silently coerced); `crates/buzz-relay/src/api/git/store.rs` (`content_key`, `put_pack`, `IF_NONE_MATCH: "*"` on every CAS write, `CasOutcome::LostRace` on 412 treated as a semantic, non-error outcome); `docs/git-on-object-storage.md` line ~149 ("No deletion under the protocol. Pack and manifest objects are never deleted by the protocol... Physical pruning of unreachable packs is a backend retention concern outside this proof boundary"); `crates/buzz-deletion/src/lib.rs` (`bucket_versioning_detected` preflight check at line 700, `versioned_keys` non-empty check at line 1143, both fail the whole-community delete permanently); `crates/buzz-relay/src/storage_sweep.rs` (`BUZZ_STORAGE_METRICS` kill switch); `migrations/` (grep for `media`/`blob`/`git_object`/`pack` across `migrations/*.sql` finds no dedicated table — only `migrations/0006_moderation.sql`'s `target_blob_sha256` report-target column and `migrations/0002_git_repo_names.sql`'s repo-name registry, neither a storage record for object bytes); `.env.example` line 86 (`# S3-Compatible Object Storage (media + Git/CAS)`, one config block for both consumers); test files confirmed at their real paths — `crates/buzz-media/tests/static_creds_minio.rs`, `crates/buzz-test-client/tests/{e2e_media.rs,e2e_media_extended.rs,e2e_media_video.rs,e2e_git.rs}`.

STEP 1 [independent] <- RUNS HERE — draft front matter and Purpose/Technology sections

Create `launchpad/docs/corpus/layers/data/object-storage/role.md` with:
- `id: layers-data-object-storage-role`, `type: layers`, `status: draft`, `origin: launchpad`, `audiences: [agent, developer, operator, reviewer]`.
- Evidence entries for: recorded revision (commit citation); the `type: layers` choice (INFERENCE, disclosing `datastore.md`'s own contrary `architecture` suggestion, per `taxonomy.md`'s step-4 disclosure rule, matching the two sibling nodes' identical disclosure); the whole-store-versus-per-namespace scoping decision (INFERENCE, disclosing that no authoritative source states this split, per the ALREADY TRUE note above); core technology/attachment facts (shared `BUZZ_S3_*` config, one bucket, two independent client constructions).
- Body: Purpose & scope statement naming `architecture-containers-object-storage` as the container node this zooms into, and stating explicitly this is a whole-store synthesis across both the Blossom and git-CAS namespaces — not a replacement for either namespace's own deep-dive document (linked in prose, not as a `relationships` edge, since neither is merged).

done when: front matter parses as YAML; `id` matches the path-derived kebab-case; `type` is a legal enum member.

STEP 2 [needs 1] — store classification, owned data, key access patterns

- Store classification: authoritative for both namespaces (no SQL table backs either; confirmed by the migrations grep above), citing `storage.rs` and `store.rs`'s own write paths plus the migrations grep as the negative evidence.
- Owned data: a two-row summary (Blossom keys, git-CAS keys) at structural granularity only, explicitly deferring the full five/four-class breakdown to the two namespace documents (linked in prose).
- Key access patterns: which crate/module owns each namespace's client (`buzz-media`'s `MediaStorage` vs. `buzz-relay`'s `api::git::store` — two independent S3 client constructions inside one binary, confirmed already by the container node and re-verified this session).

done when: every row cites a real path/symbol opened this session; no row restates a namespace's internal key-shape table in full (that is the sibling documents' job).

STEP 3 [needs 2] — lifecycle/consistency, tenancy/security, failure behavior

- Lifecycle & consistency: contrast the two namespaces' write/delete posture at the whole-store level — Blossom is create-idempotent with a real (community-scoped, manifest-driven) bulk-deletion path; git-CAS is create-only with **no deletion under the protocol at all** (`docs/git-on-object-storage.md`'s own stated axiom). Both rely on content-addressed keys plus a conditional-write precondition for their respective consistency guarantees (`IF_NONE_MATCH: "*"` for git; a both-exist idempotency check rather than a precondition header for Blossom).
- Tenancy & security boundaries: raw bytes are shared, community-agnostic CAS in both namespaces; the tenant boundary is enforced one layer up in each (Blossom's sidecar read gate; git's community-scoped pointer key) — state this as the one structural pattern both namespaces share, without re-deriving either's full detail.
- Failure behavior: the one behavior worth stating at whole-store granularity that neither namespace document states about the *other* — `crates/buzz-deletion`'s versioning-refusal check (`bucket_versioning_detected`, `versioned_keys`) applies to the shared bucket and would affect both namespaces' operational posture if it ever fired, even though only Blossom currently exercises deletion.

done when: DoD bullets "States whether the store is authoritative, derived, cache or transport" and "Names tenancy/security boundaries and failure behavior" are each satisfied by a specific, cited sentence at whole-store granularity, not a copy of either namespace document's own section.

STEP 4 [needs 3] — relationships, evidence-class audit, scope-and-omissions

- Add `relationships: [{type: part-of, target: architecture-containers-object-storage}]` only — no edge to the three unmerged sibling nodes, per the ALREADY TRUE note above; they are linked in body prose instead.
- Re-read every evidence entry: `FACT` only where the cited source was opened this session; `INFERENCE` for the `type: layers` choice and the whole-store-synthesis scoping decision, both with `confidence` and a visible reasoning trail; no `TEAM_KNOWLEDGE` expected unless a DoD-checklist quote from the issue itself is cited as a claim source.
- Scope-and-omissions: link out to `architecture-containers-object-storage` (container existence/technology), the two unmerged namespace deep-dives by name and prose link (not a `relationships` edge), and `docs/git-on-object-storage.md` (the formal no-deletion axiom). Name what is expected but unverified: whether staging enables S3 bucket versioning (same gap the container doc and both siblings already name), and that this node's own whole-store-versus-per-namespace scoping premise has not been checked against any corpus-wide convention because none exists yet.

done when: no relationship target is unresolved against `origin/launchpad`; no evidence entry rests only on an `UNVERIFIED` citation shape while classed `FACT`.

STEP 5 [needs 4] — validate, test-gate, commit

- Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until exit 0.
- Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in its own tool call; confirm `OK`.
- `git add` the plan and the target file; `git commit -s`.

done when: validator exits 0; unittest suite reports `OK`; exactly one new commit ahead of `origin/launchpad` (or a second small follow-up commit only if forced by a post-commit fix, never an amend).

PARALLEL

None. All five steps edit the same single file sequentially (front matter, then
each body section, then relationships/audit, then validate+commit) and each
depends on text the previous step wrote, so `[needs N]` chains 1->2->3->4->5 with
no independent branch to parallelize.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before commit.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report `OK` before commit, run alone in its own tool call.
- No second hand-authored canonical corpus document created in this change.

BUDGET

One document (~200-320 lines including front matter — shorter than the two
per-namespace siblings, since this node synthesizes rather than re-derives their
depth), five steps, single commit. No code changes — corpus content only.

OPEN

- Whether `type: layers` or `type: architecture` is the better long-run fit is not
  settled anywhere in the corpus today. Resolved the same way both sibling nodes
  resolved it: go with `layers` (the issue's own directory placement, PRD #602's
  surface list, and Feature #610's title all point there) and disclose the tension,
  per `standards/taxonomy.md`'s step-4 rule. Revisable later without an id change.
- Whether a `role.md` document is meant to be a whole-store synthesis (this plan's
  reading) or something narrower is not stated anywhere this session found —
  disclosed as an INFERENCE in the node's own ledger rather than asserted as
  settled. The two sibling `role.md` tasks for postgres (#1087) and redis (#1097)
  are single-technology stores with no analogous namespace split, so they cannot
  confirm or refute this reading; this remains open until a human or a later
  corpus-convention pass settles it.
- Whether staging deploys use a managed AWS S3 bucket or something else for this
  store is not established (owned by the private `squareup/block-coder-tf-stacks`
  repo) — named as a gap, matching the container doc's and both siblings' identical
  disclosure.

LEFT OUT

- Any edit to `architecture-containers-object-storage.md`, or to either unmerged
  namespace sibling (`blossom-storage.md`, `git-objects.md`) — this task only adds
  the new whole-store synthesis node and links out in prose.
- Re-deriving the full key-namespace inventory, migration mechanism, or
  per-endpoint access-pattern table for either namespace — that is each sibling
  document's own job, cited rather than repeated.
- Any runtime/product code change — this is documentation-only, per the issue's own
  Out-of-scope section.
