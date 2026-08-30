---
id: layers-data-object-storage-git-objects
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "node.schema.json's type field is a closed 13-member enum (architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion), and layers is a real member of it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Issue #1069 assigns this document the path launchpad/docs/corpus/layers/data/object-storage/git-objects.md directly, via its own corpus-plan:v2 alias header comment and its Objective sentence."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1069, read directly via gh issue view"
  - statement: "PRD #602's success criteria enumerate layers as its own distinct surface in the type taxonomy, separate from architecture."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#602 success criteria, read directly via gh issue view"
  - statement: "Parent Feature #610 is titled 'data and storage layer corpus exists' and lists issue #1069 among its 42 child issues."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#610, read directly via gh issue view"
  - statement: "This node uses type: layers rather than templates/datastore.md's own suggested value for a real datastore instance, because issue #1069's own directory assignment (a direct instruction from this task's source, per the TEAM_KNOWLEDGE entries above) is a more concrete signal than that template's speculative reasoning about a hypothetical instance: templates/datastore.md's own evidence ledger states only that a real instance 'most plausibly takes type: architecture' at confidence 0.6, reasoning from container/component template precedent rather than from any path convention. Per standards/taxonomy.md's step-4 rule (disclose an imperfect fit rather than silently pick), this tension is named here rather than resolved unilaterally."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/datastore.md"
      - "launchpad/docs/corpus/standards/taxonomy.md"
    confidence: 0.65
  - statement: "templates/datastore.md's seven required sections (Purpose & scope; Technology & attachment profile; Schema/namespace inventory; Migration/schema-versioning mechanism; Access-pattern summary; Operational characteristics; Scope and omissions) are the template this node follows: reading that template in full shows those seven required sections map directly onto issue #1069's own Definition of Done bullets (see the TEAM_KNOWLEDGE entry near the end of this ledger quoting them), and no template read this session other than datastore.md addresses a running storage technology's own internal shape."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/datastore.md"
    confidence: 0.85
  - statement: "docs/git-on-object-storage.md states 'The manifest pointer is the sole source of truth' for a repository's ref state, and that a derived relay event (kind:30618) is 'never the commit point' -- the object store (packs, manifests, and the CAS pointer) is authoritative, not a cache or derived copy of state held elsewhere."
    entry_class: FACT
    evidence:
      - "docs/git-on-object-storage.md"
  - statement: "crates/buzz-relay/src/api/git/pack_cache.rs's GitPackCache is a process-local, TempDir-backed, byte-bounded cache of immutable pack/index pairs -- a derived, ephemeral read-through cache in front of the authoritative object store, not itself a source of truth; docs/git-on-object-storage.md's v1 deployment architecture section states cache misses, restarts, and evictions 'only affect performance; object storage remains the source of truth'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/pack_cache.rs"
      - "docs/git-on-object-storage.md"
  - statement: "GitStore::new (crates/buzz-relay/src/api/git/store.rs) builds an S3-compatible client: static access_key/secret_key credentials when both are configured, otherwise the AWS default credential chain (env, profile, web-identity/IRSA, container, instance metadata), and rejects a configuration with exactly one of the two keys set as a Config error rather than silently falling back."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs"
  - statement: "crates/buzz-relay/src/config.rs reads BUZZ_S3_ENDPOINT, BUZZ_S3_ACCESS_KEY, BUZZ_S3_SECRET_KEY, BUZZ_S3_BUCKET (default 'buzz-media'), BUZZ_S3_REGION and BUZZ_S3_ADDRESSING_STYLE, and this same configured bucket backs both buzz-media's Blossom storage and the git object store -- GitStore::new takes the addressing style from buzz_media::config::S3AddressingStyle rather than defining a second enum, but constructs its own independent rust-s3 Bucket client distinct from buzz_media::MediaStorage."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-relay/src/api/git/store.rs"
      - ".env.example"
  - statement: "GitStore::content_key computes the key prefix/hex(sha256(bytes)); put_pack writes under prefix packs/ and put_manifest under prefix manifests/, both via a create-only put_immutable that derives the key from the bytes rather than accepting a caller-chosen key, so a 412 collision on write implies (by A1 content-addressing) the existing object already holds the same bytes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs"
  - statement: "GitStore::idx_key_for_pack_digest derives an idx sidecar key as idx/<pack_digest> (not the SHA-256 of the idx bytes themselves), so hydrators can compute the idx location from a manifest's pack keys without changing manifest bytes; a missing idx is treated as a cache miss to be regenerated with git index-pack, not a hydrate failure."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs"
  - statement: "manifest::pointer_key(community, owner, repo) builds the canonical pointer key repos/<community>/<owner>/<repo>/pointer, stripping a trailing .git; this is the single source of truth shared by the write side (cas_publish) and the read side (hydrate). The pack/manifest/idx namespaces are outside this community-scoped subtree and are shared globally by content digest."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/manifest.rs"
  - statement: "manifest.rs's own test same_owner_repo_pointers_do_not_bleed_between_communities pins that the same owner/repo string in two different communities resolves to two different pointer keys -- the community segment in pointer_key is load-bearing for tenant isolation, not incidental."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/manifest.rs"
  - statement: "A Manifest (manifest.rs) has version (must equal MANIFEST_VERSION on read), head (unprefixed symbolic ref), refs (BTreeMap<refname, 40-or-64-char hex oid>), packs (sorted Vec<String> of store keys), and parent (bare 64-char hex digest of the superseded manifest, or None for a repo's first push). Field order is declared significant for canonical JSON."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/manifest.rs"
  - statement: "Manifest::validate() rejects an unsafe refname or head, a malformed oid, too many packs/refs (MAX_MANIFEST_PACKS, MAX_MANIFEST_REFS), a malformed pack key, or a parent carrying a store-key prefix instead of a bare digest -- and writers must call it before canonical_bytes/put_manifest, so an unpublishable manifest cannot CAS-succeed and then 5xx every subsequent clone. Manifest::from_bytes rejects an unrecognized schema version on read. This is the store's schema-versioning and pre-write validation mechanism; there is no separate migration tool because every manifest is a freshly written, versioned, immutable object rather than a mutated schema in place."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/manifest.rs"
  - statement: "hydrate_for_read and hydrate_for_write (crates/buzz-relay/src/api/git/hydrate.rs) are the store's read and write access paths: hydrate_for_read returns Ok(None) when the pointer is absent (caller responds 404) or a materialized HydratedRepo; hydrate_for_write additionally returns the ParentState the workspace was hydrated from, which cas_publish later predicates its CAS on without re-reading the pointer. HydrationOptions bounds max_pack_bytes and max_repo_bytes per request, sourced from crates/buzz-relay/src/config.rs's git_max_pack_bytes (BUZZ_GIT_MAX_PACK_BYTES, default 500 MB) and git_max_repo_bytes (BUZZ_GIT_MAX_REPO_BYTES, default 2x pack bytes = 1 GB)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/hydrate.rs"
      - "crates/buzz-relay/src/config.rs"
  - statement: "cas_publish (crates/buzz-relay/src/api/git/cas_publish.rs) performs the pointer compare-and-swap; a lost race (HTTP 412 from the object store) surfaces as the typed CasError::Conflict { winner_manifest, winner_manifest_key }, distinct from Backend(StoreError), so a ? bubble cannot turn the expected 'lost the race' outcome into a 500. Buzz-relay's transport layer (crates/buzz-relay/src/api/git/transport.rs) has no in-handler retry on this conflict: the client's git process re-pushes, which re-hydrates against the advanced pointer."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/cas_publish.rs"
      - "docs/git-on-object-storage.md"
  - statement: "finalize_push (crates/buzz-relay/src/api/git/transport.rs) is the sole path that builds a push Response, consuming a PushContext; the shared build_git_response helper is also reached by the read-path handlers (info_refs, upload_pack) but those never carry a PushContext, so the publish-before-response fence for a push is a structural, compiler-checked property rather than a convention."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
      - "docs/git-on-object-storage.md"
  - statement: "crates/buzz-relay/src/main.rs runs GitStore::run_conformance_probe (an A1/A3 conformance gate: sequential semantics, an N-way If-Match race, an N-way If-None-Match race, and ETag-token consistency, per store.rs's own ProbeConfig/run_conformance_probe doc comments) before the relay serves git traffic, unless BUZZ_GIT_CONFORMANCE_PROBE is explicitly set to 'false'; probe failure returns an anyhow error that stops relay startup, so a non-conforming object-store backend is refused rather than silently accepted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-relay/src/api/git/store.rs"
  - statement: "crates/buzz-relay/src/config.rs sets these git-store operational defaults, each overridable by its named environment variable: BUZZ_GIT_MAX_PACK_BYTES 500 MB, BUZZ_GIT_MAX_REPO_BYTES 2x pack bytes (1 GB), BUZZ_GIT_PACK_CACHE_MAX_BYTES 5x repo bytes (5 GB), BUZZ_GIT_MAX_REPOS_PER_PUBKEY 100, BUZZ_GIT_MAX_CONCURRENT_OPS 20."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "docs/git-on-object-storage.md's axiom A1 states pack and manifest objects are 'never deleted by the protocol' and that 'physical pruning of unreachable packs is a backend retention concern outside this proof boundary' -- the protocol itself defines no TTL or expiry; any retention/GC sweep is future work the design doc explicitly does not specify."
    entry_class: FACT
    evidence:
      - "docs/git-on-object-storage.md"
  - statement: "transport.rs's GitAuth extractor requires NIP-98 (Authorization: Nostr <base64>) on every git route -- clone and push alike -- per its own module doc comment 'Auth: NIP-98 on all routes (clone + push). No public repos for v1.' Read authorization additionally requires the caller's current active membership in the repository's bound channel; push authorization is enforced by a pre-receive hook that checks channel role plus buzz-protect protection rules parsed from the kind:30617 announcement (crates/buzz-core/src/git_perms.rs), not by the object-store client itself -- GitStore performs no authorization of its own."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
      - "crates/buzz-core/src/git_perms.rs"
  - statement: "crates/buzz-relay/src/api/git/transport.rs maps failures to HTTP status: missing/invalid NIP-98 auth -> 401; caller not a relay/channel member -> 403; an absent pointer or an unbound repository -> 404, deliberately using the same generic body for both cases so an announcement-only repo's existence is not distinguishable from a never-announced one; HydrateError::ResourceLimit -> 413 (PAYLOAD_TOO_LARGE); any other hydrate/store failure -> 500 (INTERNAL_SERVER_ERROR); a CAS lost race is not an HTTP error class handled here but a typed CasError::Conflict consumed before a response is built."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "Repository-name uniqueness is tracked in Postgres, not in the object store: migrations/0002_git_repo_names.sql creates git_repo_names(community_id, repo_id, owner_pubkey, created_at) with primary key (community_id, repo_id), and crates/buzz-db/src/git_repo.rs implements reserve_repo_name / release_repo_name / count_repos_for_owner against it, scoped per community so the same repo name may be independently reserved by different owners in different communities."
    entry_class: FACT
    evidence:
      - "migrations/0002_git_repo_names.sql"
      - "crates/buzz-db/src/git_repo.rs"
  - statement: "crates/buzz-core/src/kind.rs defines KIND_GIT_REPO_ANNOUNCEMENT = 30617 (the announcement event whose tags seed channel binding and protection rules) and KIND_GIT_REPO_STATE = 30618 (the derived ref-state notification built by manifest_event::build_ref_state_event after a successful CAS, per docs/git-on-object-storage.md's Implementation Correspondence section)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "The already-merged sibling node architecture-containers-object-storage states that the same physical S3-compatible bucket backs both buzz-media and git-on-object-storage, and that its own Security implications and Data implications sections summarize the git half only briefly, explicitly deferring 'the full safety argument for this scheme' to docs/git-on-object-storage.md and naming that deferral in its own Scope-and-omissions table -- this node exists to fill exactly that named gap at the datastore level."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/object-storage.md"
  - statement: "The already-merged sibling node architecture-flows-git-push documents the ordered receive-pack interaction sequence (trigger, preconditions, ordered interactions, auth/trust-boundary crossings, failure/abort/rollback behavior) that is this datastore's own write path exercised end to end, making it real supporting context for a reader of this document rather than a citation duplicate."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/git-push.md"
  - statement: "Issue #1069's Definition of Done requires this document to state whether the store is authoritative, derived, cache or transport; describe owned data, key access patterns, lifecycle/retention and consistency semantics; name tenancy/security boundaries and failure behavior; and link schema/migrations/code/tests rather than copying DDL."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1069 definition of done"
