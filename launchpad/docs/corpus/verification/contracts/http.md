---
id: verification-contracts-http
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
  - statement: "AGENTS.md's 'Nostr-first HTTP surface' section states that the relay exposes a narrow HTTP surface -- NIP-11/NIP-05 metadata, POST /events, POST /query, POST /count, workflow webhooks, Blossom media, git smart HTTP, git policy hooks, and health probes -- and that 'these HTTP paths all preserve the same host-derived community boundary.'"
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "The relay's app router registers POST /events, POST /query and POST /count under its 'Nostr HTTP bridge (NIP-98 auth)' section, dispatching to api::bridge::submit_event, api::bridge::query_events and api::bridge::count_events respectively."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:71-74"
  - statement: "submit_event (POST /events) resolves the request's community from the Host header via tenant::bind_community before NIP-98/X-Pubkey auth or any tenant-scoped write runs; its own comment states this is 'identical to the WS door in router.rs', and an unmapped host or lookup failure fails closed with a generic 404 body that never echoes the host."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:708-723"
  - statement: "query_events (POST /query) and count_events (POST /count) each independently perform the identical bind-before-auth sequence as submit_event -- read the Host header, call tenant::bind_community, and fail closed to the same generic 404 on Err(_) -- before their own NIP-98 auth check runs; count_events's own comment cross-references both siblings as 'identical to the WS door in router.rs and query_events/submit_event above.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs:978-994"
      - "crates/buzz-relay/src/api/bridge.rs:1508-1523"
  - statement: "crates/buzz-test-client/tests/conformance_multitenant.rs's row_zero_host_binding::client_supplied_community_cannot_override_host test creates an open channel in community B and then, over POST /events against community A's host, posts a kind:9 event #h-tagging that same channel id; it asserts A's response is not a successful 'accepted:true' body, that the rejection reason string is exactly 'restricted: not a channel member' (to pin the rejection to the host-derived-community/channel-scope branch rather than an earlier gate), and that A's rejection body never echoes the B-only channel id."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:257-338"
  - statement: "Both HTTP requests the test makes -- create_open_channel's channel-creation event and post_kind9's kind:9 override attempt -- are issued as POST {base_url}/events via a plain reqwest client with an X-Pubkey header, i.e. through the same HTTP bridge endpoint this node documents, not over a WebSocket EVENT frame."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:346-408"
  - statement: "The test function client_supplied_community_cannot_override_host carries #[ignore] and, per the containing file's own module doc-comment, requires a running multi-tenant relay with two live host-to-community mappings, selected by running `cargo test -p buzz-test-client --test conformance_multitenant -- --ignored` with RELAY_URL_A and RELAY_URL_B set; a plain `cargo test` does not execute it."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:14-26"
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:257-258"
  - statement: "No workflow under .github/workflows/ and no Justfile recipe invokes the conformance_multitenant test binary or sets RELAY_URL_A/RELAY_URL_B, so this test does not run in CI or via any documented `just` recipe at the recorded revision -- only a manual invocation against a hand-provisioned two-host relay runs it."
    entry_class: FACT
    evidence:
      - "grep_repo('conformance_multitenant', '.github/workflows/*.yml;Justfile') -> no matches"
  - statement: "client_supplied_community_cannot_override_host, rather than nip42_host_binding_live.rs's AUTH-tag override test, is the correct verifying test for an HTTP-bridge-scoped community-boundary obligation, because it is the only test in the repository whose channel-creation and override-attempt requests are issued over POST /events specifically; nip42_host_binding_live.rs's do_auth_with_relay_tag helper instead opens a raw WebSocket connection (tokio_tungstenite::connect_async against a ws:// URL) and sends a kind:22242 AUTH frame, never an HTTP request."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs:383-408"
      - "crates/buzz-test-client/tests/nip42_host_binding_live.rs:19-38"
    confidence: 0.8
  - statement: "Issue #1359's definition of done requires this node to name the obligation as one precise testable sentence, name the verifying test(s) exactly by path and function, state how to run them, state enforcement status honestly (verified/gated/pending), and state a limits section naming what the test does and does not prove."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1359 definition of done"
  - statement: "row_zero_host_binding::unmapped_host_fails_closed_generically, the sibling test in the same module, is a second and distinct obligation -- that an unmapped host fails closed on the WebSocket-upgrade/SPA door in router.rs -- rather than a claim about the POST /events, /query or /count bridge specifically; it is named here as a related but separate obligation rather than folded into this node, per this task's own instruction not to combine independently discoverable obligations."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1359 task brief, compared against crates/buzz-test-client/tests/conformance_multitenant.rs:74-191"
