---
id: capabilities-git-smart-http
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "`git_router` mounts exactly three HTTP routes under `/git/{owner}/{repo}/` — `GET info/refs`, `POST git-upload-pack`, `POST git-receive-pack` — behind a single `RequestBodyLimitLayer` sized from `state.config.git_max_pack_bytes`; this is git's own smart-HTTP protocol surface, not a bespoke API."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:2103-2112"
  - statement: "`crates/buzz-relay/src/api/git/mod.rs`'s module documentation states the `transport` submodule implements the 'Smart HTTP protocol (info/refs, upload-pack, receive-pack)', naming the protocol explicitly rather than describing a custom scheme."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/mod.rs:1-7"
  - statement: "`GET info/refs?service=git-upload-pack|git-receive-pack` validates the `service` query parameter against an exact two-value allowlist and rejects anything else with 400 before any repository work begins."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:748-758"
  - statement: "For `git-upload-pack` advertisement on a branches-only repo (no `refs/tags/*`, HEAD resolves to an advertised ref), `info_refs` takes a fast path that builds the complete pkt-line advertisement body directly from the published manifest — no hydrate, no subprocess, no git-concurrency permit — documented as byte-compatible with `git upload-pack --advertise-refs` against git 2.51 for that case; every other case (tagged repos, or any `git-receive-pack` advertisement, which carries a different capability set) falls back to shelling out to the real `git` binary via `info_refs_subprocess`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:610-626"
      - "crates/buzz-relay/src/api/git/transport.rs:662-808"
  - statement: "The fast-path advertisement is framed in git's pkt-line wire format: a 4-hex-digit length prefix (counting itself) followed by the payload, built by a dedicated `pkt_line` encoder that caps a single payload at `0xffff - 4` bytes and, if a caller ever exceeded that, drops the payload into an empty `0004` pkt-line and logs an error rather than emitting a malformed 5-hex-digit length that would silently corrupt the stream for the next reader."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:628-660"
  - statement: "The fast-path advertisement offers a fixed, conservative capability string (`multi_ack thin-pack side-band side-band-64k ofs-delta shallow deepen-since deepen-not deepen-relative no-progress include-tag multi_ack_detailed no-done symref=HEAD:<ref> object-format=<sha1|sha256> agent=buzz-git`), and the object format (`sha1` vs `sha256`) is derived from the stored HEAD oid's hex width rather than hardcoded; the response is served with `Content-Type: application/x-git-upload-pack-advertisement` and `Cache-Control: no-cache`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:680-727"
      - "crates/buzz-relay/src/api/git/transport.rs:783-793"
  - statement: "`POST git-upload-pack` (clone/fetch) streams the hydrated subprocess's stdout straight into the HTTP response body via `stream_git_read` rather than buffering the whole pack in memory, and responds with `Content-Type: application/x-git-upload-pack-result`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:1001-1064"
  - statement: "`POST git-receive-pack` (push) buffers the completed subprocess output (bounded by `RECEIVE_PACK_MAX_OUTPUT_BYTES = 1 MiB`) rather than streaming it, because the response can only be constructed after the object-store CAS publish (in `finalize_push`) resolves; `build_git_response` gives it `Content-Type: application/x-git-receive-pack-result`, the sibling content type to upload-pack's result."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:51"
      - "crates/buzz-relay/src/api/git/transport.rs:1093-1192"
      - "crates/buzz-relay/src/api/git/transport.rs:1743-1755"
  - statement: "Both POST routes decode a gzip-encoded request body (`Content-Encoding: gzip` or `x-gzip`) before handing it to the subprocess, and bound the *decoded* byte count independently of the router's compressed-body limit — `UPLOAD_PACK_MAX_DECODED_BYTES = 64 MiB` for upload-pack, `state.config.git_max_pack_bytes` for receive-pack — specifically to stop a small gzip bomb (compression ratios up to ~1000:1) from feeding an effectively unbounded stream to the subprocess or scratch disk."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:60"
      - "crates/buzz-relay/src/api/git/transport.rs:960-999"
      - "crates/buzz-relay/src/api/git/transport.rs:1029"
      - "crates/buzz-relay/src/api/git/transport.rs:1101"
  - statement: "The client side of this protocol needs no bespoke Buzz tooling to speak it: `crates/git-credential-nostr` is git's own generic credential-helper mechanism (invoked by a standard `git` client configured with `credential.helper`), which signs a NIP-98 event and hands git a bearer token to retry the request — the wire protocol itself (pkt-line advertisement, upload-pack/receive-pack request-response) is unmodified git smart HTTP, only the credential acquisition is Buzz/Nostr-specific."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/README.md"
  - statement: "VISION_PROJECTS.md's Status table marks 'Git hosting (smart HTTP + NIP-34)' as '✅ Ships today' and its accompanying prose states 'git hosting ships today — `git clone`/`git push` over smart HTTP with NIP-34 manifests', naming smart HTTP explicitly as a shipped, product-level capability rather than an internal implementation detail."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:247-261"
  - statement: "The end-to-end suite's `git_clone_push_fetch_force_roundtrip` test (ignored by default, requiring a live relay + MinIO + git) exercises an initial push, a second push, a force-push, a tag push, and fetches/clones after each, over this same smart-HTTP transport, asserting a fresh clone observes the exact pushed or rewritten state each time — the closest available representative verification of the transport working end-to-end, read as intended behavior rather than executed for this node."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_git.rs"
  - statement: "`crates/buzz-relay/src/api/git/transport.rs`'s own `track_c_tests` module unit-tests the fast-path/subprocess advertisement machinery directly (spawning real `git` subprocesses against temporary bare repositories) without needing a live relay or MinIO, distinct from the ignored end-to-end suite cited above."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:2114-2170"
  - statement: "The already-merged flow node `architecture-flows-git-push` documents the full `git push` transport-and-authorization sequence in detail (NIP-98 signing, tenant binding, NIP-43 membership, the pre-receive policy callback, CAS publish, kind:30618 emission) as one ordered flow through the same `git-receive-pack` route this capability node names; this node deliberately does not re-narrate that sequence, only cites the route it flows through."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/git-push.md"
