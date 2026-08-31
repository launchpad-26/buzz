---
id: implementation-crates-buzz-pairing-cli
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3 on branch launchpad."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "buzz-pairing-cli is a Rust crate at crates/buzz-pairing-cli producing a single binary, buzz-pair, described in its own manifest as a 'CLI tool for NIP-AB device pairing interop testing', and its README states explicitly it is 'designed for interop testing and NIP submission, not production use'."
    entry_class: FACT
    evidence:
      - "crates/buzz-pairing-cli/Cargo.toml"
      - "crates/buzz-pairing-cli/README.md"
  - statement: "The crate's entire implementation is one file, crates/buzz-pairing-cli/src/main.rs (624 lines) -- there is no src/ module tree, no lib target, and no test file anywhere under crates/buzz-pairing-cli."
    entry_class: FACT
    evidence:
      - "crates/buzz-pairing-cli/src/main.rs"
      - "crates/buzz-pairing-cli/Cargo.toml"
  - statement: "The NIP-AB device-pairing protocol's state machine (PairingSession), cryptographic key/SAS/transcript derivation (derive_session_id, derive_sas, derive_transcript_hash), and QR URI encode/decode (encode_qr, decode_qr) all live in buzz-core's pairing module (crates/buzz-core/src/pairing/{session,crypto,qr}.rs), not in buzz-pairing-cli; main.rs imports these as a library and calls them, it does not reimplement any of them."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/session.rs"
      - "crates/buzz-core/src/pairing/crypto.rs"
      - "crates/buzz-core/src/pairing/qr.rs"
      - "crates/buzz-pairing-cli/src/main.rs"
  - statement: "buzz-pairing-cli opens its own outbound WebSocket connection directly via the tokio-tungstenite crate (connect_async, imported and called in main.rs) rather than through buzz-ws-client; buzz-ws-client does not appear in crates/buzz-pairing-cli/Cargo.toml's dependency list at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-pairing-cli/src/main.rs"
      - "crates/buzz-pairing-cli/Cargo.toml"
  - statement: "This directly contradicts one clause of a claim in the already-merged corpus node architecture-context-nostr-network, which states 'the crates that do open outbound Nostr WebSocket connections (buzz-acp, buzz-pairing-cli, via buzz-ws-client) connect to buzz-relay or buzz-pair-relay' -- buzz-pairing-cli is not reached via buzz-ws-client. Per ADR-0029's precedence rule, executable evidence (the dependency list and import statements) outranks the existing prose for how the system currently behaves; this discrepancy is reported here rather than silently resolved, and fixing the other node's text is left to whoever next touches it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/context/nostr-network.md"
      - "crates/buzz-pairing-cli/Cargo.toml"
  - statement: "crates/buzz-core/src/pairing/NIP-AB.md is this repository's copy of the NIP-AB device-pairing specification; it defines the kind:24134 event type, the QR payload format, event validation rules, the five-step pairing protocol (subscribe, offer, SAS verification, payload transfer, completion), a Test Vectors section giving fixed derived values, and Security Considerations including a MUST requirement to store imported key material in platform-secure storage."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md"
  - statement: "buzz-core/src/kind.rs defines KIND_PAIRING as the constant 24134, and main.rs's REQ subscriptions for both the source and target subcommands filter on { \"kinds\": [KIND_PAIRING], \"#p\": [<own ephemeral pubkey>] }, matching NIP-AB's documented subscription filter shape."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-pairing-cli/src/main.rs"
      - "crates/buzz-core/src/pairing/NIP-AB.md"
  - statement: "The source subcommand's cmd_source function (main.rs, spanning the Cmd::Source match arm and its handler) drives the full source-side protocol: resolve payload, create a PairingSession via PairingSession::new_source, print the QR URI, connect over WebSocket, perform optional NIP-42 auth, subscribe and wait for EOSE, loop on wait_for_event calling session.handle_offer until a valid offer yields a SAS code, prompt the user to confirm the SAS, call session.confirm_sas and session.send_payload, then loop again waiting for session.handle_complete."
    entry_class: FACT
    evidence:
      - "crates/buzz-pairing-cli/src/main.rs"
  - statement: "The target subcommand's cmd_target function reads a nostrpair:// URI from stdin, decodes it via decode_qr, optionally overrides the relay, creates a PairingSession via PairingSession::new_target, connects and performs the same NIP-42 auth handshake, subscribes and waits for EOSE before publishing its offer event (explicitly ordered this way in a code comment to avoid a race with a fast sas-confirm from the source), displays its own SAS code, waits for session.handle_sas_confirm, prompts the user to confirm, calls session.confirm_target_sas, waits for session.handle_payload, prints the received payload (gated behind --show-secret), and finally calls session.send_complete."
    entry_class: FACT
    evidence:
      - "crates/buzz-pairing-cli/src/main.rs"
  - statement: "The test-vectors subcommand's cmd_test_vectors function derives session_id, the ECDH shared secret, the SAS code, and the transcript_hash from three fixed hardcoded private keys and prints them as a table; NIP-AB.md's own Test Vectors section states 'Implementations MUST validate against these vectors. They can be reproduced with `buzz-pair test-vectors`', naming this exact subcommand as the spec's own reference reproduction tool."
    entry_class: FACT
    evidence:
      - "crates/buzz-pairing-cli/src/main.rs"
      - "crates/buzz-core/src/pairing/NIP-AB.md"
  - statement: "NIP-AB.md's Secure Storage subsection states unconditionally that 'after importing a key, clients MUST store it in platform-secure storage' (Keychain, Android Keystore, or an OS credential manager) with no stated exception for testing tools, while buzz-pairing-cli's cmd_target prints the received secret to stdout when --show-secret is passed and otherwise discards it in-process -- it stores nothing anywhere. Given the crate's own README self-description as an interop-testing tool and not a production client, this reads as a deliberate, disclosed divergence rather than undetected drift."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md"
      - "crates/buzz-pairing-cli/src/main.rs"
      - "crates/buzz-pairing-cli/README.md"
  - statement: "NIP-AB.md's Error Handling subsection states that if a device does not receive the expected next message in a reasonable time it SHOULD send an abort with reason 'timeout' and terminate the session; buzz-pairing-cli's wait_for_event and wait_for_eose helpers instead return CliError::Timeout on expiry, which main's top-level handler prints to stderr and exits the process with code 1 -- no abort event is constructed or sent on the local-timeout path in either cmd_source or cmd_target."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md"
      - "crates/buzz-pairing-cli/src/main.rs"
  - statement: "The launchpad-26/buzz#476-linked ecosystem audit (audit-2026-08-18-full-ecosystem.md) records finding BL2: buzz-pairing-cli's source --nsec flag is a plain clap #[arg(long)] with no env attribute, so a secret nsec passed on the command line lands in argv (visible via ps aux, /proc/<pid>/cmdline, and shell history) even though the crate's own Cargo.toml already enables clap's 'env' feature; this was independently confirmed by reading main.rs's Source variant definition directly, which shows nsec: Option<String> under a bare #[arg(long)] with no env or hide_env_values attribute."
    entry_class: FACT
    evidence:
      - "launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md"
      - "crates/buzz-pairing-cli/src/main.rs"
      - "crates/buzz-pairing-cli/Cargo.toml"
  - statement: "The same audit document states 'buzz-admin and buzz-pairing-cli (the two crates holding BL1/BL2) have zero tests at all', matching this node's own direct finding that no test file exists anywhere under crates/buzz-pairing-cli; the crate does compile as an ordinary member of the cargo workspace, so its only current verification is that it builds, not that its protocol behavior is correct."
    entry_class: FACT
    evidence:
      - "launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md"
      - "crates/buzz-pairing-cli/Cargo.toml"
  - statement: "launchpad/docs/Observability/current-state/coverage.md lists the buzz-pair process (row T06) as 'Included runnable first-party protocol client; component runtime signal behavior awaits #476' and 'Pending assessment' for observability status, corroborating that this crate has no established runtime-signal or test-coverage story yet."
    entry_class: FACT
    evidence:
      - "launchpad/docs/Observability/current-state/coverage.md"
  - statement: "crates/buzz-pairing-cli/README.md documents an automated end-to-end test script at .scratch/e2e-pair-local.sh using `expect` to drive source and target as PTY subprocesses, but .scratch/ is listed in the repository's own .gitignore, so this script is a local, untracked convenience and not present in any checkout of this repository -- it cannot be inspected or relied upon as committed verification."
    entry_class: FACT
    evidence:
      - "crates/buzz-pairing-cli/README.md"
      - ".gitignore"
  - statement: "The already-merged architecture-context-nostr-network node cites crates/buzz-pairing-cli/src/main.rs directly as evidence for how device-pairing peers reach buzz-pair-relay, making it a legitimate references target: it supplies supporting architectural context (where this crate sits in the wider Nostr network topology) without itself being a spec this crate implements or a broader node this one is part of."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/context/nostr-network.md"
  - statement: "The only other corpus node whose id could plausibly be confused with this crate by name, architecture-containers-cli, documents crates/buzz-cli (binary `buzz`, the unrelated agent-facing relay CLI) -- its own Cargo.toml, package name, and command surface share no code with crates/buzz-pairing-cli (binary `buzz-pair`); it is not a valid relationship target for this node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/cli.md"
      - "crates/buzz-pairing-cli/Cargo.toml"
