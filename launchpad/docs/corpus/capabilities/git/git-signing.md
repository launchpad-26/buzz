---
id: capabilities-git-git-signing
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "git-sign-nostr is a pluggable git signing program (configured via `gpg.format = x509` / `gpg.x509.program`) that signs and verifies git commit and tag objects using the signer's Nostr secp256k1 keypair, per NIP-GS: 'Git Object Signing with Nostr Keys'."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:1-13"
      - "docs/nips/NIP-GS.md:1-13"
  - statement: "Signing produces a BIP-340 Schnorr signature over SHA-256(\"nostr:git:v1:\" || decimal(t) || \":\" || oa_binding || payload), wrapped in a `-----BEGIN SIGNED MESSAGE-----` / `-----END SIGNED MESSAGE-----` armor around a compact JSON envelope (`v`, `pk`, `sig`, `t`, optional `oa`); the domain separator and armor form are deliberately distinct from PGP/SSH signature markers so platforms that only parse those do not misinterpret a NIP-GS signature."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-GS.md:77-124"
      - "crates/git-sign-nostr/src/lib.rs:895-916"
  - statement: "The signing key is loaded in a fixed priority order -- `NOSTR_PRIVATE_KEY` environment variable, then `BUZZ_PRIVATE_KEY`, then a keyfile named by `git config nostr.keyfile` -- accepting either 64-char hex or NIP-19 `nsec1...` bech32, and the raw key material is zeroized after use."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/README.md:29-35"
      - "crates/git-sign-nostr/src/lib.rs:397-451"
  - statement: "An optional NIP-OA owner attestation (`oa` field: owner pubkey, conditions, owner signature) can be embedded in the signature envelope so a verifier can confirm offline that the signing key was authorized by a specific owner key; the implementation rejects a self-attestation (owner pubkey equal to the signer's own pubkey) and enforces the attestation's time-bound conditions against the signing timestamp before embedding it."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-GS.md:368-465"
      - "crates/git-sign-nostr/src/lib.rs:463-549"
  - statement: "Verification-side trust reporting is deliberately limited: `TRUST_FULLY` is emitted only when the verified public key matches `user.signingkey` in local git config, and the implementation's own doc comment states this is advisory only -- not a PKI trust root -- and that callers must not rely on it for security decisions without an external allowlist or owner policy."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:22-31"
      - "docs/nips/NIP-GS.md:261-283"
  - statement: "The capability is shipped: NIP-GS was specified in merged PR #455, implemented in `crates/git-sign-nostr` in merged PR #459, and wired into automatic agent commit signing in merged PR #528."
    entry_class: FACT
    evidence:
      - "commit 1487ce625241f1669546e392c4fa0a116b97c1fd"
      - "commit 1feb18e2e06c0120b3e50611ed5d744fabfd7723"
      - "commit 70a691517bf52f30c710d897a4ece0f53c086dfc"
  - statement: "VISION_PROJECTS.md's own Status table lists 'Git hosting (smart HTTP + NIP-34)' as its own shipped row, but carries no separate row naming git object signing -- this node's maturity claim rests on code and commit evidence rather than a VISION status marker."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:256"
  - statement: "The merged architecture-flows-git-push node already names NIP-GS commit/tag signing as a related but independent concern from the push-transport authentication it documents, stating that NIP-98 authenticates the HTTP request carrying a push while NIP-GS is an optional, orthogonal signature over the git objects themselves that the push flow neither requires nor inspects."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/git-push.md:153-157"
  - statement: "At the recorded revision, `launchpad/docs/corpus/capabilities/` does not yet exist and this is the first node placed under it; of the corpus nodes already present, `architecture-flows-git-push` (type: architecture) is the only one that already resolves as a relationship target for a git-signing capability node, since it already discusses NIP-GS by name in its own scope table."
    entry_class: FACT
    evidence:
      - "find(path='launchpad/docs/corpus/capabilities', ref='cad6c375fdcc590158c1456c9fc7875f0f84a844') -> no such directory"
      - "launchpad/docs/corpus/architecture/flows/git-push.md"
  - statement: "Running `./bin/cargo test -p git-sign-nostr --lib` at the recorded revision produces 55 passing tests and 1 failing test (`test_parse_envelope_rejects_invalid_oa_pubkey`); the passing set includes `test_sign_verify_round_trip` and `test_signing_hash_matches_spec`/`test_signing_hash_with_oa_matches_spec`, which assert the implementation reproduces NIP-GS's own published test-vector hash and signature exactly."
    entry_class: FACT
    evidence:
      - "cargo_test(crate='git-sign-nostr', ref='cad6c375fdcc590158c1456c9fc7875f0f84a844') -> 55 passed, 1 failed (test_parse_envelope_rejects_invalid_oa_pubkey)"
      - "crates/git-sign-nostr/src/lib.rs:1792-2138"
  - statement: "The one failing test is not new: it is a pre-existing, already-reported defect in envelope-parsing validation, tracked as launchpad-26/buzz#199 and closed 2026-08-24 as descoped (deprioritized) rather than fixed -- unrelated to this documentation task and not something this node's authoring touched or altered."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#199 (read directly via gh issue view; issue content is mutable GitHub state, not committed code, so it stays TEAM_KNOWLEDGE rather than FACT per AGENTS.md's rule for issue-only sources)"
