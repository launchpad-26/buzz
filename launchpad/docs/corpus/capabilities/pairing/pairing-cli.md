---
id: capabilities-pairing-pairing-cli
type: capabilities
status: draft
origin: launchpad
audiences:
  - developer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "crates/buzz-pairing-cli is a Cargo package named buzz-pairing-cli, producing a single binary named buzz-pair from src/main.rs, and its own Cargo.toml description field states its purpose as 'CLI tool for NIP-AB device pairing interop testing'."
    entry_class: FACT
    evidence:
      - "crates/buzz-pairing-cli/Cargo.toml:2"
      - "crates/buzz-pairing-cli/Cargo.toml:8"
      - "crates/buzz-pairing-cli/Cargo.toml:10-12"
  - statement: "The crate is a member of the root Cargo workspace, so `cargo build --release -p buzz-pairing-cli` builds it as part of a normal repository build rather than requiring a separate toolchain or out-of-tree setup."
    entry_class: FACT
    evidence:
      - "Cargo.toml:22"
  - statement: "The buzz-pair binary exposes exactly three subcommands -- source, target and test-vectors -- defined as a clap derive enum: source generates an ephemeral keypair and session secret and displays a nostrpair:// QR URI; target reads a nostrpair:// URI from stdin and connects to the relay it encodes; test-vectors prints derived cryptographic values from the NIP-AB spec's fixed test keys with no network activity."
    entry_class: FACT
    evidence:
      - "crates/buzz-pairing-cli/src/main.rs:45-71"
      - "crates/buzz-pairing-cli/src/main.rs:335-374"
  - statement: "source and target both drive buzz_core::pairing::session::PairingSession over a live Nostr relay reached via tokio-tungstenite, subscribing to and publishing event kind 24134 (KIND_PAIRING, defined in buzz-core), and perform NIP-42 relay authentication before subscribing so the tool works against Buzz relays out of the box."
    entry_class: FACT
    evidence:
      - "crates/buzz-pairing-cli/src/main.rs:18-25"
      - "crates/buzz-pairing-cli/src/main.rs:126-135"
      - "crates/buzz-core/src/kind.rs:465"
      - "crates/buzz-pairing-cli/README.md:54"
  - statement: "Both source and target require an explicit human confirmation step ('Does your other device show <SAS>? [y/n]') before the protocol proceeds past SAS verification, and the target subcommand gates printing the received secret behind an explicit --show-secret flag that defaults to off."
    entry_class: FACT
    evidence:
      - "crates/buzz-pairing-cli/src/main.rs:156-161"
      - "crates/buzz-pairing-cli/src/main.rs:287-296"
      - "crates/buzz-pairing-cli/src/main.rs:64-66"
  - statement: "The crate's own README states this tool is 'designed for interop testing and NIP submission, not production use,' and documents an automated two-process end-to-end test script plus a manual two-terminal workflow against a locally run buzz-relay, both exercised over the real WebSocket protocol rather than mocked."
    entry_class: FACT
    evidence:
      - "crates/buzz-pairing-cli/README.md:3"
      - "crates/buzz-pairing-cli/README.md:70-99"
  - statement: "crates/buzz-pairing-cli/src/main.rs contains no #[cfg(test)] module and no #[test] functions, so the crate has no automated test coverage of its own; the README's e2e script (.scratch/e2e-pair-local.sh) is a manual/scripted interop check rather than a `cargo test` target."
    entry_class: FACT
    evidence:
      - "crates/buzz-pairing-cli/src/main.rs"
      - "crates/buzz-pairing-cli/README.md:70-80"
  - statement: "The root AGENTS.md lists buzz-pairing-cli under the 'Clients + interop' grouping of crates, describing it as 'CLI for NIP-AB device pairing interop testing,' distinguishing it from buzz-pair-relay (the pairing sidecar relay) in the same grouping."
    entry_class: FACT
    evidence:
      - "AGENTS.md:77"
      - "AGENTS.md:76"
  - statement: "The NIP-AB spec document that this CLI exercises (crates/buzz-core/src/pairing/NIP-AB.md) is marked `draft` `optional`, and no corpus node for that spec, for buzz-pair-relay, or for the PairingSession state machine was merged to origin/launchpad's corpus tree at the recorded revision, so this node declares no relationships."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md:1-7"
  - statement: "Issue #613 (parent Feature for this batch) assigns issue #801 the exact target path launchpad/docs/corpus/capabilities/pairing/pairing-cli.md, distinct from sibling tasks #800 (device-pairing, overall), #802 (pairing-relay) and #803 (pairing-session)."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#801 issue body (read directly via gh issue view)"