relationships:
  - type: part-of
    target: architecture-containers-object-storage
  - type: references
    target: architecture-flows-git-push
---

# Datastore: git objects (packs, manifests, ref pointer) on object storage

## Purpose & scope statement

This node documents the **git object-storage datastore**: the S3-compatible
bucket subtree that holds a Buzz-hosted git repository's pack objects,
manifest objects, and per-repository ref pointer. It zooms into the git half
of the already-merged container-level node
[`architecture-containers-object-storage`](../../../architecture/containers/object-storage.md)
(id `architecture-containers-object-storage`), which names the bucket's
existence, its shared use by Blossom media and git, and a one-line summary of
each — this document is the datastore-level detail that container document
explicitly defers, in its own words: "the full safety argument for this
scheme ... is not repeated here."

**What this document is not.** It does not restate or re-derive the formal
safety proofs of `docs/git-on-object-storage.md` (durability-ordering,
manifest reconstruction, linearizability) — that document is linked, not
duplicated. It is not the ordered request/response flow of one push or clone
— that is [`architecture-flows-git-push`](../../../architecture/flows/git-push.md).
It is not the domain meaning of a git object, ref, or commit — no data-entity
node for that exists in this corpus yet. And it is not the *other* datastore a
git repository touches: `git_repo_names` in Postgres, which owns repository
**name** uniqueness, not object or ref storage — see *Scope and omissions*.