relationships:
  - type: references
    target: architecture-context-nostr-network
---

# buzz-pairing-cli: implementation reference

`buzz-pairing-cli` (crate `crates/buzz-pairing-cli`, binary `buzz-pair`) is a
single-file, single-binary Rust CLI whose sole purpose is to drive the
**NIP-AB device-pairing protocol** end to end over a live Nostr relay, for
interop testing and NIP submission. It claims to realize `crates/buzz-core/
src/pairing/NIP-AB.md` -- this repository's copy of the NIP-AB
specification -- as a runnable reference client: its `source` and `target`
subcommands each drive one side of the five-step pairing handshake the spec
defines, and its `test-vectors` subcommand is the spec's own named
reproduction tool for its fixed cryptographic test values.

## Target

What is being implemented is `crates/buzz-core/src/pairing/NIP-AB.md`, a
Markdown NIP document living inside the `buzz-core` crate rather than a
corpus node -- it has no corpus node id today, so no `implements` edge is
declared toward it (inventing one would be a hard validation error). A
reader can open the spec directly at that path; its `Pairing Protocol`,
`Event Validation`, `Test Vectors`, and `Security Considerations` sections
are the sections this node checks the CLI's behavior against.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `Cmd::Source` variant + `cmd_source` (`crates/buzz-pairing-cli/src/main.rs`) | NIP-AB §Pairing Protocol, source role (Steps 1, 3-5) | Resolves the payload to transfer, creates a `PairingSession` via `buzz_core::pairing::session::PairingSession::new_source`, prints the `nostrpair://` QR URI, connects over WebSocket, performs optional NIP-42 auth, subscribes and waits for EOSE, then loops calling `session.handle_offer` until a valid offer yields a SAS code for user confirmation, then `session.confirm_sas` / `session.send_payload`, then waits for `session.handle_complete`. |
| `Cmd::Target` variant + `cmd_target` (same file) | NIP-AB §Pairing Protocol, target role (Steps 2-5) | Reads a QR URI from stdin, decodes it via `buzz_core::pairing::qr::decode_qr`, creates a `PairingSession` via `PairingSession::new_target`, connects, subscribes and waits for EOSE *before* publishing its offer (explicit race-avoidance, see code comment), displays its own SAS code, waits for `session.handle_sas_confirm`, prompts for user confirmation, calls `session.confirm_target_sas`, waits for `session.handle_payload`, prints the payload only behind `--show-secret`, then calls `session.send_complete`. |
| `Cmd::TestVectors` variant + `cmd_test_vectors` (same file) | NIP-AB §Test Vectors | Derives `session_id`, the ECDH shared secret, `sas_code`, and `transcript_hash` from the spec's three fixed hardcoded private keys and prints them as a table. NIP-AB.md names this exact subcommand as its own reproduction tool for these vectors. |
| `handle_nip42_auth` (same file) | Not a NIP-AB requirement; a Buzz-relay compatibility affordance | Waits briefly for a NIP-42 `AUTH` challenge and responds if one arrives, so the tool also works against Buzz relays that require NIP-42 auth; a relay that never challenges is not treated as an error. |
| `parse_auth_challenge`, `publish_event`, `wait_for_event`, `wait_for_eose`, `parse_relay_event` (same file) | Raw relay-message framing (`["EVENT", ...]`, `["EOSE", sub_id]`, `["AUTH", ...]`) around the protocol steps above | Owned entirely by this crate; not shared with `buzz-ws-client` or `buzz-cli`'s own transport (see divergence on the outbound-transport claim below). |
| `resolve_payload`, `hex_to_32`, `read_line`, `read_yes_no` (same file) | CLI-local input handling, not spec behavior | `resolve_payload` parses/validates a supplied `--nsec` or generates a throwaway test key; the rest are small stdio helpers. |
| `buzz_core::pairing::session::PairingSession` and its `new_source`/`new_target`/`handle_*`/`confirm_*`/`send_*`/`abort` methods (`crates/buzz-core/src/pairing/session.rs`) | The protocol *state machine* itself -- session state transitions, peer-pubkey locking, out-of-order/duplicate handling | Owned by `buzz-core`, not this crate; `buzz-pairing-cli` only calls these methods in the sequence the protocol calls for. |
| `derive_session_id`, `derive_sas`, `derive_transcript_hash`, `format_sas` (`crates/buzz-core/src/pairing/crypto.rs`) | NIP-AB §Cryptographic Primitives | Owned by `buzz-core`; `cmd_test_vectors` calls these but does not reimplement the derivations. |
| `encode_qr`, `decode_qr` (`crates/buzz-core/src/pairing/qr.rs`) | NIP-AB §QR Code Format | Owned by `buzz-core`; this crate only calls the encode/decode functions. |

