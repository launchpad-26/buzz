---
id: architecture-flows-git-push
type: architecture
status: draft
origin: launchpad
audiences:
  - developer
  - agent
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "The flow's entry point is `POST /git/{owner}/{repo}/git-receive-pack`, mounted alongside `info/refs` (GET) and `git-upload-pack` (POST) under the same body-limited router."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "A repo only accepts pushes once it has been announced as a kind:30617 event; repo creation from that event is what installs the pre-receive hook for the first time."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/hook.rs"
  - statement: "A repo's read/write access-control boundary is its `buzz-channel` tag on the kind:30617 announcement; the e2e suite documents that without this binding the read gate 404s even for the announcing owner."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_git.rs"
  - statement: "The client-side credential helper (git-credential-nostr) answers git's credential prompt by signing a NIP-98 kind:27235 event over the request URL and method with the user's Nostr key, then hands git the base64 token to retry the request with `Authorization: Nostr <token>`."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/README.md"
  - statement: "`GitAuth`, extracted via axum's `FromRequestParts`, is the server-side authentication gate for every git HTTP request: it requires an `Authorization: Nostr <base64-event>` header and rejects with 401 and a `WWW-Authenticate: Nostr` challenge if absent or malformed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "Tenant resolution happens before URL verification: the request's `Host` header is bound to a server-resolved community via `crate::tenant::bind_community`, and the NIP-98 event's signed `u` (URL) tag is checked against that server-resolved tenant, not a client-supplied or deployment-global value."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "The NIP-98 URL check is repo-root scoped (`u = http://host/git/{owner}/{repo}`), not service-scoped, because git's credential protocol does not pass query strings to helpers; the HTTP method the event was signed with is deliberately not checked against the actual request method, because git signs once with GET (`info/refs`) and reuses the same token for the following POST."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "NIP-98 event verification itself (signature, ±60s timestamp window) is delegated to `buzz_auth::nip98::verify_nip98_event`, called with `body: None` because streaming pack data cannot be buffered to verify a payload hash."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
      - "crates/buzz-auth/src/nip98.rs"
  - statement: "After NIP-98 verification, `GitAuth` additionally enforces the NIP-43 relay membership gate, reading the NIP-OA auth-tag attestation either from a tag on the signed event or from an `x-auth-tag` header (git's credential protocol has no way to carry a standalone auth-tag header from a plain `git push`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "`validate_repo_id` requires the owner path segment to be exactly 64 lowercase hex characters (a pubkey) and the repo name to be a bounded `[a-zA-Z0-9._-]` token with no leading dot and no `..`, rejecting either with 400 before any hydration work starts."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "`receive_pack` acquires an owned permit from a bounded `state.git_semaphore` before doing any work; when the semaphore is exhausted the request is rejected with 503 and a `Retry-After: 5` header rather than queuing indefinitely."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "There is deliberately no per-repo advisory lock serializing concurrent pushes to the same repo; the relay hydrates a fresh ephemeral workspace and parent-state snapshot per push (`hydrate_for_write`) and relies entirely on the object-store CAS at publish time for correctness, accepting that two concurrent same-repo pushes each pay the full hydrate + `receive-pack` cost and the loser's work is discarded."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "Each push gets a fresh pre-receive hook installed into its ephemeral workspace, with per-push state (callback URL, HMAC secret, repo id/owner, server-resolved community id, authenticated pusher pubkey) injected as process environment variables at `git receive-pack` exec time rather than baked into the hook script."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/hook.rs"
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "`git receive-pack --stateless-rpc` is run against the hydrated workspace via `run_git_at`; a pre-receive hook decline does not make the subprocess exit non-zero, so the relay separately parses the pkt-line report-status stream (`receive_pack_report_rejected`) for an `ng <ref> <reason>` line, on either a side-band or non-side-band channel, and folds that into the pack result's `ok` flag."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "The pre-receive hook calls back to `POST /internal/git/policy`, which is mounted behind middleware that rejects any request not originating from a loopback address, as defense-in-depth on top of the HMAC binding."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/mod.rs"
  - statement: "`hook_policy_check` first runs cheap structural validation on every field (repo id/owner/pusher hex shapes, ref name shapes, ref-update count bounds) before computing the HMAC, to avoid spending HMAC verification cost on malformed payloads; a request failing structural validation is denied with 403 before the signature is even checked."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/policy.rs"
  - statement: "The hook callback payload is authenticated by an HMAC-SHA256 over a canonical, length-prefixed encoding of repo id, repo owner, community id, pusher pubkey, the sorted ref updates, and a timestamp, keyed by a per-deployment secret (`state.config.git_hook_hmac_secret`); a 30-second callback age limit plus a 5-second future-timestamp tolerance additionally bounds replay."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/policy.rs"
  - statement: "The policy check re-resolves the repo's kind:30617 announcement by an exact `(community_id, kind=30617, pubkey=owner, d_tag=repo_id)` query rather than trusting any owner/community value asserted in the callback payload, keeping the localhost callback on the same server-resolved tenant as the git HTTP request that spawned it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/policy.rs"
  - statement: "Channel binding resolution is a fail-closed tri-state (`Bound`/`NotBound`/`Broken`) read from the announcement's first `buzz-channel` tag; a malformed or ambiguous binding (`Broken`) is denied for every pusher, including the repo owner, before the owner short-circuit below it is ever reached — collapsing `Broken` into `NotBound` would let an owner push through a binding the read gate refuses to honor."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/binding.rs"
      - "crates/buzz-relay/src/api/git/policy.rs"
  - statement: "A push to a repo whose bound channel is archived is denied with 403 (\"channel is archived (read-only)\"), independent of the pusher's role."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/policy.rs"
  - statement: "The pusher's authority is resolved as: the announcing repo owner, or (if not) a cryptographically verified managed-agent owner of the announcing pubkey, both of which are granted `MemberRole::Owner`; otherwise the pusher's channel membership role is looked up, and a pusher with no channel binding at all or no channel membership is denied — a repo with no `buzz-channel` binding produces a distinct, cross-component-contracted denial body (`GIT_NO_CHANNEL_BINDING_BODY`) consumed by the Desktop client's merge classifier and dialog matcher."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/policy.rs"
      - "crates/buzz-core/src/git_perms.rs"
  - statement: "A channel `Bot` role is downgraded to `Member` for git authorization purposes only — bot is a designation of what the account is, not a permission tier, so protection rules still apply to it exactly as to a human member."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/policy.rs"
  - statement: "Each ref update is classified by comparing old/new object ids against the all-zero OID and a `git merge-base --is-ancestor` result into one of Create, FastForward, NonFastForward, or Delete, and `evaluate_push` denies any update whose classified kind requires more than the pusher's effective role grants, collecting one denial per failing ref rather than failing the whole push on the first violation."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/git_perms.rs"
  - statement: "The default permission matrix requires only `Member` to create or fast-forward a branch ref, but requires `Admin` to create a non-branch/non-tag ref, to move (overwrite) a tag, to force-push (non-fast-forward), or to delete any ref; a `buzz-protect` tag on the kind:30617 announcement can further tighten these defaults per ref pattern."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/git_perms.rs"
  - statement: "A denied push (whether from a `run_git_at` subprocess failure or an in-band pre-receive decline folded into `ctx.pack.ok == false`) skips both the object-store CAS publish and the derived kind:30618 emission entirely — the workspace's refs were never advanced, so there is no committed state to publish, and publishing anyway would falsely attribute ref state to a denied pusher."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "Before publishing, the relay acquires and re-verifies a per-community \"serving write\" lease from the deletion-fence subsystem, both immediately before the object-store CAS and again after it (spanning the CAS, the derived event insert, and the local fan-out attempt); losing that lease at any point aborts the push with 503 rather than partially publishing."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "The object-store publish (`cas_publish`) binds its compare-and-swap predicate to the exact `parent_state` pointer observed at hydration time, with no re-read of the pointer in between; a concurrent writer that publishes first causes `CasError::Conflict`, which the relay turns into a 409 response instructing the client to pull and retry, discarding the loser's ephemeral workspace."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
      - "crates/buzz-relay/src/api/git/cas_publish.rs"
  - statement: "Two further CAS-time failure classes are distinguished by status code: `CasError::ManifestInvalid` (an unsafe ref name, malformed oid, empty HEAD, or malformed parent produced by the workspace) maps to 400 because no pointer was written; `CasError::ResourceLimit` (the repo would exceed the relay's configured pack/repo byte limits) maps to 413. Every other CAS error (manifest-read failure on parent corruption, backend error, pack-capture error) maps to 500."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "A relay-signed kind:30618 ref-state event is derived and emitted only after the CAS pointer write succeeds, and only when the committed manifest's canonical bytes actually differ from the parent's — a pack-only push that produces byte-identical refs/head is deduplicated for free by the relay DB's insert path rather than skipped up front, so a true no-op push still costs at most one extra DB round-trip, not a duplicate visible event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
      - "crates/buzz-relay/src/api/git/manifest_event.rs"
  - statement: "On a successful push, the relay-signed kind:30618 is fanned out to local subscribers through the same guarded send path as any other event, and the response only returns success to the git client after both the CAS commit and the kind:30618 publication attempt have completed — a pointer committed but a kind:30618 publish failure still surfaces to the git client as a 500 asking it to retry, even though the object data is already durably published."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "The end-to-end suite's `git_clone_push_fetch_force_roundtrip` test exercises this flow against a live relay and MinIO: initial push, a second push, a force-push (non-fast-forward) rewriting history, and a tag push, asserting after each step that the S3 manifest pointer advanced and that a fresh clone observes the exact pushed SHA or rewritten content."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_git.rs"
  - statement: "The end-to-end suite's `git_concurrent_push_one_wins_and_repo_recovers` test races 8 concurrent pushers against the same branch tip and asserts that exactly one push succeeds, the rest fail cleanly, the S3 manifest pointer advances exactly once, and a fresh clone afterward observes precisely the winning contender's commit — the closest available representative verification of the CAS-conflict failure path described above, though it exercises the CAS race rather than a policy denial or resource-limit rejection."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_git.rs"
  - statement: "Both e2e tests above are marked `#[ignore = \"requires live relay + MinIO + git\"]`, so they are not exercised in a default `cargo test` run and this node's verification claims rest on reading test code that documents intended behavior, not on having executed it in this task."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_git.rs"
  - statement: "Signing git commit/tag objects with a Nostr key (NIP-GS, via the separate `git-sign-nostr` program and `git config gpg.format x509`) is a related but independent concern from the push-transport authentication this node documents: NIP-98 authenticates the HTTP request that carries the push, while NIP-GS is an optional, orthogonal signature over the git objects themselves that this flow neither requires nor inspects."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/README.md"
      - "docs/nips/NIP-GS.md"