**Authoritative, not derived, not a cache, not a transport.** The object
store's packs, manifests, and per-repository pointer are the sole source of
truth for a repository's ref state. A relay-signed `kind:30618` event is
published as a best-effort derived notification after a successful push, but
it is never the commit point — a ref change exists iff the pointer object was
CAS-swapped, independent of whether or when any event is observed. The one
cache in this picture, `GitPackCache`, is a process-local, byte-bounded,
ephemeral cache of already-durable pack/index pairs sitting in front of the
store — restarts and evictions cost performance only, never correctness or
data.

## Technology & attachment profile

The backend is any S3-compatible object store (AWS S3, or MinIO for local
development) reached through `rust-s3`. `GitStore::new` builds a client from
a bucket name, region, endpoint, and addressing style, with credentials
resolved the same way `buzz-media`'s client resolves them: static
`access_key`/`secret_key` when both are configured (the common MinIO/local
or static-key production shape), otherwise the AWS default credential chain
(environment, shared profile, web-identity/IRSA, container, or EC2 instance
metadata), letting a relay pod use its own IAM role. Configuring exactly one
of the two static keys is treated as a configuration error rather than a
silent fallback.

The attachment point is fully externalized configuration, never a hardcoded
address: `BUZZ_S3_ENDPOINT`, `BUZZ_S3_ACCESS_KEY`, `BUZZ_S3_SECRET_KEY`,
`BUZZ_S3_BUCKET` (default `buzz-media`), `BUZZ_S3_REGION`, and
`BUZZ_S3_ADDRESSING_STYLE` (`path`, for MinIO's bundled DNS, or `virtual`,
for standard S3 and providers such as Railway). **One bucket, two client
constructions.** The same configured bucket backs both `buzz-media`'s
Blossom storage and this git store; `GitStore` reuses `buzz_media`'s
`S3AddressingStyle` enum rather than duplicating it, but constructs its own
independent `rust-s3` `Bucket` client — `buzz-relay` is the only crate that
builds both.