## Divergences

Checked against NIP-AB.md's `Event Validation`, `Security Considerations`,
and `Error Handling` sections directly, three real divergences were found;
none were assumed absent by default.

1. **No platform-secure storage of imported key material (deliberate).**
   NIP-AB.md's `Secure Storage` subsection states unconditionally that
   "clients MUST store imported keys in platform-secure storage," with no
   exception carved out for testing tools. `cmd_target` prints the received
   secret to stdout only when `--show-secret` is passed and otherwise holds
   it in-process and discards it -- it never persists anything. Given the
   crate's own README states it is "designed for interop testing and NIP
   submission, not production use," this reads as a disclosed, deliberate
   divergence rather than undetected drift, but it is a real gap against the
   spec's MUST clause as written.
2. **No `abort` sent on local receive-timeout (drift).** NIP-AB.md's `Error
   Handling` subsection says a device that does not receive the expected
   next message in a reasonable time SHOULD send an `abort` with reason
   `"timeout"` before terminating. `wait_for_event`/`wait_for_eose` instead
   return `CliError::Timeout`, which the top-level `main` handler prints to
   stderr and exits the process with code 1 -- no abort event is constructed
   on either the source or target local-timeout path. This is a SHOULD, not
   a MUST, but nothing in the code or comments flags it as an intentional
   omission.
3. **`--nsec` accepted as a plain CLI argument (drift, tracked).** Not a
   NIP-AB requirement, but a real implementation-quality gap: `Source`'s
   `nsec: Option<String>` field is a bare `#[arg(long)]` with no `env`
   attribute, even though `Cargo.toml` already enables clap's `env` feature
   (used nowhere in this crate). A secret nsec passed this way lands in
   `argv`, visible via `ps aux`/`/proc/<pid>/cmdline`/shell history. This is
   tracked externally as finding BL2 in `audit-2026-08-18-full-ecosystem.md`,
   not fixed by this documentation node.