---

# Flow: `git push` to a Buzz repository

How a `git push` reaches a Buzz relay, is authenticated, authorized, applied
to the object store, and either published or rejected. This is the
transport-and-authorization flow around one HTTP request-response pair
(`git-receive-pack`); it does not cover object-level commit/tag signing
(NIP-GS — see *Scope and omissions*).

## Trigger

An HTTP `POST /git/{owner}/{repo}/git-receive-pack` request, sent by a
standard `git push` invocation once git's own smart-HTTP negotiation
(`GET .../info/refs?service=git-receive-pack`) has completed. `{owner}` is
the repo announcer's 64-hex-char Nostr pubkey; `{repo}` is the repo's short
name, both validated structurally before any other work begins.

## Preconditions

- **The repo must already be announced.** A kind:30617 event (`d` tag =
  repo id) creates the bare repository and installs its pre-receive hook;
  pushing to an unannounced repo has nothing to hydrate.
- **The repo should carry a `buzz-channel` binding.** That tag on the
  kind:30617 announcement is the repo's access-control boundary. Without
  it, even the announcing owner is denied further down this flow (via the
  `GIT_NO_CHANNEL_BINDING_BODY` denial) except where the owner short-circuit
  applies before role resolution — see *Ordered interactions*, step 7.
- **The client holds a Nostr private key** and has git's credential helper
  configured to invoke `git-credential-nostr`, which signs the NIP-98
  authentication event git needs to retry the request with an
  `Authorization: Nostr <token>` header.
