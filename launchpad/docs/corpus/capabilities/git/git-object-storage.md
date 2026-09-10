---
id: capabilities-git-git-object-storage
type: capabilities
status: draft
origin: launchpad
audiences:
  - developer
  - operator
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "Buzz's git hosting has no persistent per-repo filesystem: repository content (packs, manifests, ref pointers) is stored on an S3-compatible object store, and every git HTTP request hydrates an ephemeral working tree from the published manifest rather than reading a bare repo from disk."
    entry_class: FACT
    evidence:
      - "docs/git-on-object-storage.md"
      - "crates/buzz-relay/src/api/git/store.rs"
  - statement: "Pack and manifest objects are content-addressed: their store key is the SHA-256 hex digest of their own bytes (`content_key`, used for the `packs/<hex>` and `manifests/<hex>` namespaces), and writes use an `If-None-Match: *` create-only precondition so a given key is never overwritten."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs"
  - statement: "A manifest is a JSON document with five fields in a fixed declared order (`version`, `head`, `refs`, `packs`, `parent`); `refs` is a `BTreeMap<String, String>` (ref name to 40-or-64-char hex oid) and `packs` is sorted ascending before serialization, so `canonical_bytes()` is deterministic and `key == sha256(bytes)` holds by construction."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/manifest.rs"
  - statement: "`Manifest::validate()` rejects, before any object-store write, a manifest whose `head` is empty, whose ref names or oids are malformed, whose `parent` is not a bare 64-char hex digest, or whose pack/ref counts exceed the bounded limits (`MAX_MANIFEST_PACKS = 128`, `MAX_MANIFEST_REFS = 10_000`) — turning a would-be un-clone-able manifest into a push-time 4xx instead of a silently broken published state."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/manifest.rs"
  - statement: "The current state of one repository is a single mutable pointer object at a community-scoped key (`repos/<community>/<owner>/<repo>/pointer`, via `pointer_key`), holding the digest of the current manifest; a push commits by writing that pointer through an S3 conditional PUT used as compare-and-swap — `If-Match: <etag>` when a pointer already exists, `If-None-Match: *` for a repo's first push — and a `412` response from that PUT is the protocol's normal \"lost the race\" outcome (`CasOutcome::LostRace`), not an error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/manifest.rs"
      - "crates/buzz-relay/src/api/git/store.rs"
  - statement: "`docs/git-on-object-storage.md` gives a formal specification for this scheme and proves three safety theorems relative to three stated object-store axioms (durable write A1, strong read-after-write A2, linearizable conditional write A3): Theorem 1 (durability-ordering) — a client is never told a push succeeded before its manifest and packs are durable; Theorem 2 (manifest reconstruction) — a resolved manifest's named pack set is a superset of the object graph reachable from its refs; Theorem 3 (no lost update) — two concurrent ref-changing pushes never silently overwrite each other, because the CAS alone serializes writers with no advisory lock in v1."
    entry_class: FACT
    evidence:
      - "docs/git-on-object-storage.md"
  - statement: "The three safety theorems are additionally model-checked (not only argued in prose) by a companion TLA+ module (`docs/spec/GitOnObjectStore.tla`, run against `docs/spec/GitOnObjectStore.cfg`), which checks eight named invariants and demonstrates each is non-vacuous by a mutation that trips it."
    entry_class: FACT
    evidence:
      - "docs/spec/GitOnObjectStore.tla"
      - "docs/spec/GitOnObjectStore.cfg"
      - "docs/git-on-object-storage.md"
  - statement: "Axiom A3 (linearizable conditional write) is not assumed universally true of every S3-compatible backend; it is empirically admitted per deployment by `GitStore::run_conformance_probe`, which the relay runs at startup and treats as fail-closed — a probe failure aborts relay startup with an error rather than serving git traffic against an unadmitted backend — unless explicitly disabled via `BUZZ_GIT_CONFORMANCE_PROBE=false`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs"
      - "crates/buzz-relay/src/main.rs"
  - statement: "The conformance probe's default configuration races 32 concurrent writers over 3 rounds against both an `If-Match` CAS key and an `If-None-Match: *` create-only key, requiring exactly one winner per round among classified (non-transport-error) observers, plus a separate ETag-token-consistency check between the HEAD-path and GET-path extraction — the concurrent race phases are the load-bearing half, since A3 is a claim about races, not sequential correctness alone."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs"
  - statement: "Because ref/object state is entirely object-store-backed, the relay's own Helm chart documentation states each relay replica needs only its own `ReadWriteOnce` ephemeral volume for hydration — no shared `ReadWriteMany` filesystem is required for git, and the relay is multi-instance-ready without cross-instance filesystem coordination."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
      - "docs/git-on-object-storage.md"
  - statement: "Git object storage and Blossom media storage are two independent client code paths sharing one physical S3-compatible bucket inside the same `buzz-relay` binary: `crates/buzz-relay/src/api/git/store.rs` builds its own `rust-s3` `Bucket` client for content-addressed pack/manifest objects and the pointer CAS, separately from `buzz-media`'s `MediaStorage` client, though both are configured from the same `BUZZ_S3_*` environment variables and, by default, the same bucket."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs"
      - ".env.example"
  - statement: "VISION_PROJECTS.md's own Status table marks \"Git hosting (smart HTTP + NIP-34)\" as \"Ships today,\" and its accompanying prose states git hosting already supports `git clone`/`git push` over smart HTTP with NIP-34 manifests — the object-storage backend this node documents is what that shipped capability is built on, per the code and spec cited above, not a separately staged rollout."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md"
  - statement: "The end-to-end suite's `git_clone_push_fetch_force_roundtrip` and `git_concurrent_push_one_wins_and_repo_recovers` tests (in `crates/buzz-test-client/tests/e2e_git.rs`) exercise this object-storage layer against a live relay and MinIO — asserting, respectively, that the S3 manifest pointer advances correctly across a push/second-push/force-push/tag-push sequence, and that exactly one of 8 concurrent same-ref pushers wins the CAS race while the manifest pointer advances exactly once — but both are `#[ignore]`-gated behind a live relay, MinIO, and `git`, so they were read as intended-behavior documentation for this node, not executed."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_git.rs"
  - statement: "`store.rs`'s own conformance-probe unit tests (`probe_412_surfacing`, `probe_full_roundtrip`, `probe_conformance`, `probe_get_exposes_etag`) self-skip unless the `BUZZ_GIT_S3_PROBE=1` environment variable is set, so a default `cargo test` run exercises none of them against a real backend either — the empirical A1/A3 evidence in this node rests on reading these tests' assertions, not on having run them in this task."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/store.rs"
  - statement: "Issue #613 (parent PRD) and this task's own sibling issues #745 (git-hosting) and #753 (smart-http) were open, undrafted corpus tasks at the recorded revision, so no capability node existed yet for either the broader git-hosting capability or the smart-HTTP transport surface to `references` from this node."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#745 and launchpad-26/buzz#753 (read directly via gh issue view; both OPEN with no drafted document at this revision)"
