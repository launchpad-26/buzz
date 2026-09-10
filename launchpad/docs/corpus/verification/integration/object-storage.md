---
id: verification-integration-object-storage
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "buzz-media's MediaStorage wraps an S3-compatible bucket via the rust-s3 crate and exposes put, put_file, get, get_range, get_stream, head, head_with_metadata, delete, delete_objects, preflight_version_listing, delete_object_versions, list_page, list_prefix_page and list_prefix_versions_page, among others."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/src/storage.rs:220-561"
  - statement: "crates/buzz-media/tests/static_creds_minio.rs exercises a live round trip of MediaStorage's static-credential path against a real S3-compatible service -- PUT, HEAD (existence and size via head_with_metadata), GET (byte-for-byte round trip), DELETE, then HEAD reporting absence -- and its single test, static_creds_round_trip_against_minio, is annotated #[ignore = \"requires a live MinIO (docker compose up -d minio minio-init)\"]."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/tests/static_creds_minio.rs:1-19"
      - "crates/buzz-media/tests/static_creds_minio.rs:49-80"
  - statement: "crates/buzz-media/tests/versioned_minio.rs carries two #[ignore]-annotated tests -- never_versioned_bucket_lists_null_versions_and_exact_delete_empties_listing and versioned_bucket_exact_version_delete_reaches_final_list_versions_emptiness -- each creating and destroying its own throwaway bucket against docker-compose MinIO, covering: null-version listing/deletion on a never-versioned bucket; paginated ListObjectVersions across historical versions and delete markers on a versioned bucket; exact (key, version_id) deletion; idempotent retry of an already-deleted version; and, when the local MinIO supports it, behavior after `mc version suspend`."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/tests/versioned_minio.rs:1-17"
      - "crates/buzz-media/tests/versioned_minio.rs:130-363"
  - statement: "Neither static_creds_minio.rs nor versioned_minio.rs is selected by any GitHub Actions workflow: no occurrence of \"buzz-media\" appears in any .github/workflows/*.yml file at the recorded revision."
    entry_class: FACT
    evidence:
      - "grep_repo('buzz-media', '.github/workflows/*.yml') -> no matches at commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "scripts/run-tests.sh's run_integration_tests function, which just test and CI's integration-test path invoke, runs `cargo test --test '*'` for workspace integration tests with no --ignored flag, so buzz-media's #[ignore]-annotated static_creds_minio and versioned_minio test binaries are compiled and their tests discovered but every case inside them is skipped as ignored, never executed, by that path."
    entry_class: FACT
    evidence:
      - "scripts/run-tests.sh:127-145"
  - statement: "root TESTING.md documents `just test` as running unit tests plus integration tests against Postgres and Redis, and documents buzz-test-client's e2e suites (relay-backed, #[ignore]-gated) separately; it names no MinIO or S3-specific integration-test requirement anywhere in its 354 lines."
    entry_class: FACT
    evidence:
      - "TESTING.md:1-20"
  - statement: "docker-compose.yml defines a minio service (image minio/minio:latest, container buzz-minio, S3 API on host port 9000, console on 9001) and a minio-init service that creates and anonymizes a buzz-media bucket via `mc`; both static_creds_minio.rs and versioned_minio.rs default their endpoint/credentials/bucket to this same local MinIO."
    entry_class: FACT
    evidence:
      - "docker-compose.yml:103-146"
      - "crates/buzz-media/tests/static_creds_minio.rs:24-47"
  - statement: "buzz-relay's own git-on-object-storage code path (crates/buzz-relay/src/api/git/store.rs) carries a separate, structurally different live-backend verification mechanism: a #[cfg(test)] mod probe of four #[tokio::test] functions (probe_412_surfacing, probe_full_roundtrip, probe_conformance, probe_get_exposes_etag), each gated at runtime by a probe_enabled() check on BUZZ_GIT_S3_PROBE=1 (a silent early return, not #[ignore]) rather than by cargo's ignore mechanism."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs:1019-1214"
  - statement: "crates/buzz-relay/src/main.rs runs GitStore::run_conformance_probe -- the same function mod probe's probe_conformance test calls directly -- against the relay's actually-configured S3-compatible backend on every relay startup, gated by BUZZ_GIT_CONFORMANCE_PROBE (default true, i.e. on unless explicitly set to \"false\"), with a comment stating failure is fatal because a backend that cannot satisfy pointer CAS invalidates the manifest-pointer protocol, and calling this 'a deployment gate, not a proof.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:489-525"
  - statement: "ci.yml's backend-integration job starts the relay binary with BUZZ_GIT_PROBE_WRITERS=8 set and does not set BUZZ_GIT_CONFORMANCE_PROBE=false, and that job's relay-startup step polls /_readiness and fails the job if the relay process exits before becoming ready -- so the git-on-object-storage startup conformance probe against the job's live MinIO container runs, and gates, on every run of that CI job, independent of and not selecting either buzz-media test file."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:604-650"
      - ".github/workflows/ci.yml:715-750"
  - statement: "No corpus node exists yet, on origin/launchpad's corpus tree at the recorded revision, in a launchpad/docs/corpus/verification/ subtree at all -- the only nodes present outside schema/ are under agents/, architecture/, capabilities/, development/, layers/, standards/ and templates/ -- so no verification-e2e-media (or similarly named) sibling node exists to declare a relationship toward."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> no verification/ path present; top-level subdirectories are agents/, architecture/, capabilities/, development/, layers/, schema/ (excluded from validation), standards/, templates/"
  - statement: "crates/buzz-test-client/tests/e2e_media.rs's own module doc-comment states it requires 'relay running at localhost:3000, MinIO running at localhost:9000' and that all its tests are #[ignore]; unlike buzz-media's own storage-layer tests, e2e_media.rs (with e2e_media_extended and e2e_media_video) is explicitly selected and run --ignored in ci.yml's backend-integration job, so the full relay-HTTP media flow has a materially stronger CI enforcement level than the storage-layer tests this node documents."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_media.rs:1-14"
      - ".github/workflows/ci.yml:907"
  - statement: "No live-MinIO integration test exercises buzz-media's AWS-default-credential-chain (IRSA/environment/shared-profile/instance-metadata) path -- the only fallback branch of MediaStorage::new when s3_access_key/s3_secret_key are unset -- because static_creds_minio.rs and versioned_minio.rs are the only test files under crates/buzz-media/tests/ that touch a live S3-compatible service, and both hardcode a static access key and secret key."
    entry_class: FACT
    evidence:
      - "crates/buzz-media/tests/static_creds_minio.rs:24-37"
      - "crates/buzz-media/tests/versioned_minio.rs:28-38"
  - statement: "The git-on-object-storage startup admission gate is a better structural fit for this corpus's invariant template (#1343) than for the test-contract template this node is built from, because it is a production-path admission check enforced at every relay boot rather than a test invoked by a test harness, and the test-contract template's own boundary section names exactly this shape -- 'an invariant whose sole enforcement tier is test-enforced' -- as the closest neighboring case, distinguishing it by which node the obligation lives in."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/test-contract.md"
      - "crates/buzz-relay/src/main.rs:489-525"
    confidence: 0.6