## Schema / namespace inventory

A structural list of the four key shapes actually written under the
configured bucket by `crates/buzz-relay/src/api/git/store.rs` and
`manifest.rs`. All four are namespaced separately from `buzz-media`'s own
key shapes (`{sha256}.{ext}`, `{sha256}.thumb.jpg`, `_meta/...`,
`_uploads/...`, documented in the container-level sibling node).

| Key shape | Structural purpose | Written by |
|---|---|---|
| `packs/<hex sha256 of bytes>` | One content-addressed git pack object. Create-only; the key is derived from the bytes, never chosen by the caller. | `GitStore::put_pack` |
| `manifests/<hex sha256 of bytes>` | One content-addressed manifest object: `version`, `head`, `refs` (refname → hex oid), `packs` (sorted store keys), `parent` (bare digest of the superseded manifest, or none). | `GitStore::put_manifest`, `manifest::Manifest::canonical_bytes` |
| `idx/<pack_digest>` | Best-effort pack-index cache sidecar for `packs/<pack_digest>`, keyed by the pack's own digest rather than the idx bytes' digest, so it is derivable from a manifest's pack list without changing manifest bytes. A miss just means "regenerate with `git index-pack`," not a hydrate failure. | `GitStore::put_idx` / `get_idx` |
| `repos/<community>/<owner>/<repo>/pointer` | The single mutable object per repository: current manifest digest plus ETag, written by conditional PUT. The only key namespace scoped by community; packs/manifests/idx are shared globally by content digest. | `manifest::pointer_key`, `GitStore::put_pointer` / `get_pointer` |