relationships:
  - type: part-of
    target: capabilities-git-git-hosting
  - type: references
    target: architecture-containers-object-storage
  - type: references
    target: architecture-flows-git-push
---

# Git object storage: capability

Buzz's git hosting durably stores repository content — packs, manifests, and
per-repo ref state — on an S3-compatible object store, with no authoritative
per-repo filesystem. Because of this, a client's `git clone`/`git push` is
served by a relay that hydrates an ephemeral working tree from object storage
on every request, any relay instance can serve any repo without cross-instance
filesystem coordination, and a formally proved compare-and-swap scheme on one
mutable pointer per repo guarantees that concurrent pushes never silently lose
each other's ref updates.

## Maturity

**Ships today.** VISION_PROJECTS.md's Status table marks "Git hosting (smart
HTTP + NIP-34)" as shipped, and the object-storage backend documented here is
the mechanism that capability runs on, not a future or partially built layer —
`crates/buzz-relay/src/api/git/store.rs` and `manifest.rs` implement the
content-addressed writes and pointer CAS, `crates/buzz-relay/src/main.rs`
wires the fail-closed conformance gate into relay startup, and
`docs/git-on-object-storage.md` plus its companion TLA+ model
(`docs/spec/GitOnObjectStore.tla`) give the safety argument for why this
design is sound. Live end-to-end coverage exists
(`crates/buzz-test-client/tests/e2e_git.rs`) but is gated behind a live relay
and MinIO — see *Scope and omissions* for what that means for this node's own
verification.

## Boundary

This node does not describe:

- **How the git object-storage container is built or deployed** — the S3
  client wrapper, credential resolution, addressing style, and its
  relationship to the Blossom media client sharing the same bucket. That is
  `architecture-containers-object-storage`'s subject; this node cites the
  container as evidence the capability exists and `references` it rather than
  restating its ownership boundary or deployment profiles.