---

# Object storage integration — test contract

## Purpose and boundary

This node documents one obligation: that `buzz-media`'s `MediaStorage` S3 client
performs its core object operations correctly against a **real, live
S3-compatible backend**, not only against in-process assertions. It covers
only the storage-layer integration tests that call `MediaStorage` directly.
It does **not** cover the full Blossom HTTP flow through the relay (upload,
get, head requests, BUD-11 auth) -- that is a distinct obligation belonging
to an `e2e`-level node once one is authored (see *Scope and omissions*) --
and it does not cover the git-on-object-storage code path's own live-backend
verification, which is a structurally different mechanism named below rather
than folded in.

## Obligation

> `buzz-media`'s `MediaStorage` client performs a correct static-credential
> PUT/HEAD/GET/DELETE round trip, and correct version-aware listing and
> exact-`(key, version_id)` deletion of object versions and delete markers
> across both never-versioned and versioned buckets, against a real
> S3-compatible object-storage backend.

## Verifying test(s)

- `crates/buzz-media/tests/static_creds_minio.rs` --
  `static_creds_round_trip_against_minio` -- puts an object with static
  credentials, confirms existence and size via `head`/`head_with_metadata`,
  confirms `get` round-trips the exact bytes, then confirms `delete` followed
  by `head` reports absence. Exists specifically to prove that adding the
  AWS-default-credential-chain fallback did not regress the static-key path.