Domain meaning of what a ref, commit, or pack actually represents is not
this document's subject — no data-entity node exists yet for git objects in
this corpus; see *Scope and omissions*.

## Migration / schema-versioning mechanism

There is no schema-migration tool in the Postgres sense, because every
manifest is a freshly written, versioned, immutable object rather than a row
mutated in place. Versioning is per-object: `Manifest` carries a `version`
field that must equal the code's own `MANIFEST_VERSION` constant on read
(`Manifest::from_bytes` rejects any other value), and a bump to that constant
is how an incompatible manifest-shape change would be introduced. Before any
manifest is written, `Manifest::validate()` rejects an unsafe refname or
`head`, a malformed hex oid, too many packs or refs
(`MAX_MANIFEST_PACKS`/`MAX_MANIFEST_REFS`), a malformed pack key, or a
`parent` carrying a store-key prefix instead of a bare 64-hex digest —
pre-CAS rejection exists specifically so an unpublishable manifest can never
CAS-succeed and then 5xx every later clone. The same predicates run again,
symmetrically, on the read side in `hydrate` as defense in depth.

## Access-pattern summary

| Path | Component | Mechanism |
|---|---|---|
| Read (clone/fetch/`info/refs`) | `crates/buzz-relay/src/api/git/hydrate.rs` | `hydrate_for_read` resolves the pointer, verifies and fetches the manifest, GETs each named pack (or serves a fast-path answer from manifest refs alone via `load_manifest_for_read`), and materializes an ephemeral bare repo. `Ok(None)` on an absent pointer signals "repo never existed" to the caller (404). |
| Write (`receive-pack`) | `crates/buzz-relay/src/api/git/hydrate.rs`, `cas_publish.rs`, `transport.rs` | `hydrate_for_write` returns a `(HydratedRepo, ParentState)` pair; `cas_publish` later predicates its CAS on that same `ParentState` without re-reading the pointer, so a concurrent writer that advances the pointer between hydrate and CAS surfaces as a typed `CasError::Conflict`, never a manifest built on stale state. `finalize_push` is the sole path that constructs a push `Response`, gated on a `PushContext` the compiler requires. |
| Cache population | `crates/buzz-relay/src/api/git/pack_cache.rs` | `GitPackCache` is a process-local, `TempDir`-backed, byte-bounded cache of verified-digest pack/index pairs, populated with single-flight coordination (`DashMap<String, Arc<PopulationFlight>>`) so concurrent hydrations of the same pack don't each re-download it. |
| Startup admission | `crates/buzz-relay/src/main.rs` | `GitStore::run_conformance_probe` runs before the relay serves any git traffic, gated off only by explicit `BUZZ_GIT_CONFORMANCE_PROBE=false`. |