relationships:
  - type: references
    target: architecture-flows-http-event-submission
  - type: references
    target: architecture-principles-fail-closed-boundaries
---

# HTTP bridge community-boundary — test contract

## Purpose and boundary

This node documents one obligation of the relay's Nostr-over-HTTP bridge: that
`POST /events` resolves the requester's community strictly from the
connection's `Host` header and never honors a client-supplied `#h`
channel-tag as an override of that host-derived community. It covers that
obligation only. It does not cover the rest of the narrow HTTP surface
`AGENTS.md`'s "Nostr-first HTTP surface" section names (NIP-11/NIP-05,
workflow webhooks, Blossom media, git smart HTTP, git policy hooks, health
probes) beyond citing that section as the surface this obligation is one
instance of, and it does not cover the sibling "unmapped host fails closed"
obligation exercised on the WebSocket/SPA door — see *Scope and omissions*.

## Obligation

> `POST /events`, the relay's Nostr-over-HTTP event-submission bridge,
> resolves the requester's community solely from the connection's `Host`
> header (via `tenant::bind_community`), before NIP-98/X-Pubkey auth or any
> tenant-scoped write runs; a client-supplied `#h` channel-tag naming a
> channel that exists only in a different community is rejected, never
> honored as an override of the host-derived community.

## Verifying test(s)