- `crates/buzz-media/tests/versioned_minio.rs` --
  `never_versioned_bucket_lists_null_versions_and_exact_delete_empties_listing`
  -- covers listing and exact-version deletion of a `null`-version object on a
  bucket with versioning never enabled.
- `crates/buzz-media/tests/versioned_minio.rs` --
  `versioned_bucket_exact_version_delete_reaches_final_list_versions_emptiness`
  -- covers paginated `ListObjectVersions` across historical object versions
  and delete markers, exact-version deletion, idempotent retry of an
  already-deleted version, and (opportunistically, when the local MinIO
  supports it) behavior after `mc version suspend`.

## How to run it

```bash
docker compose up -d minio minio-init
cargo test -p buzz-media --test static_creds_minio -- --ignored --nocapture
cargo test -p buzz-media --test versioned_minio -- --ignored --nocapture
```

Both test files default their endpoint, credentials and bucket to the
docker-compose MinIO service (`http://localhost:9000`, `buzz_dev` /
`buzz_dev_secret`), overridable via the same `BUZZ_S3_*` environment
variables the relay itself reads. `versioned_minio.rs` additionally shells
out to `docker exec <container> mc` (container name overridable via
`BUZZ_MINIO_CONTAINER`, default `buzz-minio`) to create/enable-versioning/
remove its own throwaway buckets, so it also requires the `minio/mc` image
the docker-compose `minio-init` service already uses to be reachable via
`docker exec` on the running `buzz-minio` container.

## Current enforcement status

**Gated.** Both tests exist, are annotated `#[ignore]` with a reason naming
the live-MinIO requirement, and are not selected by any automated path in
this repository:

