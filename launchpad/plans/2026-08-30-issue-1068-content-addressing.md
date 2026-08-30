# Plan: issue #1068 — document layers/data/object-storage/content-addressing.md

Issue #1068 (launchpad-26/buzz), parent PRD #610 ("data and storage layer corpus
exists"), part of a 42-document batch built as isolated worktrees for later
bundling into batch PRs.

Stated size: issue #1068 carries no explicit Size label; the batch-author task brief states this is "one small document" (one corpus node, single file)  ->  cap: 5 steps

ALREADY TRUE

- `launchpad/docs/corpus/schema/node.schema.json` exists and its `type` enum is
  `architecture, layers, capabilities, platforms, implementation,
  interfaces-events, verification, operations, development, release,
  governance, agent, ingestion` — no `data` value exists, so the correct
  front-matter `type` for a node under `layers/` is `layers`, not `data`.
- The target file `launchpad/docs/corpus/layers/data/object-storage/content-addressing.md`
  does not exist yet; neither does the `layers/` directory at all (confirmed
  `find launchpad/docs/corpus -maxdepth 3 -type d`).
- No per-type template exists yet for a `layers`-typed node — the 25 files
  under `launchpad/docs/corpus/templates/` are all `type: governance`
  meta-documents (concept, datastore, data-entity, component, etc.), not
  themselves `layers`-typed instances, and `AGENTS.md`'s own "Scope and
  omissions" table says per-type templates are "somewhere in #1307-#1351,"
  not landed. The closest structural match by subject is
  `templates/datastore.md` (its "Required sections" and "Evidence
  expectations" mirror #1068's DoD bullets almost verbatim: authoritative/
  derived/cache/transport, owned data, access patterns, lifecycle/retention,
  consistency, tenancy/security, failure behavior, link-not-copy schema).
  This plan follows that template's shape without claiming `type: governance`
  for the instance (the template itself says a real instance takes the
  surface-appropriate enum member — here `layers`).