- `crates/buzz-test-client/tests/conformance_multitenant.rs` —
  `row_zero_host_binding::client_supplied_community_cannot_override_host`
  (lines 257-338) — covers the override-rejection half of the obligation:
  a channel created only in community B is `#h`-tagged in a kind:9 event
  posted to community A over `POST /events`; the test asserts A rejects with
  exactly `"restricted: not a channel member"` (pinning the rejection to the
  host-derived-community/channel-scope branch rather than an earlier gate
  such as `bind_community`'s own 404, bridge-auth 403, replay, or JSON parse)
  and that A's rejection body never echoes the B-only channel id. Both the
  channel-creation request and the override attempt are issued as
  `POST {base_url}/events` (lines 346-408), i.e. through the HTTP bridge this
  node documents, not a WebSocket frame.

This test does not itself exercise the "resolves from the `Host` header
before auth runs" half of the obligation in isolation — that half is read
directly from `submit_event`'s source (see the front-matter evidence ledger)
rather than from a dedicated assertion; the override-rejection test is the
one place a passing/failing run can currently falsify the composed claim.

## How to run it

```bash
RELAY_URL_A=http://a.localhost:3000 \
RELAY_URL_B=http://b.localhost:3000 \
cargo test -p buzz-test-client --test conformance_multitenant \
  row_zero_host_binding::client_supplied_community_cannot_override_host \
  -- --ignored --nocapture
```

Both URLs must address the same relay process (same pod, same Postgres, same
Redis) with two live host-to-community mappings — only the `Host` header
differs. `cargo test -p buzz-test-client --test conformance_multitenant`
with no arguments runs nothing here: the test is `#[ignore]`d and is skipped
by a plain invocation.

## Current enforcement status

**Gated**, as of `473205a7457b208455f188847bfb27b01aa83cac`. The test exists,
is not a `todo!()` stub, and asserts real behavior, but it is marked
`#[ignore]` and requires a hand-provisioned two-host relay
(`RELAY_URL_A`/`RELAY_URL_B`) that no workflow under `.github/workflows/` and
no `Justfile` recipe provisions or invokes. It therefore does not run in CI
and does not run under `just ci`, `just test`, or any other documented
recipe — only a manual, out-of-band run against such a deployment currently
exercises it.

## Limits

- **What this test proves, when run:** that on this specific two-host
  topology, a client-supplied `#h` claim naming a channel that exists only
  in the other community is rejected on `POST /events`, with the rejection
  traceable to the channel-scope/override branch rather than an incidental
  earlier gate, and that the rejection does not leak the other community's
  channel id.
- **What it does not prove:** the same property for `POST /query` or
  `POST /count`. Both handlers read the `Host` header and call
  `tenant::bind_community` before auth in the same way `submit_event` does
  (cited as FACT above from source), but no test in this repository exercises
  an override attempt against either endpoint specifically — that is
  read-from-source, not test-verified, for those two routes.
- **What it does not prove, because the test has not been run:** this test
  was read for its assertions and its `#[ignore]`/gating state, both of which
  are checkable from the file alone; whether it currently passes against a
  live two-host relay was not established while authoring this node, because
  no such deployment was available. The enforcement status above is "gated",
  not "verified", precisely because a pass has not been observed at this
  revision.
- **What a pass would not prove even if observed:** only that this one
  scenario (an *open*-visibility channel, a kind:9 event, one specific
  rejection-reason string) behaves correctly — not every event kind, channel
  visibility, or client-supplied tag shape that could attempt the same kind
  of override.

## Scope and omissions

**This node covers** the community-boundary obligation on `POST /events`
described above: one obligation, one directly verifying test, its current
gated enforcement status, and what a pass on it would and would not prove.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full `/events` request lifecycle (auth, admission, replay, ingest) beyond the host-binding step | `architecture-flows-http-event-submission` |
| The general fail-closed-on-unknown-host principle across every relay door | `architecture-principles-fail-closed-boundaries` |
| The sibling obligation that an unmapped host fails closed on the WebSocket-upgrade/SPA door (`row_zero_host_binding::unmapped_host_fails_closed_generically`) | Not yet a corpus node; a candidate for a future `verification/contracts/` sibling |
| An equivalent override-rejection test for `POST /query` and `POST /count` specifically | Not tested anywhere in this repository at the recorded revision |
| The rest of the narrow HTTP surface AGENTS.md names (NIP-11/NIP-05, webhooks, Blossom media, git smart HTTP, git policy hooks, health probes) | Not this node; each would be its own test-contract node if and when one is authored |
| How any corpus node should cite a test as evidence, generally | `launchpad/docs/corpus/standards/test-references.md` |
| The corpus's general evidence contract and citation shapes | `launchpad/docs/corpus/AGENTS.md`, `launchpad/project-intelligence/CONTRACT.md` §3 |

**Relationships, checked rather than assumed absent.** This worktree was
branched directly from `origin/launchpad` with no other changes, so its
corpus tree is the merge target's corpus tree; both `architecture-flows-http-event-submission`
and `architecture-principles-fail-closed-boundaries` are present there and
both edges validate today. No `implements` edge to
`corpus-template-test-contract` is declared: that template node is `type:
governance` describing how to author a node like this one, not a standard
this node is a template-instance of in the schema's sense, and the template
document itself states it does not yet mandate specific edges from nodes
built against it.

**Expected but not verified when this node was written:**

- **Whether `client_supplied_community_cannot_override_host` currently
  passes against a live two-host relay was not established.** No such
  deployment was provisioned while authoring this node; the test's
  assertions and its `#[ignore]`/gating state were read from source, not
  executed.
- **Whether `POST /query` or `POST /count` would pass an equivalent
  override-rejection scenario was not established**, and no test asserting
  it was found. The identical-bind-before-auth claim about those two
  handlers rests on reading their source, not on running anything against
  them.