- **The relay has spare `git_semaphore` capacity** and, if the pushing
  community is being deleted, has not yet fenced writes for it.

## Ordered interactions

1. **Client-side signing.** `git-credential-nostr` builds and signs a
   NIP-98 kind:27235 event over the request URL and (nominal) method, and
   hands git the base64 token. Git attaches it as
   `Authorization: Nostr <token>` and reuses the same token across the
   `info/refs` GET and the following `git-receive-pack` POST in one push
   session.
2. **Tenant binding, before URL verification.** The relay resolves a
   server-side tenant from the request's `Host` header
   (`crate::tenant::bind_community`) and checks the signed event's `u`
   (URL) tag against that server-resolved tenant — not against any
   client-supplied value.
3. **NIP-98 verification.** `buzz_auth::nip98::verify_nip98_event` checks
   the event signature and a ±60s timestamp window against the
   tenant-bound expected URL. HTTP method is deliberately not checked
   (git reuses one GET-signed token for a following POST); payload body is
   not hashed (pack data streams and cannot be buffered first).
4. **Relay-membership gate (NIP-43).** The pusher's NIP-OA auth-tag
   attestation — carried on the signed event or an `x-auth-tag` header — is
   checked against the target community's membership.
5. **Path validation, permit acquisition.** `validate_repo_id` rejects
   malformed owner/repo path segments with 400. `acquire_git_permit` takes
   a slot from the bounded `git_semaphore`, or the request is rejected
   with 503 (`Retry-After: 5`) rather than queued.