relationships:
  - type: references
    target: architecture-flows-git-push
---

# Git commit and tag signing with Nostr keys: capability

A human developer or an autonomous agent can cryptographically sign their git
commits and tags using the same Nostr secp256k1 keypair they already use for
relay authentication, channel membership, and owner attestation — with no
separate GPG key, SSH key, or certificate authority to provision. The
signature is verifiable by any standard `git verify-commit` / `git
verify-tag` invocation configured to use the corresponding verification
program, and it can optionally embed a NIP-OA owner attestation proving an
agent's signing key was authorized by a specific human or organizational
owner key.

## Maturity

**Shipped.** The specification ([NIP-GS](../../../../../docs/nips/NIP-GS.md))
and its implementation (`crates/git-sign-nostr`) are both merged, and the
capability is wired into automatic commit signing for agent processes. See
the evidence ledger for the three merge commits (spec, implementation,
agent-signing integration) that establish this. `VISION_PROJECTS.md`'s own
capability status table tracks "Git hosting" (the smart-HTTP push/clone
transport) as a separate shipped row and does not carry its own line for
object signing — this maturity claim is grounded in the shipped code and its
merge history, not a VISION status marker.

**Representative verification.** `crates/git-sign-nostr`'s own unit test
suite (55 passing / 1 failing at the recorded revision) covers sign/verify
round-tripping and reproduces NIP-GS's own published test vectors exactly
(`test_sign_verify_round_trip`, `test_signing_hash_matches_spec`,
`test_signing_hash_with_oa_matches_spec`). The one failure,
`test_parse_envelope_rejects_invalid_oa_pubkey`, is a pre-existing defect
already tracked and closed-as-descoped in `launchpad-26/buzz#199` — it is
named here rather than silently omitted, and this node makes no claim that
it is fixed.

## Boundary

This node does not describe:

- **How git pushes reach and are authorized by the relay.** That is the
  transport-and-authorization concern of `architecture-flows-git-push`,
  which this node `references`. NIP-98 (HTTP request authentication) and
  NIP-GS (git object signing) are complementary but independent: one
  authenticates the pusher, the other authenticates the committer, and
  neither requires the other.
- **The interface(s) this capability is exposed through** — the
  `git-sign-nostr` CLI's exact invocation contract
  (`--status-fd`, `-bsau`, `--verify`) and the GnuPG status-line protocol it
  speaks to git. No interface-type corpus node exists yet for this surface;
  the crate's own README and doc comments are the current reference.
- **The step-by-step flow of a single sign or verify invocation.** No
  flow-type corpus node exists yet for this capability; `docs/nips/NIP-GS.md`
  is the normative step-by-step specification in the interim.
- **How the running system is operated** (key provisioning to agents,
  rotation, revocation). NIP-GS explicitly defines no key-management,
  rotation, or revocation mechanism of its own — that is out of scope for
  the specification itself, not merely for this node.
- **The implementation's internal safety mechanics** — secret zeroization
  guarantees, the crate's documented `unsafe` blocks for Unix file-descriptor
  handling, and its other "Known Limitations" — beyond what is needed to
  state the capability's trust model above. A future implementation-reference
  node is the right place for those details if one is written.

## Relationships

- references: `architecture-flows-git-push` — the independent, complementary
  push-transport authentication flow that already documents this capability
  as an explicit boundary in its own scope table.

## Scope and omissions

**This node covers** what the git-signing capability lets a user or agent do
(sign and verify git commits/tags with a Nostr key, optionally carrying an
owner attestation), its shipped maturity and the evidence for it, its trust
model at the capability level (`TRUST_FULLY` is advisory, not a PKI root),
and its boundary against the push-transport flow, a not-yet-written interface
node, and a not-yet-written flow node.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Push-transport authentication and authorization | `architecture-flows-git-push` |
| The `git-sign-nostr` CLI's exact invocation contract and GnuPG status-line protocol | a future interface-type node (none exists yet) |
| The step-by-step sign/verify sequence | a future flow-type node (none exists yet); `docs/nips/NIP-GS.md` is the current normative reference |
| Key provisioning, rotation, and revocation for signing keys | out of scope for NIP-GS itself; no corpus node owns this yet |
| Implementation-level safety mechanics (zeroization, `unsafe` fd handling) | a future implementation-reference node, if written |

**Expected but not verified when this node was written:**

- **No live signing or verification was executed.** This node's claims are
  sourced from reading the crate's source, its doc comments, its README, and
  the NIP-GS specification's own test vectors — not from running
  `git-sign-nostr` against a real git repository during this task.
- **Whether any interface- or flow-type corpus node for this capability has
  since been drafted** was checked only against the corpus tree at the
  recorded revision; a later reader should re-check before assuming the two
  "not yet written" rows above still hold.