- `scripts/run-tests.sh`'s `run_integration_tests` function -- what `just
  test`'s integration half and any CI job invoking it would run -- calls
  `cargo test --test '*'` with no `--ignored` flag, so these two test
  binaries compile and their cases are discovered and reported `ignored`,
  never executed.
- No occurrence of `buzz-media` appears anywhere in
  `.github/workflows/*.yml` at the recorded revision -- unlike
  `crates/buzz-test-client/tests/e2e_media.rs` (the full relay-HTTP media
  flow), which **is** explicitly selected with `--ignored` in `ci.yml`'s
  `backend-integration` job. The storage-layer obligation this node
  documents therefore has a materially weaker enforcement level than the
  HTTP-flow obligation neighboring it.

Running these tests today requires a developer (or an agent) to explicitly
bring up `docker compose up -d minio minio-init` and pass `--ignored` by
hand. Nothing currently re-runs them on a schedule or on a change to
`crates/buzz-media/src/storage.rs`.

## Limits

- These tests exercise `MediaStorage` directly, in-process, calling its Rust
  methods -- they do not go through the relay's HTTP media routes, Blossom
  BUD-11 auth, or content-type validation. A pass here says nothing about
  the HTTP surface; that is a distinct obligation (see *Scope and
  omissions*).
- `static_creds_minio.rs` only exercises the static-access-key/secret-key
  credential path. No live-MinIO test exercises `MediaStorage::new`'s
  AWS-default-credential-chain fallback (environment, shared profile,
  web-identity/IRSA, container, instance metadata) -- both live tests
  hardcode static credentials. A relay pod configured to rely on its IAM
  role rather than static keys has no integration coverage of that path.
- Both tests run only against local, single-node docker-compose MinIO. They
  are not run, by this obligation, against a managed cloud S3-compatible
  provider (AWS S3, Railway Storage Buckets) -- the object-storage
  architecture container node records that the Helm chart's production
  profile targets exactly such an external service, with no
  chart-side credential generation, and that path is unexercised here.
- Neither test touches `MediaStorage`'s sidecar/auxiliary key namespacing
  (`_meta/{community}/{sha256}.json`, `_uploads/{community}/{sha256}/{ulid}.json`),
  the `list_page`/`list_prefix_page` pagination the storage sweep uses, or
  thumbnail generation -- those code paths in `crates/buzz-media/src/storage.rs`
  and `bucket_index.rs` are not exercised by either verifying test.
- A passing run proves these specific operations worked against whatever
  MinIO state existed at run time; it does not prove the operations are
  correct under concurrent access from multiple relay pods, which neither
  test attempts.

## Scope and omissions

**This node covers** buzz-media's `MediaStorage` live-integration test pair
(`static_creds_minio.rs`, `versioned_minio.rs`): what they verify, how to run
them, and their actual (gated, not CI-enforced) status.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full Blossom HTTP media flow (upload/get/head through the relay, BUD-11 auth) exercised by `crates/buzz-test-client/tests/e2e_media.rs`, `e2e_media_extended.rs` and `e2e_media_video.rs` | A future `verification`-typed e2e-media node. None exists on `origin/launchpad`'s corpus tree at the recorded revision (no `launchpad/docs/corpus/verification/` subtree at all), so no `relationships` edge is declared toward it -- see *Relationships* below. |
| The git-on-object-storage live-backend verification mechanism: `crates/buzz-relay/src/api/git/store.rs`'s `mod probe` (manual, `BUZZ_GIT_S3_PROBE=1`-gated tests) and the always-on-by-default startup admission gate in `crates/buzz-relay/src/main.rs` that runs the same `run_conformance_probe` logic on every relay boot, including inside `ci.yml`'s `backend-integration` job | Not this node. This is a structurally different obligation -- a production admission gate, not a conventional `#[ignore]`-gated test -- and per the test-contract template's own boundary section reads as a closer fit for the corpus's invariant template (#1343) than for this one. Named here as a second, distinct obligation for a future task rather than folded in. |
| The AWS-default-credential-chain / IRSA fallback path in `MediaStorage::new` | Nobody yet -- no live-MinIO test exercises it. Named as a real coverage gap, not merely an omission of this document. |
| The object-storage container's full responsibility, technology and deployment picture (both media and git halves) | `launchpad/docs/corpus/architecture/containers/object-storage.md` |
| The general corpus rules for citing a test as evidence | `launchpad/docs/corpus/standards/test-references.md` |
| Production-scale behavior (large buckets, `storage_sweep.rs`'s `max_objects`/`timeout` boundaries, concurrent multi-pod access) | Not established by either verifying test; also named as an unverified gap by `architecture-containers-object-storage`. |

**No `relationships` are declared.** Checked immediately before finalizing
this front matter, against the branch this node is authored to merge into,
not this worktree:

```bash
git fetch origin launchpad
git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus
```

At the recorded revision this returns no path under
`launchpad/docs/corpus/verification/` at all -- the corpus's `verification`
surface is otherwise empty on `origin/launchpad`. The one plausible target,
`architecture-containers-object-storage`, is a real, loadable id (it
describes the same S3-compatible bucket this node's tests exercise), but a
`references` edge to an `architecture`-typed container node from a
`verification`-typed test-contract node would name a domain relationship the
`relationships.schema.json` vocabulary (`depends-on`, `supersedes`,
`implements`, `references`, `part-of`) does not obviously fit without
guessing at directionality this node's task does not ask it to settle, and
no sibling `verification`-typed node exists yet to make `implements` or
`part-of` meaningful. This is a deliberate omission, not a claim that
nothing exists to point at -- the first sibling `verification` node, or a
considered decision about the container edge, is the point to revisit it.

**Expected but not verified when this node was written:**

- **Whether these two tests currently pass.** They were read in full and
  their `#[ignore]` gating and CI non-selection were confirmed structurally,
  but they were not executed against a live MinIO as part of authoring this
  node -- no MinIO instance was running in this worktree. Their "current
  enforcement status" above is about whether they *run automatically*, which
  was established; whether they *currently pass* when run by hand was not.
- **Whether `squareup/block-coder-tf-stacks`' staging deployment of the
  relay's Helm chart exercises either test.** That repository is private and
  not part of this checkout; `architecture-containers-object-storage`
  already records this same gap for the container generally.
- **Whether any non-CI, non-`run-tests.sh` automation (a cron job, a
  release-gate script) invokes either test with `--ignored`.** Only the
  repository's own committed CI workflows and `scripts/run-tests.sh` were
  checked; an out-of-repository trigger was not ruled out, only not found.