- On `origin/launchpad`'s corpus tree (`git ls-tree -r --name-only
  origin/launchpad -- launchpad/docs/corpus`), three nodes already exist whose
  ids are safe `relationships` targets: `architecture-containers-object-storage`,
  `architecture-flows-media-upload`, `architecture-flows-media-download`. All
  three already document, in detail, the Blossom media route table, the
  `{sha256}.{ext}` / `{sha256}.thumb.jpg` / sidecar / auxiliary key taxonomy,
  the git pack/manifest/pointer CAS scheme, and the upload/download HTTP flows
  end to end.
- Direct source research (this session, this worktree, HEAD
  `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`) confirms two independent
  content-addressed key families sharing one physical S3-compatible bucket:
  media blobs (`crates/buzz-media/src/upload.rs`,
  `crates/buzz-media/src/bucket_index.rs`) and git packs/manifests
  (`crates/buzz-relay/src/api/git/store.rs`, `docs/git-on-object-storage.md`'s
  axiom A1). A third finding not yet stated in any existing corpus node: the
  raw content-addressed keys in both families carry **no tenant/community
  segment** (`{sha256}.{ext}`, `packs/<sha256>`, `manifests/<sha256>` are
  global), while tenancy is enforced one layer up — the media sidecar
  (`_meta/{community}/{sha256}.json`, gated per-tenant on read via
  `read_sidecar_mime(tenant, ...)` in `crates/buzz-relay/src/api/media.rs`)
  and the git ref pointer (`repos/{community}/{owner}/{repo}/pointer` in
  `crates/buzz-relay/src/api/git/manifest.rs::pointer_key`, whose own doc
  comment states the CAS objects "remain outside that scoped pointer
  namespace"). This is the node's main net-new contribution beyond what the
  three existing nodes already say.
- `python3 launchpad/project-intelligence/corpus/validate.py` is the
  deterministic gate; `python3 -m unittest discover -s
  launchpad/project-intelligence/corpus/tests -p "test_*.py"` is the commit
  gate. Neither has been run yet for this change.

STEP 1  Create the corpus node                                    [independent]  <- RUNS HERE

Create `launchpad/docs/corpus/layers/data/object-storage/content-addressing.md`
(new directories `layers/`, `layers/data/`, `layers/data/object-storage/`)
with schema-valid front matter:

- `id: layers-data-object-storage-content-addressing`
- `type: layers`
- `status: draft`
- `origin: launchpad`
- `audiences: [agent, developer, operator, reviewer]`
- `evidence`: one entry per substantive claim below, classified FACT (source
  opened this session — `upload.rs`, `bucket_index.rs`, `storage.rs`,
  `auth.rs`, `store.rs`, `manifest.rs`, `media.rs`, `docs/git-on-object-storage.md`,
  `migrations/0002_git_repo_names.sql`, `migrations/0006_moderation.sql`),
  INFERENCE with `confidence` (e.g. "no Postgres blob-metadata/refcounting
  table exists" — an absence claim from a `migrations/` grep, not a single
  quotable file), or TEAM_KNOWLEDGE with `provided_by` (issue #1068's DoD
  bullets themselves). Include a commit citation
  (`338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`) as the provenance entry.
- `relationships`: `part-of` -> `architecture-containers-object-storage`
  (this node zooms into one facet of that container's internal shape, the
  same directionality `templates/datastore.md` itself prescribes for a
  datastore-level document); `references` -> `architecture-flows-media-upload`
  and `references` -> `architecture-flows-media-download` (cited for
  supporting flow/verification detail this node does not restate). All three
  targets confirmed present on `origin/launchpad`'s tree in this step's
  research, not merely in this worktree.

Body sections, addressing every DoD bullet from the issue:

1. **Purpose & scope** — what "content addressing" means here (SHA-256-keyed
   bytes across two independent families sharing one bucket), explicit
   boundary against the three existing sibling nodes (link, don't restate
   their route tables / verification flows / key taxonomy prose).
2. **Addressing scheme** — the two key families and their construction sites.
3. **Authoritative / derived / cache / transport**, per object class (media
   blob: authoritative, no DB-backed copy; thumb: derived/regenerable; media
   sidecar: authoritative tenant binding, itself S3-resident not DB; git
   pack/manifest: authoritative, append-only; git idx sidecar: pure cache
   keyed by pack digest; git ref pointer: authoritative mutable
   compare-and-swap value, itself not content-addressed).
4. **Owned data / key-namespace inventory** — a structural table, no DDL.
5. **Access patterns** — write-time hash computation + verification point
   (media: Blossom `x`-tag match at upload, `HashMismatch` on disagreement;
   git: key is constructively the digest, so write-time mismatch is
   impossible by construction — verification instead happens at
   `get_verified`/`get_verified_limited` read time, `DigestMismatch` on
   disagreement); media read path does *not* re-hash, trusts the sidecar gate
   instead (`media.rs`'s own comment: "Storage is not authoritative").
6. **Lifecycle & retention** — no GC/reference-counting exists for orphaned
   media blobs today (documented future "V2" item in `upload.rs`); no
   deletion under the git CAS protocol at all (A1's own stated proof
   boundary — physical pruning is explicitly future, out-of-protocol backend
   work).
7. **Consistency semantics** — create-only writes both families rely on
   (`If-None-Match: *` for git, sidecar+blob dual-existence check for media
   idempotency); a same-content 412 collision is treated as idempotent
   success "by construction" for git; strong read-after-write is an assumed
   backend property (A1/A2 in `docs/git-on-object-storage.md`), not
   independently re-verified by the media path.
8. **Tenancy & security boundaries** — the net-new finding above: raw
   content-addressed keys are tenant-agnostic; tenancy is enforced one layer
   up (media sidecar gate; git's separate, community-scoped pointer
   namespace). State plainly that two different communities uploading
   byte-identical content share the same physical object, and that each
   still needs its own sidecar/pointer entry to read it.
9. **Failure behavior** — `HashMismatch` -> collapses to a generic 401 on
   upload (existing node already documents the auth-oracle rationale, link
   don't repeat); `DigestMismatch` -> hard read-side error for git, "never a
   silent corruption" (quote `store.rs`'s own comment); missing sidecar ->
   generic 404 on media read; CAS `412` -> not an error, the documented
   `LostRace` / idempotent-collision outcome.
10. **Deduplication** — incidental to the addressing scheme, not a designed
    feature; no explicit dedup table on either path.
11. **Scope and omissions**, per `AGENTS.md`'s required shape: what this node
    does not cover (route tables, full auth-event verification chain, HTTP
    error-code mapping — owned by the three linked sibling nodes; the
    `.env.example` Typesense/GC gaps already named in `templates/datastore.md`
    are out of scope here) and what was expected but not independently
    re-verified (whether `moderation_reports.target_blob_sha256` is ever
    queried against the sidecar's own sha256 field at read time — read the
    column definitions, did not trace every call site).

done when: the file exists at the target path with schema-required front
matter fields present, `relationships` limited to the three ids named above,
every body section listed above present, and every substantive claim carries
an `evidence` entry classified FACT/INFERENCE/TEAM_KNOWLEDGE per the rules
just stated.

STEP 2  Validate                                                       [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
worktree root. Fix any reported error (unresolved relationship target,
missing required field, malformed citation shape) and re-run until it exits 0.

done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.

STEP 3  Self-review against the issue DoD                              [needs 2]

Re-read `git diff origin/launchpad -- .` against every DoD checklist line in
issue #1068's body, one at a time. Confirm: exactly one hand-authored
canonical document; no second concept folded in; every evidence entry's cited
source was actually opened this session (spot-check at least the highest-risk
FACT entries — the tenancy-boundary claim and the authoritative/derived
classification table); no relationship target unresolved against
`origin/launchpad`.

done when: every DoD bullet in issue #1068 has been checked against the diff
and either satisfied or explicitly noted as out of scope with a reason, and no
unresolved discrepancy remains.

STEP 4  Earn the commit gate and commit                                [needs 3]

Run, as the sole command in its own step, `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` and confirm `OK`.
Only then stage exactly the plan file and the target corpus document and
commit with `git commit -s`.

done when: the unittest run reports `OK` and a single new commit exists on
`task/1068-content-addressing` containing only the plan file and the target
corpus document.

PARALLEL

None of this batch task's steps are parallelizable with each other — each
depends on the file created in STEP 1. This task itself is one of 42
independent worktrees in the wider batch; those are parallel to each other,
not internally.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
  before self-review (STEP 2, blocking STEP 3).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
  -p "test_*.py"` must report `OK` before the commit (STEP 4) — this is the
  commit gate per the batch task brief, run as a lone command in its own tool
  call.