6. **Hydration.** `hydrate_for_write` builds a fresh ephemeral workspace
   and observes a `ParentState` snapshot of the object-store pointer in one
   round-trip. There is no per-repo lock: concurrent pushes to the same
   repo each hydrate independently, and the loser's work is discarded at
   step 10.
7. **Hook install and `receive-pack`.** A pre-receive hook is (re)installed
   into the ephemeral workspace on every push, with per-push state (hook
   callback URL, HMAC secret, repo id/owner, server-resolved community id,
   authenticated pusher pubkey) injected as process environment. `git
   receive-pack --stateless-rpc` then runs against the hydrated workspace.
8. **Pre-receive policy callback.** Before accepting any ref update, git's
   pre-receive hook calls back to `POST /internal/git/policy` — reachable
   only from loopback addresses, and its payload independently HMAC-bound
   and timestamp-bounded (30s TTL, 5s future skew). The relay re-resolves
   the repo's kind:30617 announcement from its own database (not from the
   callback payload), resolves the fail-closed channel-binding tri-state,
   checks the bound channel is not archived, resolves the pusher's
   effective role (owner / managed-agent-owner / channel member, with
   `Bot` downgraded to `Member` for authorization purposes only), and
   evaluates every ref update's classified kind (create / fast-forward /
   non-fast-forward / delete) against that role and any `buzz-protect`
   overrides. `allowed: true` lets git apply the refs; a denial makes git
   report `ng <ref> <reason>` in-band without a non-zero process exit.
9. **Reject fold.** The relay parses the pkt-line report-status stream for
   any `ng ` line to fold a hook decline into the pack result's `ok` flag,
   because a decline alone does not make the subprocess exit non-zero.
10. **Fence check and CAS publish.** If `ok` is false (subprocess failure
    or in-band decline), the flow stops here — see *Failure, abort, and
    rollback behavior*. Otherwise the relay acquires and re-verifies a
    per-community serving-write lease, then publishes via `cas_publish`,
    whose compare-and-swap predicate is bound to the exact pointer
    `ParentState` observed at hydration (step 6) with no re-read in
    between.