---

# Git smart HTTP transport: capability

Any standard, unmodified git client can `clone`, `fetch`, and `push` against a
Buzz-hosted repository using git's own smart-HTTP transport protocol —
`info/refs` service advertisement followed by `git-upload-pack` or
`git-receive-pack` request/response — with no Buzz-specific plugin, wire-format
change, or custom client required. The only Buzz/Nostr-specific piece a user's
tooling needs is a credential helper (`git-credential-nostr`) that answers
git's generic credential prompt; everything downstream of that (pkt-line
framing, service negotiation, pack transfer) is exactly the protocol any git
host speaks.

## Maturity

Ships today. VISION_PROJECTS.md's own Status table marks "Git hosting (smart
HTTP + NIP-34)" as "✅ Ships today," and the routes, pkt-line encoder,
fast-path/subprocess advertisement logic, and streaming pack transfer this
node cites are implemented and unit-tested in
`crates/buzz-relay/src/api/git/transport.rs` at the recorded revision — not a
design sketch.

## Boundary

This node does not describe:
- **How a request is authenticated or authorized.** NIP-98 request signing,
  tenant/community resolution, NIP-43 relay membership, and the pre-receive
  policy callback's channel-role and `buzz-protect` evaluation are a separate
  concern from the transport wire protocol itself — see the (unmerged, at
  this revision) `nostr-git-authentication` capability task (#748) and the
  already-merged `architecture-flows-git-push` flow node, which documents the
  full authenticated push sequence end to end.
- **The overall git-hosting capability** — repo announcement from a
  kind:30617 event, the pre-receive hook and its policy callback, the
  object-store CAS publish and kind:30618 derived-event emission, and the
  permission/protection model that governs who may push what. Those are the
  (unmerged, at this revision) `git-hosting` capability task (#745)'s
  subject; this node is scoped to the transport protocol mechanics alone —
  the routes, the wire format, and how bytes move over HTTP — not to what
  gates or follows them.
- **The step-by-step `git push` flow.** `architecture-flows-git-push` already
  documents the ordered sequence (signing, tenant binding, membership,
  policy callback, CAS publish, response) through the `git-receive-pack`
  route this node names; this node states that the transport exists and how
  its wire mechanics work, not the flow through it.
- **How the running system is operated** (deployment, monitoring, incident
  response for the git subsystem) — the `operations` corpus surface, not
  this node.
- **NIP-34's repository-announcement and patch-event data model** beyond the
  fact that a repo is *served* over this transport once announced — the data
  model itself is `git-hosting` (#745)'s and any NIP-34-specific corpus
  node's subject.

## Relationships

None declared. `architecture-flows-git-push` exists on `origin/launchpad` at
the recorded revision and is the natural `references` target for this node,
but the capability template's own guidance treats `references` as optional
supporting context rather than a requirement, and the sibling capability
tasks this node's boundary section names (`git-hosting` #745,
`nostr-git-authentication` #748) are both still open and unmerged — adding a
`relationships` entry to either now would target an id no loaded corpus node
carries, which `AGENTS.md` states is a hard validation error. This is the
moment to add those edges once those siblings land, not before.

## Scope and omissions

**This node covers** the smart-HTTP transport surface itself: the three
routes `git_router` mounts, the `info/refs` service-negotiation and its
fast-path (manifest-derived) versus subprocess (real `git` binary)
advertisement paths, the pkt-line wire encoding, the `application/x-git-*`
content types on each response, gzip request decoding and its independent
decoded-byte bound, and streaming versus buffered response construction —
grounded in one product-level statement: any standard git client can talk to
a Buzz repo unmodified.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Request authentication (NIP-98) and authorization (NIP-43, channel role, `buzz-protect`) | `#748` (nostr-git-authentication capability, not yet merged) and `architecture-flows-git-push` |
| Repo announcement, the pre-receive hook, the policy callback, CAS publish, kind:30618 emission | `#745` (git-hosting capability, not yet merged) |
| The full ordered `git push` sequence | `launchpad/docs/corpus/architecture/flows/git-push.md` (merged) |
| NIP-34's repository/patch data model | `#745` and any future NIP-34-specific node |
| How the git subsystem is deployed and operated | the `operations` corpus surface |

**Expected but not verified when this node was written:**
- **No live end-to-end run was executed.** `git_clone_push_fetch_force_roundtrip`
  and the fast-path/subprocess unit tests were read, not run, for this node —
  the ignored e2e test needs a live relay, MinIO, and `git`, none of which were
  started for this task.
- **The exact byte-for-byte parity between the fast-path advertisement and a
  real `git upload-pack --advertise-refs` invocation** is asserted by the
  source's own comments and `track_c_tests` unit tests, not independently
  re-derived here against a live `git` binary.
- **How a fetch (as opposed to a fresh clone) exercises `git-upload-pack`
  incrementally (`have`/`want` negotiation over multiple round-trips) was not
  traced in detail** — this node cites the route and content type, not the
  full negotiation state machine, which is upstream git protocol behavior
  this transport passes through to the subprocess or fast path unchanged.