- No push, no PR — this worktree stops at a local commit for a later
  orchestration step to bundle.

BUDGET

One corpus document (~150-250 lines including front matter), one plan
document, one commit. No code changes, no other files touched.

OPEN

- Whether `moderation_reports.target_blob_sha256` is ever cross-referenced
  against the sidecar layer at read/moderation-action time, or is purely a
  write-once audit column — not traced to every call site this session: named
  as a gap in the node's own "Scope and omissions" rather than resolved here.
- Whether a `layers`-typed per-topic template (distinct from the existing
  `type: governance` `templates/datastore.md`) will later be formalized for
  this `layers/data/object-storage/` directory — #1307-#1351 track per-type
  template work generally; this node is written directly against
  `node.schema.json` in the meantime, per `AGENTS.md`'s stated fallback for
  types with no landed template.

LEFT OUT

- Rewriting or duplicating the route tables, full Blossom auth-event
  verification chain, or HTTP status-code mapping already covered in detail
  by `architecture-containers-object-storage`,
  `architecture-flows-media-upload`, and `architecture-flows-media-download`
  — linked via `relationships`, not restated.
- Any sibling `layers/data/object-storage/*` document (lifecycle policy,
  tenancy policy, etc.) that might belong in this same directory later — out
  of scope for issue #1068, which is content addressing only; a second
  concept discovered while drafting would be filed as its own task per
  `AGENTS.md`'s one-node-one-idea rule, not folded in here.
- Fixing the `.env.example` Typesense-variable staleness or building the
  documented-but-unbuilt V2 media GC job — both are pre-existing repository
  gaps named by evidence already read (`upload.rs`,
  `templates/datastore.md`), not this task's job to resolve.