relationships:
  - type: part-of
    target: capabilities-pairing-device-pairing
---

# NIP-AB pairing interop-testing CLI: capability

`buzz-pairing-cli` (binary `buzz-pair`) lets a developer or agent exercise the
full NIP-AB device-pairing protocol end to end from the command line, against
any live Nostr relay, without a paired mobile/desktop app on either side. One
process plays the `source` device (holds the secret, shows a QR URI) and
another plays the `target` device (scans the URI, receives the secret); both
display a human-verifiable 6-digit SAS code and require an explicit
confirmation before the transfer completes. A third subcommand,
`test-vectors`, prints the protocol's fixed-key derived values with no network
activity at all, for cross-checking a NIP-AB implementation against the spec
offline. The tool exists specifically to make NIP-AB interoperable and
submittable as a NIP: it is how someone other than Buzz's own client can prove
their implementation of the protocol talks to Buzz's, and vice versa.

## Maturity

Shipped. `crates/buzz-pairing-cli` is a real Cargo workspace member producing
a working `buzz-pair` binary with three implemented subcommands driving the
production `PairingSession` state machine from `buzz-core` over a real
WebSocket connection, not a stub or a design document. It carries no automated
test suite of its own (no `#[test]` in `src/main.rs`); its own README
documents a manual two-terminal workflow and a separate scripted end-to-end
check as the way it is currently verified, which is weaker assurance than a
`cargo test` target but is still evidence of the tool being exercised, not
merely written.

## Boundary

This node does not describe:
- **The NIP-AB protocol itself** -- its message types, cryptographic
  derivations, and state machine are specified in
  `crates/buzz-core/src/pairing/NIP-AB.md` and implemented in
  `crates/buzz-core/src/pairing/`. This node describes the CLI that *drives*
  that implementation, not the protocol's own rules.
- **`buzz-pair-relay`**, the ephemeral sidecar relay used for NIP-AB pairing
  in other contexts (per `AGENTS.md`'s "Clients + interop" listing) -- a
  separate crate from `buzz-pairing-cli` and not exercised by it; `buzz-pair`
  connects to an arbitrary relay URL supplied on the command line, public or
  local, not specifically to `buzz-pair-relay`.
- **The `PairingSession` state machine's internal logic** (SAS derivation,
  transcript-hash verification, abort handling) -- that lives in
  `crates/buzz-core/src/pairing/session.rs` and is only *invoked* by this CLI.
- **Any production, end-user pairing UI.** The CLI is explicitly a testing and
  spec-validation tool ("not production use," per its own README), not the
  pairing experience end users see in the desktop or mobile apps, if or when
  one exists.

## Relationships

None declared. `launchpad/docs/corpus/capabilities/` does not yet exist on
`origin/launchpad` at the recorded revision, and no corpus node for the
NIP-AB protocol, `buzz-pair-relay`, or `PairingSession` (sibling batch tasks
#800/#802/#803) is merged there either -- a `references` edge to any of them
would target an id no loaded node carries, which `validate.py` treats as a
hard error. Add `references` edges to those nodes once they merge.

## Scope and omissions

**This node covers** what `buzz-pairing-cli` (binary `buzz-pair`) is, the
three subcommands it exposes, the human-in-the-loop confirmation and
secret-display safeguards it enforces, its relay-agnostic and NIP-42-aware
connection behavior, its stated purpose (interop testing and NIP submission,
not production use), and its current test-coverage shape (none automated;
manual/scripted only).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The NIP-AB protocol's message formats and cryptography | `crates/buzz-core/src/pairing/NIP-AB.md` (no corpus node yet) |
| `PairingSession`'s internal state machine | `crates/buzz-core/src/pairing/session.rs` (no corpus node yet) |
| `buzz-pair-relay`, the pairing sidecar relay | batch sibling #802 (no corpus node yet) |
| Overall device-pairing capability (product-level) | batch sibling #800 (no corpus node yet) |
| Any production pairing UI in desktop/mobile | not yet built, per this crate's own README |

**Expected but not verified when this node was written:**
- The `.scratch/e2e-pair-local.sh` script referenced by the crate's README was
  not executed as part of drafting this node; its existence and documented
  behavior are taken from the README text, not from running it.
- Whether `buzz-pair` is used in any CI job (as opposed to only manual/local
  interop testing) was not checked; no CI workflow reference to it was found
  during this pass but the search was not exhaustive.