11. **Derived event.** Only after the CAS commit succeeds, and only if the
    committed manifest's canonical bytes differ from the parent's, a
    relay-signed kind:30618 ref-state event is built and inserted, then
    fanned out to local subscribers over the same guarded send path as any
    other event.
12. **Response.** The git client receives its `git-receive-pack` response
    (report-status, human-readable messages) only after the CAS commit and
    the kind:30618 publish attempt have both completed; the serving-write
    lease is held across that entire span and released only at the end.

## Authentication / authorization / trust-boundary crossings

- **Client → relay (transport):** NIP-98 signed-event bearer auth, with the
  signed URL checked against a server-resolved tenant rather than a
  client-supplied Host or community value — this is the boundary the flow
  refuses to let a client spoof.
- **Client → relay (membership):** NIP-43 relay-membership check via the
  NIP-OA auth-tag attestation.
- **Relay → relay, over loopback (policy callback):** the pre-receive
  hook's callback to `/internal/git/policy` is both network-restricted
  (loopback-only middleware) and cryptographically bound (per-push HMAC
  over a canonical payload including the server-resolved community id),
  so a hook callback cannot be replayed across communities or forged
  from outside the host.
- **Authorization (role → ref-update kind):** the pusher's resolved role
  (owner, managed-agent owner, or channel member role) gates which kinds
  of ref update (create/fast-forward/non-fast-forward/delete, per ref
  pattern and any `buzz-protect` override) that pusher may perform — this
  is evaluated fresh on every push from server-side membership and
  announcement state, never from anything the client asserts.

## Failure, abort, and rollback behavior

There is no partial commit to roll back: the object store is only ever
mutated by the single CAS write at step 10, so every failure mode below is
either "nothing was written" or "something else won the race and this push
was cleanly superseded."

| Failure | Where | Response | What was (not) published |
|---|---|---|---|
| Missing/malformed auth, tenant mismatch, failed NIP-98 verification | `GitAuth` extraction | 401 | Nothing — request never reaches hydration |
| Not a relay member (NIP-43) | `GitAuth` extraction | 403 (via membership gate) | Nothing |
| Malformed owner/repo path | `validate_repo_id` | 400 | Nothing |
| No spare semaphore capacity | `acquire_git_permit` | 503, `Retry-After: 5` | Nothing |
| Hydration failure | `hydrate_for_write` | mapped by `hydrate_error_to_response` | Nothing |
| Hook install failure | `install_hook` | 500 | Nothing |
| Pre-receive policy denial (bad HMAC, expired callback, broken/archived channel binding, insufficient role) | `hook_policy_check` | in-band `ng` report, folded to `ctx.pack.ok == false` | Nothing — CAS and kind:30618 both skipped; refs in the ephemeral workspace were never advanced |
| Community write-fence lost (deletion in progress) | serving-write lease acquire/verify, before and during CAS | 503 | Nothing |
| Lost the CAS race to a concurrent writer | `cas_publish` → `CasError::Conflict` | 409, "pull and retry" | Nothing — the loser's ephemeral workspace is dropped; the winner's state stands |
| Workspace produced an invalid manifest (unsafe refname, malformed oid, empty HEAD/parent) | `cas_publish` → `CasError::ManifestInvalid` | 400 | Nothing — pre-CAS |
| Repo would exceed configured pack/repo byte limits | `cas_publish` → `CasError::ResourceLimit` | 413 | Nothing — pre-CAS |
| Other CAS-layer error (parent corruption, backend, pack-capture) | `cas_publish` | 500 | Nothing, except the rare case where the winner's manifest read failed while fetching *another* push's already-installed state — unrelated to this push |
| Pointer committed but kind:30618 build/insert failed | after CAS, before response | 500, "committed but... retry" | The object data **is** durably published; only the derived event is missing, and the client is told to retry rather than being told it failed outright |

A denied or superseded push is never partially visible: readers and future
clones only ever observe a manifest pointer that some push's CAS actually
won.

## Representative verification