- **How a `git push` is authenticated and authorized before it ever reaches
  the object store** — NIP-98 signing, NIP-43 membership, the pre-receive
  policy callback and its role/ref-update permission matrix. That is
  `architecture-flows-git-push`'s subject; this node treats a push's arrival
  at the CAS step as its starting point and `references` that flow node for
  the transport that gets it there.
- **The step-by-step interaction sequence a client or agent experiences**
  doing a clone, push, or fetch (request/response order, error messages seen
  client-side). That is a flow-shaped concern, and no flow node for git
  clone/fetch exists in the merged corpus at this revision.
- **The CLI or HTTP surface a user or agent commands git hosting through**
  (`buzz-cli` subcommands, the smart-HTTP route group itself as an interface
  contract). That is `#753`'s scope (smart-http capability, not yet drafted)
  and, more specifically, an interface-typed node once one exists.
- **The broader git-hosting capability** — repo announcement (kind:30617),
  channel binding, push permission tiers, and NIP-34 manifest semantics beyond
  the object-storage mechanics. That is `#745`'s scope (git-hosting capability,
  not yet drafted); this node is deliberately narrower, covering only how git
  *content* is stored and kept consistent once the broader capability accepts
  it.
- **How the running system operates this storage day to day** — bucket
  provisioning, retention/pruning of unreachable packs (explicitly out of the
  formal proof's scope per `docs/git-on-object-storage.md`), and monitoring.
  That is the `operations` corpus surface's territory.

## Relationships

- references: `architecture-containers-object-storage` — the S3-compatible
  object-storage container this capability's writes and reads physically go
  through, shared with (but independent of) the Blossom media client.
- references: `architecture-flows-git-push` — the transport/authorization
  flow that gets a push to the point where this capability's CAS-publish step
  takes over; that node explicitly treats the object-store CAS as an outcome
  it cites rather than an internal it documents.

## Scope and omissions

**This node covers** the capability's statement (content-addressed,
create-only git object storage plus a single CAS-published manifest pointer
per repo, with no authoritative per-repo filesystem), its shipped maturity,
the formal safety argument backing it (three axioms, three theorems, a
model-checked TLA+ companion), the fail-closed conformance-probe admission
gate that empirically checks those axioms against a real backend at startup,
and the deployment consequence (no shared `ReadWriteMany` filesystem needed).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The object-storage container's ownership boundary, technology choice, and deployment profiles | `architecture-containers-object-storage` |
| Push transport authentication and ref-update authorization | `architecture-flows-git-push` |
| The step-by-step clone/push/fetch interaction sequence | a future flow node, not yet written |
| The CLI/HTTP interface surface for git hosting | `#753` (smart-http capability, not yet drafted) |
| The broader git-hosting capability (announcement, channel binding, NIP-34 manifests) | `#745` (git-hosting capability, not yet drafted) |
| Physical retention/pruning of unreachable pack objects | explicitly out of `docs/git-on-object-storage.md`'s proof boundary; an `operations`-surface concern, not yet a corpus node |
| The front-matter contract itself and node creation/update/retirement procedure | `node.schema.json` and `AGENTS.md` |

**Expected but not verified when this node was written:**

- **The live end-to-end tests were read, not executed.** Both
  `git_clone_push_fetch_force_roundtrip` and
  `git_concurrent_push_one_wins_and_repo_recovers` are `#[ignore]`-gated
  behind a live relay, MinIO, and `git`; this node's claims about their
  assertions come from reading the test code and the production path it
  exercises, not from a passing run in this task.
- **The conformance probe's own unit tests were not executed against a real
  backend either.** They self-skip unless `BUZZ_GIT_S3_PROBE=1` is set, so the
  empirical A1/A3 evidence here is read from test code and
  `docs/git-on-object-storage.md`'s own claimed verification history, not
  reproduced in this task.
- **Physical pack/manifest pruning behavior at scale was not checked.** The
  formal spec states retention/GC is outside its proof boundary and a
  separate backend concern; nothing in the code inspected here was read for
  an actual pruning implementation, so whether one currently exists at all is
  unverified rather than confirmed absent.
- **What `squareup/sprout-oss` or `squareup/block-coder-tf-stacks` provision
  for the S3-compatible bucket in the staging/production deployments this
  capability depends on** was not checked — those are separate, private repos
  not present in this checkout, consistent with the same gap already recorded
  in `architecture-containers-object-storage`.
