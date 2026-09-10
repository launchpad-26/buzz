---
id: implementation-crates-buzz-test-client
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "buzz-test-client's package description is 'Integration test client and E2E test suite for Buzz', and it ships one library crate plus four binaries: buzz-test-cli (src/main.rs, the manual send/subscribe CLI), and src/bin/mention.rs and src/bin/wamp_bench.rs (additional manual/benchmarking tools)."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/Cargo.toml"
      - "crates/buzz-test-client/src/main.rs"
      - "crates/buzz-test-client/src/bin/mention.rs"
      - "crates/buzz-test-client/src/bin/wamp_bench.rs"
  - statement: "The crate's public library surface is the BuzzTestClient struct in src/lib.rs, wrapping buzz-ws-client's NostrWsConnection: connect/connect_unauthenticated, authenticate/authenticate_with_nip_oa (NIP-42), send_event, send_text_message, subscribe/close_subscription, send_raw, recv_event, collect_until_eose, and disconnect, plus a re-exported parse_relay_message/OkResponse/RelayMessage/WsClientError from buzz-ws-client and its own TestClientError enum."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/src/lib.rs"
  - statement: "buzz-ws-client (the crate buzz-test-client wraps rather than reimplements) is a separate, smaller crate whose own public surface is NostrWsConnection, WsClientError, parse_relay_message, build_auth_event and publish_event -- the shared NIP-42 WebSocket client this repository's root CLAUDE.md names as its own component ('buzz-ws-client -- Shared NIP-42 WebSocket client')."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/lib.rs"
      - "CLAUDE.md"
  - statement: "All 19 files under crates/buzz-test-client/tests/ are integration suites written against a live relay; e2e_relay.rs's own module doc states 'These tests require a running relay instance. By default they are marked #[ignore] so that cargo test does not fail in CI when the relay is not available', and conformance_multitenant.rs's A/B isolation tests carry the literal #[tokio::test] #[ignore] attribute pair."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
  - statement: "This repository's own root CLAUDE.md names four of those suites explicitly as the E2E test guide's entry points: e2e_relay.rs (WebSocket relay protocol), e2e_media.rs (media upload/download / Blossom), e2e_media_extended.rs (extended media scenarios), and e2e_nostr_interop.rs (NIP-50 search, NIP-10 threads, NIP-17 gift wraps)."
    entry_class: FACT
    evidence:
      - "CLAUDE.md:252-255"
  - statement: "TESTING.md states plainly that neither `just test-unit` nor `just test` runs the E2E suites in buzz-test-client -- 'those are marked #[ignore] and require a running relay' -- and gives the manual invocation as 'cargo test -p buzz-test-client -- --ignored' against a relay started separately."
    entry_class: FACT
    evidence:
      - "TESTING.md:10-17"
  - statement: "scripts/run-tests.sh -- the script both `just test` and `just test-unit` shell out to -- contains no `cargo test -p buzz-test-client` or `cargo nextest run -p buzz-test-client` invocation at any point in the file (checked directly, not inferred from TESTING.md's prose): grepping the whole script for the crate name and for `-p buzz-test-client` returns no matches."
    entry_class: FACT
    evidence:
      - "scripts/run-tests.sh"
  - statement: "buzz-test-client's own src/lib.rs ships four infra-free unit tests under #[cfg(test)] mod tests (parse_relay_messages, parse_unknown_message_type_errors, auth_event_has_relay_and_challenge_tags, text_event_carries_h_tag) that need no live relay and carry no #[ignore] -- but because run-tests.sh never enumerates `-p buzz-test-client` at all (previous entry) and the Justfile states directly that 'nothing in CI runs `cargo test --workspace` -- workspace membership alone buys clippy/check, not a single executed test', these four tests run in no CI lane today, the same gap the Justfile documents by name for buzz-backend-kubernetes and buzz-agent's corpora."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/src/lib.rs:218-351"
      - "scripts/run-tests.sh"
      - "Justfile:349-351"
  - statement: "buzz-relay declares buzz-test-client as a [dev-dependencies] path dependency, with a comment naming the exact reason: 'Relay-driven mesh lifecycle smoke (examples/mesh_relay_lifecycle_smoke.rs): the relay client for discovery notes and the exact ed25519 the mesh owner keys use for binding verification.' -- BuzzTestClient is imported there for relay-as-control-plane mesh join/deny flows, the one place outside its own crate that consumes the library."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml:88-94"
      - "crates/buzz-relay/examples/mesh_relay_lifecycle_smoke.rs"
  - statement: "A second reference to buzz-test-client exists in crates/buzz-relay/src/state.rs as a forward-looking code comment only ('Conformance tests overwrite this with a JsonlTracer after construction (see test helpers in `crates/buzz-test-client` once those land)') -- not an actual dependency edge, and the comment's own wording ('once those land') marks the described helper as not yet present at this revision."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:943-946"
  - statement: "architecture-containers-relay (a merged corpus node on origin/launchpad) already names crates/buzz-test-client/tests/e2e_relay.rs and sibling e2e suites as the relay container's own Verification evidence, in its 'Implementation, verification and neighboring references' section -- confirming the relay-testing relationship this node's own `references` edge formalizes from the other direction."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/relay.md"
  - statement: "At the recorded revision, git ls-tree -r --name-only HEAD -- launchpad/docs/corpus lists no implementation/ or verification/-typed node other than this one being authored -- so architecture-containers-relay is the only existing corpus node this document has a verified, resolvable relationship target for; the realization target this template asks for (the repository's own testing approach, described in prose in TESTING.md and ARCHITECTURE.md, not as a corpus node) has no corpus node id yet, so no `implements` edge is declared per AGENTS.md's rule against inventing edges to ids that do not exist."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='HEAD', path='launchpad/docs/corpus') -> AGENTS.md, README.md, architecture/**, schema/**, standards/**, templates/**, at commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
---

# `buzz-test-client`: implementation reference

This node documents `crates/buzz-test-client` -- the Rust crate this
repository's own root `CLAUDE.md` and the crate's own `Cargo.toml` both
describe as "Integration test client and E2E test suite for Buzz". It is
`type: verification` rather than `type: implementation`: the crate's whole
purpose is to exercise other Buzz code end to end, not to ship product
behavior of its own, and `node.schema.json`'s enum carries `implementation`
and `verification` as siblings precisely so a corpus author can make that
distinction. What it claims to realize is not a single spec or ADR but this
repository's own documented testing approach -- the client side of the NIP-01
WebSocket protocol (plus NIP-42 authentication) used to drive `buzz-relay`
through its real wire surface, as narrated in `TESTING.md` and
`ARCHITECTURE.md` -- which has no corpus node id of its own yet.

## Target

What is being "implemented" here is this repository's own E2E/integration
testing approach for `buzz-relay`, documented today as prose rather than as a
corpus node:

- `TESTING.md` (repository root) -- the canonical runbook: how to run
  `just test-unit` / `just test`, how to start a live relay, and the explicit
  statement that `buzz-test-client`'s own E2E suites are excluded from both
  and must be run manually.
- `ARCHITECTURE.md` and root `CLAUDE.md` §"Testing" -- name the four
  representative E2E suites (`e2e_relay.rs`, `e2e_media.rs`,
  `e2e_media_extended.rs`, `e2e_nostr_interop.rs`) as the multi-agent E2E test
  guide's entry points.

Neither document carries a corpus node id at this revision, so this node
names them by path in this section rather than declaring an `implements` edge
to an id that does not exist -- per `AGENTS.md`'s rule that an edge to a
nonexistent id is a hard validation error, not a soft placeholder.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `src/lib.rs` -- `BuzzTestClient` (`connect`, `connect_unauthenticated`, `authenticate`, `authenticate_with_nip_oa`, `send_event`, `send_text_message`, `subscribe`, `close_subscription`, `send_raw`, `recv_event`, `collect_until_eose`, `disconnect`) | The client-side NIP-01 WebSocket protocol (EVENT/REQ/CLOSE/subscribe) plus NIP-42 authentication, wrapping `buzz-ws-client`'s `NostrWsConnection` rather than reimplementing the wire protocol | This is the crate's one public library entry point; every consumer below goes through it |
| `crates/buzz-ws-client` (dependency, not owned by this crate) | The actual NIP-42 WebSocket connect/auth/publish mechanics `BuzzTestClient` wraps | Named here because it is the dependency doing the protocol work this crate's public API exposes; this crate's own `TestClientError` wraps `buzz-ws-client::WsClientError` variant-for-variant |
| `src/main.rs` (bin `buzz-test-cli`) | An operator-facing manual send/subscribe CLI against a running relay (`--send`, `--subscribe`, `--channel`, `--kind`) | Not test-harness code; a human-driven debugging tool built on the same library |
| `src/bin/mention.rs` | Sends one `@mention`-tagged event to a channel | Manual smoke tool, not part of any automated suite |
| `src/bin/wamp_bench.rs` | Paced `kind:9` load generator for relay write-amplification benchmarking, emitting per-connection OK-latency samples | Performance tooling, not a correctness test |
| `tests/*.rs` (19 files: `e2e_relay.rs`, `e2e_media.rs`, `e2e_media_extended.rs`, `e2e_nostr_interop.rs`, `conformance_multitenant.rs`, and 14 further suites) | The repository's E2E/integration test surface for the relay's WebSocket, HTTP, media, git, workflow, mesh and multi-tenancy behavior | Every file in this directory is `#[ignore]`d and requires a running relay; none run under `just test` or `just test-unit` |
| `src/lib.rs` `#[cfg(test)] mod tests` (`parse_relay_messages`, `parse_unknown_message_type_errors`, `auth_event_has_relay_and_challenge_tags`, `text_event_carries_h_tag`) | Infra-free unit coverage of relay-message parsing and NIP-42/`h`-tag event shaping | See *Divergences* -- these are not `#[ignore]`d but still run in no enumerated CI lane today |

## Divergences

- **The crate's own infra-free unit tests run in no CI lane.** `src/lib.rs`'s
  four `#[cfg(test)]` tests need no live relay and carry no `#[ignore]`, so on
  their face they look like exactly the kind of test `just test-unit` exists
  to run. But `scripts/run-tests.sh` -- the script both `just test-unit` and
  `just test` invoke -- never enumerates `-p buzz-test-client` anywhere in the
  file (checked by reading the whole script, not by inference), and the
  `Justfile` states directly, for the same reason it excludes other crates'
  otherwise-unit-shaped tests, that "nothing in CI runs `cargo test
  --workspace` -- workspace membership alone buys clippy/check, not a single
  executed test." So these four tests are real, fast, and currently exercised
  by no automated gate; they would need to be added to `run-tests.sh`'s
  explicit per-crate list (the same pattern already used for
  `buzz-backend-kubernetes` and `buzz-agent`) to close the gap. This was
  found by reading `run-tests.sh` end to end and cross-checking against the
  `Justfile`'s own stated policy, not assumed from `TESTING.md`'s prose about
  the `#[ignore]`d E2E suites, which is a separate and correctly-documented
  exclusion.
- **No divergence found in what `TESTING.md` claims versus what the code
  does for the `#[ignore]`d E2E suites.** `TESTING.md`'s statement that
  neither `just test-unit` nor `just test` runs `buzz-test-client`'s E2E
  suites, and that they require `cargo test -p buzz-test-client --
  --ignored` against a running relay, was checked directly against
  `e2e_relay.rs`'s module doc, `conformance_multitenant.rs`'s test
  attributes, and `scripts/run-tests.sh`'s full contents -- all three agree.

## Verification

- **Automated, but not via `just test`/`just test-unit`.** The crate's 19
  E2E/integration suites are real `cargo test` targets, gated behind
  `#[ignore]`, run manually with `cargo test -p buzz-test-client --
  --ignored` (optionally `--test <name>` for one suite) against a relay
  started per `TESTING.md`'s "Live Local Relay" section. `desktop`'s own
  Playwright E2E suites are a separate mechanism and do not exercise this
  crate.
- **The crate's own unit tests: none currently gated.** See *Divergences*
  above -- `src/lib.rs`'s four `#[cfg(test)]` tests are real and passing
  today but are not wired into any enumerated CI job.
- **Consumed as a dev-dependency, exercised only when its consumer is run.**
  `buzz-relay`'s `examples/mesh_relay_lifecycle_smoke.rs` imports
  `BuzzTestClient` for its relay-as-control-plane mesh join/deny scenario;
  that example is a `cargo run --example` target, not a `cargo test`, so
  building it (via `cargo check`/`cargo build` in CI) is the only automatic
  signal that this dependency edge still compiles.

## Relationships

- references: architecture-containers-relay

## Scope and omissions

**This node covers** what `buzz-test-client` is responsible for (a WebSocket
test-client library plus manual CLI/benchmark binaries and the repository's
E2E integration suites), its public library entry point (`BuzzTestClient`
and its re-exports from `buzz-ws-client`), its important dependency
(`buzz-ws-client`, which does the actual NIP-42 protocol work), representative
tests, and precisely where the crate's tests do and do not run in this
repository's automated gates.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full content of any individual E2E suite (what `e2e_relay.rs`, `e2e_media.rs`, etc. each assert) | The suites themselves, and `TESTING.md`'s multi-agent E2E guide |
| `buzz-ws-client`'s own implementation detail (connection lifecycle, message framing) | A future `implementation-crates-buzz-ws-client` node, not yet authored |
| `buzz-relay`'s own responsibility and interfaces | `architecture-containers-relay` |
| The relay's own protocol pipeline and endpoint table | `ARCHITECTURE.md` |
| Desktop's Playwright E2E harness (a separate, non-Rust test mechanism) | `desktop/tests/e2e/` and `CLAUDE.md`'s "Writing E2E Screenshot Specs" section |

**No `implements` edge declared.** See *Target* above: the repository's own
testing-approach documentation has no corpus node id at this revision, so
none is invented.

**Expected but not verified when this node was written:**

- Whether the `src/lib.rs` unit-test CI gap named in *Divergences* is already
  tracked by an open issue was not checked; an author closing that gap should
  search before filing a new one.
- Whether any of the 19 test files besides `e2e_relay.rs` and
  `conformance_multitenant.rs` deviates from the "all `#[ignore]`d" pattern
  was not checked file-by-file; the claim rests on those two files' explicit
  module documentation and attributes plus the crate-wide framing in
  `TESTING.md`, not an exhaustive per-file `#[ignore]` grep.