- `crates/buzz-test-client/tests/e2e_git.rs::git_clone_push_fetch_force_roundtrip`
  — clone, push, second push, force-push (non-fast-forward), and tag push
  against a live relay + MinIO, asserting the S3 manifest pointer advances
  on each and that fresh clones observe the exact resulting state.
- `crates/buzz-test-client/tests/e2e_git.rs::git_concurrent_push_one_wins_and_repo_recovers`
  — races 8 concurrent pushers at the same branch tip; asserts exactly one
  wins, the manifest pointer advances exactly once, and a fresh clone
  observes precisely the winner's commit. This is this repository's closest
  representative coverage of the CAS-conflict path in the failure table
  above, though it exercises the race itself rather than a policy denial or
  a resource-limit rejection.
- Both tests are `#[ignore]`-gated on a live relay, MinIO, and `git` being
  available, so they were read, not executed, while authoring this node —
  see *Scope and omissions*.
- `crates/buzz-relay/src/api/git/policy.rs`'s own unit tests (HMAC
  tamper/replay rejection for every signed field, and
  `push_gate_denies_owner_through_broken_binding`) cover the policy
  callback's authentication and fail-closed binding resolution in
  isolation, without needing live infrastructure.

## Scope and omissions

**This node covers** the HTTP push transport: client-side NIP-98 signing,
server-side authentication and NIP-43 membership, the pre-receive policy
callback and its role/ref-update authorization matrix, and the CAS publish
step through to the derived kind:30618 event — including every failure path
reachable from that sequence.

**It does not cover, and these are separate concerns rather than gaps in
this one:**

| Not covered here | Why it is a separate node's subject |
|---|---|
| NIP-GS commit/tag object signing (`git-sign-nostr`) | Orthogonal to transport auth — signs the git objects themselves, independent of how the push reached the relay |
| `git clone` / `git fetch` (`info/refs`, `git-upload-pack`) | A read flow with its own authorization surface, sharing only `GitAuth` and repo/tenant resolution with this one |
| The object-store CAS algorithm's internals (pointer format, manifest canonicalization, pack/idx storage) | `crates/buzz-relay/src/api/git/{cas_publish,manifest,store}.rs` — this node cites the CAS *outcome* (conflict, success, resource limit) at the granularity a push client observes, not its implementation |
| `buzz-protect` rule syntax and the full protection-rule evaluation beyond the default role matrix | `crates/buzz-core/src/git_perms.rs`'s `parse_protection_tag*` family — this node states only that overrides exist and tightens, not their grammar |
| Repo creation from a kind:30617 announcement, and the invite/community-provisioning flow that makes a pusher a channel member in the first place | Separate architecture/flow nodes, none of which exist in the merged corpus at this revision |

**No `relationships` are declared.** At the recorded revision, no other
`architecture`/flow corpus node is confirmed merged on `origin/launchpad` —
this batch's other 46 nodes are being authored in parallel, isolated
worktrees and had not landed on the target branch when this node was
written. A `relationships[].target` naming an id no loaded node carries is a
hard validation error, so no edge is declared here; the natural first edges
(to a repo-announcement/creation flow node, and to a `git clone`/`fetch`
flow node) are named above as a pointer for whoever authors those nodes, or
for a later pass over this one once they exist.

**Expected but not verified when this node was written:**

- **Neither e2e test above was actually executed.** Both are
  `#[ignore]`-gated behind a live relay, MinIO, and `git`, none of which
  were started for this task. Every behavioral claim about the flow's
  observable outcome (pointer advances, exactly-one-winner races, force-push
  and tag round-tripping) is sourced from reading what the test asserts and
  the production code path it exercises, not from a passing run.
- **The exact wording and machine-readability of `buzz-protect` rule
  parsing** (`parse_protection_tag`, `parse_protection_tag_with_warnings`)
  was not read in full; only `default_min_role`'s baseline matrix and the
  fact that overrides exist were verified.
- **How the Desktop client's merge classifier and dialog matcher actually
  consume `GIT_NO_CHANNEL_BINDING_BODY`** was not traced into `desktop/` —
  only that the relay-side constant and its two required matcher strings
  are documented as a cross-component contract in `buzz-core`.