No `#[datastore_span]` tracing attribute (the repository's own Postgres-only
datastore-tracing macro, documented on the `architecture-containers-object-storage`
sibling and in `crates/buzz-datastore-tracing`) instruments this store's S3
calls — that instrumentation currently covers Postgres only and its own macro
rejects any other `system` value at compile time. Whether git object-storage
calls should gain equivalent tracing is a decision for whoever next extends
that macro, not a gap this node resolves.

## Operational characteristics

- **Consistency.** Writes are create-only and content-addressed for packs
  and manifests (`If-None-Match: *`), verified by digest on read, so any
  deviation is detectable rather than silently served. The single mutable
  pointer per repository is updated only by conditional PUT
  (`If-Match`/`If-None-Match`), which the relay treats as a linearizable
  compare-and-swap; a `412` response is the protocol's expected "lost the
  race" outcome, not an error condition, and callers never retry a CAS with
  a stale token — a loser re-hydrates against the advanced pointer instead.
- **Admission gate.** `GitStore::run_conformance_probe` empirically checks
  the configured backend against the object-store properties the design
  (`docs/git-on-object-storage.md`) depends on — sequential create/CAS
  semantics, an N-way `If-Match` race, an N-way `If-None-Match` race, and
  ETag-token consistency between the read and write paths — and fails relay
  startup on any phase failure. This is a per-deployment admission decision,
  not a universal proof.
- **Retention.** Pack and manifest objects are never deleted by protocol
  discipline; the design doc states physical pruning of unreachable objects
  is "a backend retention concern outside this proof boundary." No TTL or
  expiry is implemented in this codebase at the recorded revision.
- **Bounded resource use.** Per-request and per-tenant limits are
  configuration, not hardcoded: `BUZZ_GIT_MAX_PACK_BYTES` (default 500 MB),
  `BUZZ_GIT_MAX_REPO_BYTES` (default 1 GB), `BUZZ_GIT_PACK_CACHE_MAX_BYTES`
  (default 5 GB), `BUZZ_GIT_MAX_REPOS_PER_PUBKEY` (default 100),
  `BUZZ_GIT_MAX_CONCURRENT_OPS` (default 20).
- **No advisory lock.** Writer serialization for a single repository is the
  pointer CAS alone; under concurrent same-repo pushes every contender
  hydrates and runs `receive-pack`, and the CAS losers' subprocess work is
  discarded. This is a named, accepted v1 tradeoff (wasted CPU/IO under
  contention), not a correctness gap.

## Tenancy / security boundaries and failure behavior

**Tenancy.** The pointer namespace is the only community-scoped key shape:
`repos/<community>/<owner>/<repo>/pointer`. A test in `manifest.rs`
(`same_owner_repo_pointers_do_not_bleed_between_communities`) exists
specifically to pin that the same owner/repo string in two communities
resolves to two independent pointer cells. Pack, manifest, and idx objects
are **not** community-scoped — they are shared globally, keyed only by
content digest, which is safe because they are immutable and their identity
*is* their content; only the pointer that names which packs/manifest
currently constitute a given repository's refs needs a tenant boundary.
Repository **name** uniqueness is a separate tenancy concern owned by
Postgres (`git_repo_names`, scoped by `community_id`), not by this store —
see *Scope and omissions*.

**Security.** `GitStore` itself performs no authorization — every git HTTP
route requires NIP-98 request signing (`Authorization: Nostr <base64>`) on
both reads and writes, per `transport.rs`'s own module doc comment ("No
public repos for v1"). Read access additionally requires the caller's
current active membership in the repository's bound channel. Push access is
enforced by a pre-receive hook that evaluates channel role plus
`buzz-protect` protection-tag rules parsed from the repository's `kind:30617`
announcement (`crates/buzz-core/src/git_perms.rs`) — "channel role = repo
role" is that module's own summary of the model. Credential handling for the
store's own S3 connection mirrors `buzz-media`: static keys are optional, and
an unset pair falls back to the AWS default chain (including IRSA on EKS),
so a production deployment can avoid long-lived static keys.