**Not checked as a divergence:** full step-by-step conformance of
`buzz-core`'s `PairingSession` state machine against every MUST in NIP-AB's
`Event Validation` and `Duplicate Event Handling` sections (peer-pubkey
locking, out-of-order/duplicate discarding, NIP-44 payload-length bounds).
That state machine is owned and implemented by `buzz-core`, not by this
crate -- verifying it belongs to a `buzz-core`-scoped implementation-reference
node, not this one, which only confirms that `buzz-pairing-cli` calls those
methods in the protocol-correct order.

## Verification

**None automated.** No test file exists anywhere under
`crates/buzz-pairing-cli` at the reviewed revision, confirmed directly and
corroborated independently by `audit-2026-08-18-full-ecosystem.md`'s finding
that "buzz-admin and buzz-pairing-cli ... have zero tests at all." The crate
does compile as an ordinary member of the cargo workspace (`cargo build
--workspace` / `cargo check`), so the only verification today is that it
builds, never that its protocol behavior is correct. The README documents a
manual two-terminal smoke test and an `expect`-driven end-to-end script at
`.scratch/e2e-pair-local.sh` -- but `.scratch/` is git-ignored, so that
script is a local convenience, not committed, reviewable, or CI-run
verification. `launchpad/docs/Observability/current-state/coverage.md`
(row T06) independently marks this process's runtime-signal assessment as
still pending.

