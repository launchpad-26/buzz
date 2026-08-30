Issue #1069 — task: document layers/data/object-storage/git-objects.md

Stated size: issue #1069 has no explicit Size line; the task brief driving this plan explicitly caps it for "one small document" -> cap: 5 steps

ALREADY TRUE

- Repository revision for this plan: `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5` (origin/launchpad tip at fetch time).
- Target path `launchpad/docs/corpus/layers/data/object-storage/git-objects.md` does not exist; the `layers/` directory does not exist anywhere in the corpus yet (`find launchpad/docs/corpus -name "*.md"` lists no `layers/*` file).
- Issue #1069's body confirms the target path via its own `corpus-plan:v2 alias:DOC:layers/data/object-storage/git-objects.md` header comment and its Objective sentence, matching the task brief's guess exactly.
- `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum is `architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion` — `layers` is a real member.
- `launchpad/docs/corpus/templates/datastore.md` exists and its "Required sections" (Purpose & scope; Technology & attachment profile; Schema/namespace inventory; Migration/schema-versioning mechanism; Access-pattern summary; Operational characteristics; Scope and omissions) map 1:1 onto issue #1069's own Definition-of-Done bullets ("authoritative, derived, cache or transport"; "owned data, key access patterns, lifecycle/retention and consistency"; "tenancy/security boundaries and failure behavior"; "link schema/migrations/code/tests rather than copying DDL"). This is the assigned template.
- The real subject already has a from-scratch formal spec at `docs/git-on-object-storage.md` (root, not corpus) and a working implementation under `crates/buzz-relay/src/api/git/{store.rs,manifest.rs,cas_publish.rs,hydrate.rs,pack_cache.rs,transport.rs}`, inspected this session.
- A merged sibling corpus node already exists at container level: `launchpad/docs/corpus/architecture/containers/object-storage.md` (id `architecture-containers-object-storage`, type `architecture`, status `draft`). It explicitly states the git-CAS design proof is "not repeated here" and points at `docs/git-on-object-storage.md` — this is exactly the gap issue #1069's node fills. Its own Scope-and-omissions table lists "The formal safety proof for git-on-object-storage" as owned by that doc, not by itself.
- A second merged sibling exists at flow level: `launchpad/docs/corpus/architecture/flows/git-push.md` (id `architecture-flows-git-push`, type `architecture`), documenting the `receive-pack` ordered interactions that exercise this datastore's write path end to end.
- Both sibling ids are present on `origin/launchpad`'s actual corpus tree (confirmed by `find`, not assumed), so both are legal `relationships[].target`s per `AGENTS.md` step 9.
- Tenancy boundary confirmed in code: `manifest::pointer_key(community, owner, repo)` builds `repos/<community>/<owner>/<repo>/pointer`, community-scoped; `manifest.rs`'s own test `same_owner_repo_pointers_do_not_bleed_between_communities` pins this. Pack/manifest CAS objects (`packs/<hex>`, `manifests/<hex>`, `idx/<pack_digest>`) are content-addressed and **not** community-scoped (shared globally by digest, per A1 content-addressing).
- Bucket config is shared with Blossom media: `.env.example` / `crates/buzz-relay/src/config.rs` (`BUZZ_S3_ENDPOINT`, `BUZZ_S3_ACCESS_KEY`, `BUZZ_S3_SECRET_KEY`, `BUZZ_S3_BUCKET` default `"buzz-media"`, `BUZZ_S3_REGION`, `BUZZ_S3_ADDRESSING_STYLE`) — one bucket, two independent S3 client constructions (`buzz_media::MediaStorage` and `GitStore::new`).
- Repo-name uniqueness lives in Postgres, not the object store: `migrations/0002_git_repo_names.sql` creates `git_repo_names(community_id, repo_id, owner_pubkey, created_at)`, PK `(community_id, repo_id)`; `crates/buzz-db/src/git_repo.rs` implements reserve/release/count against it.
- Startup fail-closed gate confirmed: `crates/buzz-relay/src/main.rs` runs `GitStore::run_conformance_probe` before serving git traffic unless `BUZZ_GIT_CONFORMANCE_PROBE=false`; probe failure is a fatal `anyhow` error (process does not start).
- Byte/quota limits confirmed in `crates/buzz-relay/src/config.rs`: `BUZZ_GIT_MAX_PACK_BYTES` (default 500 MB), `BUZZ_GIT_MAX_REPO_BYTES` (default 2x pack = 1 GB), `BUZZ_GIT_PACK_CACHE_MAX_BYTES` (default 5x repo = 5 GB), `BUZZ_GIT_MAX_REPOS_PER_PUBKEY` (default 100), `BUZZ_GIT_MAX_CONCURRENT_OPS` (default 20).
- Failure-mode HTTP mapping confirmed in `crates/buzz-relay/src/api/git/transport.rs`: NIP-98 auth failure -> 401; non-member -> 403; unbound/nonexistent repo -> 404 (same generic body for both, to avoid leaking which case applies); `HydrateError::ResourceLimit` -> 413; CAS lost-race -> typed `CasError::Conflict` -> 409; other backend errors -> 500.
- Event kinds: `KIND_GIT_REPO_ANNOUNCEMENT = 30617`, `KIND_GIT_REPO_STATE = 30618` (`crates/buzz-core/src/kind.rs`), matching the design doc's own kind references.

STEP 1 [independent] <- RUNS HERE — draft front matter and Purpose/Technology sections

Create `launchpad/docs/corpus/layers/data/object-storage/git-objects.md` with:
- `id: layers-data-object-storage-git-objects`, `type: layers`, `status: draft`, `origin: launchpad`, `audiences: [agent, developer, operator, reviewer]`.
- Evidence entries for: recorded revision (commit citation); the datastore-template mapping decision; the `type: layers` choice (INFERENCE, disclosing the datastore-template's own contrary `architecture` suggestion per taxonomy.md's disclosure rule); technology/attachment facts (`GitStore::new`, shared bucket config, addressing style).
- Body: Purpose & scope statement (names `architecture-containers-object-storage` as the container-level node this zooms into, and states this is the object-storage half only — not Postgres's `git_repo_names`, not the desktop/CLI git client). Technology & attachment profile section.

done when: front-matter parses as YAML; `id` matches path-derived kebab-case; `type` is a legal enum member.

STEP 2 [needs 1] — schema/namespace inventory, migration mechanism, access-pattern summary

- Namespace inventory table: `packs/<sha256>` (pack objects), `manifests/<sha256>` (manifest objects), `idx/<pack_digest>` (idx cache sidecar), `repos/<community>/<owner>/<repo>/pointer` (mutable CAS pointer). Each row cites `store.rs`'s key-construction functions.
- Migration/schema-versioning: `Manifest::MANIFEST_VERSION`, `Manifest::validate()` pre-CAS rejection, `Manifest::from_bytes` version rejection (`manifest.rs`).
- Access-pattern summary: `hydrate_for_read` / `hydrate_for_write` (`hydrate.rs`), `cas_publish` (`cas_publish.rs`), `GitPackCache` process-local cache (`pack_cache.rs`), `finalize_push` seam (`transport.rs`).

done when: every row cites a real path/symbol inspected this session; no row asserts a table/DDL that isn't there (this is not a Postgres store).

STEP 3 [needs 2] — operational characteristics, tenancy/security, failure behavior

- Operational characteristics: fail-closed conformance probe gate (A1/A3), byte/quota config defaults, no-deletion-under-protocol retention posture (from `docs/git-on-object-storage.md` A1), process-local pack cache eviction being performance-only (not correctness-bearing).
- Tenancy/security: community-scoped pointer key vs. globally-shared content-addressed pack/manifest objects; NIP-98 auth + channel-role-based push authorization (`git_perms.rs`) enforced above the store, not by the store itself; static-vs-IAM credential selection mirroring `buzz-media`.
- Failure behavior: the HTTP status mapping table from `transport.rs`; `CasError::Conflict` (409) as the *expected* concurrent-push outcome, not an error condition; `HydrateError::ResourceLimit` -> 413.

done when: DoD bullets "States whether the store is authoritative, derived, cache or transport" and "Names tenancy/security boundaries and failure behavior" are each satisfied by a specific, cited sentence — not a restatement of the design doc's abstract.

STEP 4 [needs 3] — relationships, evidence-class audit, scope-and-omissions

- Add `relationships: [{type: part-of, target: architecture-containers-object-storage}, {type: references, target: architecture-flows-git-push}]`.
- Re-read every evidence entry: FACT only where the cited source was actually opened this session; INFERENCE for the `type: layers` choice and for the "no deletion under protocol, not the store" retention framing (states an implication, not a directly-read line); no TEAM_KNOWLEDGE expected (issue text itself is not being cited as a claim source here, unlike the template's own ledger).
- Scope-and-omissions: link out to `architecture-containers-object-storage` (container existence/technology), `docs/git-on-object-storage.md` (formal safety proofs), `architecture-flows-git-push` (ordered push interactions), Postgres `git_repo_names` (repo-name uniqueness — a different datastore). Name anything expected-but-unverified (e.g., staging bucket provisioning in the private `block-coder-tf-stacks` repo, same gap the container doc already names).

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

BUDGET

One document (~250-400 lines including front matter), five steps, single commit. No code changes — corpus content only.

OPEN

- Whether `type: layers` or `type: architecture` is the better long-run fit is not settled anywhere in the corpus today — `datastore.md`'s own template guidance (an INFERENCE, confidence 0.6) suggests `architecture` for a real datastore instance, but issue #1069's own assigned path (`layers/data/object-storage/...`), PRD #602's surface list, and Feature #610's title ("data and storage layer corpus exists") all point at `layers`. Resolved by going with `layers` (the issue's own directory placement is the more direct, unambiguous signal) and disclosing the tension in the node's evidence ledger and scope-and-omissions, per `standards/taxonomy.md`'s step-4 disclosure rule. Revisable later without an id change.
- Whether staging deploys use a managed AWS S3 bucket or something else for this store is not established (owned by the private `squareup/block-coder-tf-stacks` repo) — named as a gap, matching the sibling container doc's own identical disclosure.

LEFT OUT

- Any edit to `architecture-containers-object-storage.md`, `architecture-flows-git-push.md`, or `docs/git-on-object-storage.md` — this task only adds the new datastore-level node and links out.
- Postgres `git_repo_names` as its own datastore node — out of scope per issue #1069's Objective (this issue is the object-storage node only); it is referenced, not documented, here.
- Any runtime/product code change — this is documentation-only, per the issue's own Out-of-scope section.