**Failure behavior.** `transport.rs` maps failures to HTTP status
deliberately: missing/invalid NIP-98 auth → 401; authenticated but not a
member → 403; an absent pointer or an unbound repository → 404, using the
same generic body for both so a repository's existence cannot be inferred
from which 404 a caller receives; a per-request resource-limit breach
(`HydrateError::ResourceLimit`) → 413; any other hydrate or store failure →
500. A CAS lost race is not surfaced as an HTTP error class at all — it is
the typed `CasError::Conflict`, consumed and turned into a non-fast-forward
git response before any generic error path sees it, exactly because it is
the protocol's expected outcome under contention rather than a fault.

## Links

- Container-level existence and shared-bucket summary:
  [`architecture-containers-object-storage`](../../../architecture/containers/object-storage.md)
- Formal safety specification (durability-ordering, manifest reconstruction,
  linearizability, the object-store axioms, the conformance probe, and the
  TLA+ model): [`docs/git-on-object-storage.md`](../../../../../../docs/git-on-object-storage.md)
- Ordered push interaction sequence:
  [`architecture-flows-git-push`](../../../architecture/flows/git-push.md)
- Code: `crates/buzz-relay/src/api/git/{store.rs,manifest.rs,cas_publish.rs,hydrate.rs,pack_cache.rs,transport.rs}`
- Live end-to-end regression coverage (clone/push/fetch/force-push roundtrip,
  N-way concurrent-push no-fork): `crates/buzz-test-client/tests/e2e_git.rs`
- Repository-name registry (a different datastore, Postgres):
  `migrations/0002_git_repo_names.sql`, `crates/buzz-db/src/git_repo.rs`
- Push-side authorization model: `crates/buzz-core/src/git_perms.rs`
- Event kinds: `crates/buzz-core/src/kind.rs`
  (`KIND_GIT_REPO_ANNOUNCEMENT = 30617`, `KIND_GIT_REPO_STATE = 30618`)

## Scope and omissions

**This node covers** the git object-storage datastore's own internal shape:
what is authoritative versus cached, its key/namespace inventory, its
schema-versioning mechanism, which code paths read and write it, its
operational characteristics, and its tenancy/security/failure behavior.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The object-storage container's existence, shared-bucket summary, and Blossom media's own key taxonomy | `architecture-containers-object-storage` |
| The formal safety proofs (Theorems 1-3, the object-store axioms, the TLA+ model) | `docs/git-on-object-storage.md` |
| The ordered request/response sequence of one push | `architecture-flows-git-push` |
| Repository-name uniqueness (a different datastore, Postgres) | `migrations/0002_git_repo_names.sql`, `crates/buzz-db/src/git_repo.rs` |
| The domain meaning of a git object, ref, or commit | Not yet documented anywhere in this corpus |
| Per-endpoint HTTP request/response schemas beyond the failure-status table above | `ARCHITECTURE.md`, `crates/buzz-relay/src/api/git/transport.rs` |
| The evidence-class contract (FACT/INFERENCE/TEAM_KNOWLEDGE, citation shapes) | `launchpad/docs/corpus/AGENTS.md` |

**No `relationships` beyond the two declared above.** At the checked
revision the only other in-scope, merged candidates this node's evidence
already cites directly by path — `docs/git-on-object-storage.md` (not a
corpus node; it is a root-level design doc, so it cannot be a
`relationships.target`) and `crates/buzz-core/src/git_perms.rs` (source code,
not a corpus node) — are not corpus nodes at all, so no edge to them is
possible; they are linked in prose instead.

**Expected but not verified when this node was written:**

- **Whether `squareup/block-coder-tf-stacks` provisions staging object
  storage as managed AWS S3, or something else.** That repository is private
  and outside this checkout; `architecture-containers-object-storage` names
  the same gap for the bucket generally, and this node inherits it for the
  git subtree specifically without re-verifying anything new.
- **Whether any GC/retention sweep exists for unreachable pack objects.**
  `docs/git-on-object-storage.md` states pruning is future work outside its
  proof boundary; this node did not find an implemented sweep for git
  objects (distinct from `buzz-media`'s unrelated hourly storage-usage
  sweep) at the recorded revision, and did not exhaustively rule one out.
- **Whether `#[datastore_span]` tracing will ever be extended to this
  store's S3 calls.** Named as a real, enforced-today restriction in the
  Access-pattern summary above, not resolved.