## Relationships

- references: [architecture-context-nostr-network](../../architecture/context/nostr-network.md) --
  the already-merged node that documents where this crate's outbound
  WebSocket connections sit in Buzz's Nostr network topology (source and
  target devices reaching `buzz-pair-relay`), cited here as supporting
  context, not as a spec this node implements.

No `implements` edge is declared: NIP-AB.md has no corpus node id yet, and
`AGENTS.md` bars inventing one. No `part-of` edge is declared: no broader
`implementation`-typed node exists in the corpus yet for this to sit inside
-- this is the corpus's first node of that type. A companion
implementation-reference node for `buzz-pair-relay` (the relay this CLI's
`source`/`target` subcommands connect to) is being authored in the same
batch run on a separate, unmerged branch and is not a valid relationship
target from here yet; once merged, a `depends-on` or `references` edge
toward it would be the natural next addition.

## Scope and omissions

**This node covers** what `buzz-pairing-cli` is responsible for (driving the
NIP-AB pairing protocol's `source`/`target`/`test-vectors` subcommands over a
live relay connection it opens itself), its public entry points, its
dependency on `buzz-core`'s pairing module for all protocol/crypto/QR logic,
where its behavior diverges from NIP-AB.md's stated requirements, and how
(and how little) that behavior is verified today.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `buzz-core`'s `PairingSession` state machine's own conformance to NIP-AB's `Event Validation`/`Duplicate Event Handling` MUST clauses | A future `buzz-core`-scoped implementation-reference node, not this one |
| `buzz-pair-relay`'s own behavior (session forwarding, expiry, loopback binding) | A companion implementation-reference node for `buzz-pair-relay`, authored in parallel in this same batch, not yet merged |
| `crates/buzz-cli` (binary `buzz`, id `architecture-containers-cli`) | That container's own node -- an unrelated crate despite the name-adjacent `cli` in both crate directories |
| Whether NIP-AB.md itself is accurate to the wire protocol Buzz relays actually enforce | Not this node's subject -- this node checks the CLI against the spec document, not the spec against relay behavior |

**Expected but not verified when this node was written:**

- **Whether `buzz-pair-relay` behaves as this CLI assumes at runtime** --
  this node reads `buzz-pairing-cli`'s source only; no live pairing session
  was actually run against a relay while authoring it.
- **Full line-by-line NIP-44 payload-length bound checking** (132-87472
  base64 characters, per NIP-AB.md's `Event Validation` item 5) --
  confirmed to live in `buzz-core`, not read in enough depth there to state
  as FACT that it is enforced correctly; out of this node's scope per the
  ownership boundary above.
- **Whether `architecture-context-nostr-network`'s `buzz-ws-client` claim
  about `buzz-pairing-cli` was a simple copy-paste from the `buzz-acp`
  half of the same sentence**, or a deliberate but mistaken generalization --
  the cause was not investigated, only the discrepancy itself, which is
  recorded above rather than corrected in that node (out of this task's
  scope).
