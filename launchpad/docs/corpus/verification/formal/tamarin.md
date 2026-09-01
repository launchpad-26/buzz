---
id: verification-formal-tamarin
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
  - statement: "A repository-wide search for the string 'tamarin' and for files with a .spthy extension turns up exactly two real Tamarin theory files -- docs/spec/MultiTenantAuth.spthy and crates/buzz-core/src/pairing/NIP-AB.spthy -- plus prose documents that discuss one or both of them; no other .spthy file and no other protocol-verification tool (ProVerif, CryptoVerif) reference was found anywhere in the repository."
    entry_class: FACT
    evidence:
      - "shell(grep -ril tamarin .) -> docs/multi-tenant-relay.md, docs/spec/MultiTenantAuth.spthy, VISION.md, launchpad/docs/corpus/capabilities/communities/community.md, launchpad/docs/corpus/templates/specification.md, crates/buzz-core/src/pairing/NIP-AB.md"
      - "shell(find . -iname '*.spthy') -> ./docs/spec/MultiTenantAuth.spthy, ./crates/buzz-core/src/pairing/NIP-AB.spthy"
      - "shell(grep -ril 'formal verif\\|proverif\\|symbolic model\\|protocol verification' --include=*.md .) -> docs/nips/NIP-RS.md, launchpad/docs/corpus/capabilities/communities/community.md, crates/buzz-core/src/pairing/NIP-AB.md -- none of these name a tool other than Tamarin/TLA+"
  - statement: "crates/buzz-core/src/pairing/NIP-AB.spthy declares exactly sixteen lemmas: executable_core_flow, payload_requires_successful_sas_match, payload_secrecy_without_endpoint_compromise, target_completion_agrees_on_source_payload, source_completion_implies_prior_target_completion_without_compromise, injective_target_source_agreement, sas_match_implies_genuine_target, payload_delivery_requires_genuine_target, target_decrypts_payload_only_after_dual_consent, executable_with_qr_leak, executable_with_source_compromise, executable_with_target_compromise, decryption_requires_prior_buffering, executable_payload_buffered_before_approval, source_compromise_can_leak_payload, target_compromise_can_leak_payload."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.spthy:290-455"
  - statement: "crates/buzz-core/src/pairing/NIP-AB.md's Formal Verification section (lines 611-676) names the same sixteen lemmas, describes the model as treating the relay and network as a full Dolev-Yao attacker with explicit compromise rules for QR-code exposure, source-session compromise and target-session compromise, states that the model 'intentionally abstracts away' a named list of details (exact NIP-01/Schnorr signatures, exact NIP-44 ciphertext framing, HKDF-SHA256 internals, exact secp256k1 ECDH, SAS-comparison imperfection, timeout/abort branches, duplicate-event bookkeeping, p-tag/replay-protection state machinery, version negotiation, complete success/failure semantics, and payload typing), and gives the invocation `tamarin-prover --prove crates/buzz-core/src/pairing/NIP-AB.spthy`."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md:611-676"
  - statement: "The NIP-AB protocol this model covers is backed by real, shipping implementation code, not only by the model and the prose NIP: crates/buzz-core/src/pairing/ contains crypto.rs, qr.rs, session.rs and types.rs, and two further crates in this workspace exist specifically for it -- buzz-pair-relay ('Ephemeral sidecar relay for NIP-AB device pairing') and buzz-pairing-cli ('CLI for NIP-AB device pairing interop testing')."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/mod.rs"
      - "crates/buzz-core/src/pairing/crypto.rs"
      - "crates/buzz-core/src/pairing/qr.rs"
      - "crates/buzz-core/src/pairing/session.rs"
      - "crates/buzz-pair-relay/Cargo.toml"
      - "crates/buzz-pairing-cli/Cargo.toml"
      - "AGENTS.md"
  - statement: "docs/multi-tenant-relay.md -- the prose specification paired with docs/spec/MultiTenantAuth.spthy, the repository's other Tamarin model -- states in its own Implementation Correspondence section that 'Today there is no community layer; channel_id is the only locality', i.e. the tenancy entity that model's 32 lemmas (S1-S8) reason about does not exist in the codebase this model is checked against; the document itself is marked `draft` at its own top."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-relay.md:3"
      - "docs/multi-tenant-relay.md:884-885"
      - "docs/multi-tenant-relay.md:578-579"
  - statement: "Issue #1370, filed under the same parent Feature #617 as this node's own issue (#1373), has the stated objective 'Create launchpad/docs/corpus/verification/formal/multi-tenant-auth.md as the single canonical test contract node for multi tenant auth' -- i.e. a future test-contract node already claims docs/spec/MultiTenantAuth.spthy as its subject."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1370, read directly via 'gh issue view 1370 --repo launchpad-26/buzz' while authoring this node -- an issue URL is external and unpinnable, so per AGENTS.md this is TEAM_KNOWLEDGE rather than FACT even though the issue was opened and read"
  - statement: "Given that NIP-AB.spthy's protocol has real implementation code behind it today while MultiTenantAuth.spthy's protocol does not yet exist in the codebase it models, and that a separate future node (issue #1370) already claims MultiTenantAuth.spthy as its subject under the same parent feature, this node -- built from the test-contract template's one-obligation shape -- documents the NIP-AB.spthy obligation rather than the MultiTenantAuth.spthy one, to avoid two nodes describing the same artifact and to avoid picking the not-yet-implemented model as a 'must stay true today' obligation."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/pairing/mod.rs"
      - "docs/multi-tenant-relay.md:884-885"
      - "https://github.com/launchpad-26/buzz/issues/1370"
    confidence: 0.8
  - statement: "No GitHub Actions workflow and no Justfile recipe in this repository references tamarin-prover, Tamarin, or either .spthy file by name -- the search returned no matches in either location."
    entry_class: FACT
    evidence:
      - "shell(grep -rl -i tamarin .github/workflows/) -> no matches"
      - "shell(grep -n -i tamarin Justfile) -> no matches"
      - "shell(grep -rl -i tamarin scripts/) -> no matches"
  - statement: "Neither `tamarin-prover` nor `maude` is installed in the environment this node was authored in, so this authoring pass could not itself execute the proof to independently confirm the sixteen lemmas' current pass/fail state; the claim that they are proved rests on crates/buzz-core/src/pairing/NIP-AB.md's own text (cited above), not on an execution performed while writing this node."
    entry_class: FACT
    evidence:
      - "shell(which tamarin-prover) -> tamarin-prover not found"
      - "shell(which maude) -> maude not found"
  - statement: "crates/buzz-core/src/pairing/NIP-AB.md marks the whole NIP-AB protocol `draft` `optional` at its own top and states in its Audit subsection that an independent security audit of the protocol is planned but not yet completed, recommending that implementations in high-security contexts treat the NIP as draft and conduct their own review until an audit exists."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/pairing/NIP-AB.md:7"
      - "crates/buzz-core/src/pairing/NIP-AB.md"
  - statement: "Feature #617's verification/formal/ track additionally includes issue #1369 ('task: document verification/formal/git-object-store.md'), #1371 ('task: document verification/formal/multi-tenant-relay.md'), #1372 ('task: document verification/formal/stateful-gateway.md') and #1374 ('task: document verification/formal/tla-plus.md') -- none of which name Tamarin or a .spthy file in their title, and #1371/#1374 correspond to the two TLA+ files docs/spec/MultiTenantRelay.tla and docs/spec/GitOnObjectStore.tla identified in this node's own repository search."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1369, #1371, #1372 and #1374, read directly via 'gh issue view <n> --repo launchpad-26/buzz' while authoring this node -- issue URLs are external and unpinnable, so per AGENTS.md this is TEAM_KNOWLEDGE rather than FACT even though each issue was opened and read"
  - statement: "Issue #1373's definition of done requires: schema-valid front matter with provenance/evidence and typed relationships; one independently maintainable node, with a newly discovered second obligation filed separately rather than folded in; every substantive claim traceable and classified FACT/INFERENCE/TEAM_KNOWLEDGE; links to relevant implementation/verification/specification without duplicating their content; the draft checked against the recorded revision and against Git/PR/issue history where relevant; clean corpus validation; the body stating preconditions/action/expected outcome, naming negative/error cases that are part of the contract, linking the actual verifying automated/formal/manual check, and not claiming coverage that is not present."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1373 definition of done"
relationships:
  - type: references
    target: corpus-standard-test-references
  - type: references
    target: corpus-standard-code-references
---

# Tamarin formal verification: NIP-AB device pairing — test contract

## Purpose and boundary

This node documents one obligation: that the Tamarin (`tamarin-prover`) symbolic
protocol model of **NIP-AB, Buzz's QR-initiated device-pairing protocol**
(`crates/buzz-core/src/pairing/NIP-AB.spthy`), continues to prove all of its
declared security lemmas. It covers that obligation only.

A repository-wide search (`grep -ril tamarin .`, `find . -iname '*.spthy'`, and a
search for other formal-verification tool names) found exactly **two** real
Tamarin models in this repository, not one: `crates/buzz-core/src/pairing/NIP-AB.spthy`
(device pairing) and `docs/spec/MultiTenantAuth.spthy` (the multi-tenant relay's
NIP-98 mint / bearer-token / per-community signing-key / audit-chain authorization
model, paired with the prose specification `docs/multi-tenant-relay.md`). Both are
real, substantial, already-written models — this is not a "no Tamarin model exists"
node. This node covers only the first of the two; see *Scope and omissions* for why
the second is a distinct, out-of-scope obligation rather than folded in here.

## Obligation

> Every lemma declared in the Tamarin model of the NIP-AB device-pairing protocol
> (`crates/buzz-core/src/pairing/NIP-AB.spthy`) proves under
> `tamarin-prover --prove` — none is reported `falsified` — establishing, under a
> full Dolev-Yao network adversary with explicit QR-leak, source-compromise and
> target-compromise rules, that: an honest source only sends the paired payload
> after a successful SAS (short authentication string) match; the payload stays
> unknown to the attacker unless a session endpoint is separately compromised; a
> completed target session agrees with the source on the exact payload sent, and
> a completed source session agrees that the target actually finished; every SAS
> match is bound to a genuinely target-role-generated key rather than an
> attacker-substituted one; and the target decrypts the payload only after both
> transcript verification and an explicit user-approval step.

The model deliberately does not cover several things named as normative
elsewhere instead (see *Limits*): exact NIP-01/Schnorr signature mechanics,
exact NIP-44 ciphertext framing, HKDF-SHA256's RFC 5869 internals, exact
secp256k1 ECDH, the ~20-bit SAS-collision computational bound, timeout/abort
handling, duplicate-event bookkeeping, `p`-tag replay-protection state
machinery, `offer` version negotiation, `complete` success/failure semantics,
and payload typing.

## Verifying test(s)

- `crates/buzz-core/src/pairing/NIP-AB.spthy` (lines 290-455) — the Tamarin
  theory itself, sixteen lemmas total:
  - **Core security invariants:** `executable_core_flow`,
    `payload_requires_successful_sas_match`,
    `payload_secrecy_without_endpoint_compromise`,
    `target_completion_agrees_on_source_payload`,
    `source_completion_implies_prior_target_completion_without_compromise`,
    `injective_target_source_agreement`.
  - **MITM resistance:** `sas_match_implies_genuine_target`,
    `payload_delivery_requires_genuine_target`.
  - **Dual consent and payload buffering:**
    `target_decrypts_payload_only_after_dual_consent`,
    `decryption_requires_prior_buffering`,
    `executable_payload_buffered_before_approval`.
  - **Reachability / anti-vacuousness** (proving the compromise rules and the
    buffering path are not dead code, so the guards above are non-trivial):
    `executable_with_qr_leak`, `executable_with_source_compromise`,
    `executable_with_target_compromise`, `source_compromise_can_leak_payload`,
    `target_compromise_can_leak_payload`.
- `crates/buzz-core/src/pairing/NIP-AB.md` (lines 611-676) — the prose
  companion document. It names the same sixteen lemmas with a one-line
  description of what each proves, states the model's Dolev-Yao adversary
  assumptions, lists what the model intentionally abstracts away, and gives
  the exact run command reproduced below. It is not itself a second
  independent check — it is the document a reader compares the `.spthy`
  file's actual lemma names against, per this corpus's own citation
  conventions for a claim about what a source states.

## How to run it

```bash
tamarin-prover --prove crates/buzz-core/src/pairing/NIP-AB.spthy
```

This requires a local install of `tamarin-prover` and its `maude` dependency;
neither is part of this repository's Hermit-managed toolchain, `just setup`,
or any CI job (see *Current enforcement status*). A full run reports, per
lemma, `verified` or `falsified`; the obligation above holds only if every one
of the sixteen lemmas reports `verified`.

## Current enforcement status

**Gated** — not pending (a real, substantial theory file exists and is not
stubbed), not verified-in-CI (nothing runs it automatically). Specifically:

- The `.spthy` file and its sixteen lemmas are real and already written —
  this is not an obligation waiting on a model to be built.
- No GitHub Actions workflow, no `Justfile` recipe, and no script under
  `scripts/` references `tamarin-prover`, "Tamarin", or either `.spthy` file
  by name. Running the proof is a manual, local step; nothing in this
  repository's `just ci` or CI pipeline would fail if a change silently broke
  one of these lemmas.
- `crates/buzz-core/src/pairing/NIP-AB.md`'s own text states the lemmas are
  proved. This node's authoring pass could not independently re-execute the
  proof to confirm that claim at the recorded revision: neither
  `tamarin-prover` nor `maude` is installed in the environment this node was
  written in. Per this corpus's evidence standard, a behavior claim needs
  executable evidence checked at the recorded revision, not a memory of it
  passing once — so the "verified" half of this status rests on the cited
  document's own words, honestly attributed as such, not on an independent
  re-run performed here.

## Limits

- **Symbolic, not computational.** Tamarin's Dolev-Yao model treats
  cryptographic primitives as a perfect equational theory (unforgeable
  signatures, opaque hashes, ideal Diffie-Hellman, ideal authenticated
  encryption). It does not model computational attacks on the underlying
  primitives (bit-level forgery, side channels, weak randomness) — those are
  out of scope for any Tamarin proof, not only this one.
- **The SAS comparison is modeled as perfect.** The proof assumes the user's
  visual short-authentication-string comparison always succeeds correctly
  when it should. The real ~20-bit collision probability (1-in-10^6, per
  `NIP-AB.md`) is a separate, non-symbolic computational argument the Tamarin
  model does not itself carry.
- **Named abstractions are not covered at all**, per `NIP-AB.md`'s own list:
  exact NIP-01 event IDs / Schnorr signatures, exact NIP-44 ciphertext
  framing/padding/version bytes/nonce handling, HKDF-SHA256's RFC 5869
  internals (collapsed to tagged hashes), exact secp256k1 ECDH (modeled as
  symbolic Diffie-Hellman), timeout and abort branches, duplicate-event
  bookkeeping, `p`-tag validation and within-session replay protection,
  `offer` version negotiation, `complete` success/failure semantics, and
  payload typing (`nsec` / `bunker` / `connect` / `custom`). Those remain
  normative in the NIP text and the Rust implementation; a passing Tamarin
  run says nothing about whether the Rust code actually implements them
  correctly.
- **The proof is about the model, not the Rust implementation.** Nothing
  connects `crates/buzz-core/src/pairing/NIP-AB.spthy`'s rules to the actual
  Rust in `crates/buzz-core/src/pairing/crypto.rs`, `qr.rs`, `session.rs` and
  `types.rs`, or to `buzz-pair-relay`/`buzz-pairing-cli`, by any mechanical
  check. A model/implementation drift (the model no longer matching what the
  code does) would not be caught by re-running `tamarin-prover` — only by a
  human re-reading both.
- **No regression protection.** Because nothing in CI runs this proof, a
  future edit to the `.spthy` file that silently weakens a lemma's
  guarantees (or an edit that breaks a proof entirely) would not be caught
  automatically. The gate on this obligation staying true is a human
  remembering to re-run it.
- **The protocol itself is still `draft`/`optional` and unaudited.**
  `NIP-AB.md`'s own Audit subsection states an independent security audit is
  planned but not completed. A Tamarin proof is a proof about the *model*'s
  faithfulness to a specification, not a substitute for that audit.
- **This node's own "currently passes" claim is second-hand.** As stated
  under *Current enforcement status*, this authoring pass did not execute
  `tamarin-prover` — the tool was unavailable in this environment. A reader
  relying on "verified" here is relying on `NIP-AB.md`'s text, cited
  honestly as such, not on independent execution performed for this node.

## Scope and omissions

**This node covers** the obligation that NIP-AB.spthy's sixteen lemmas prove
under `tamarin-prover`, what each lemma establishes, how to run the check,
its current (gated, not CI-enforced) status, and the named limits of what a
green run would and would not prove.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `docs/spec/MultiTenantAuth.spthy` — the repository's *other* real Tamarin model (multi-tenant relay authorization: NIP-98 minting, bearer-token confinement, per-community signing keys, per-community audit chains; 32 lemmas across obligations S1-S8) | A distinct, out-of-scope obligation. Issue #1370, filed under this node's own parent Feature #617, already has the stated objective of creating `launchpad/docs/corpus/verification/formal/multi-tenant-auth.md` as "the single canonical test contract node" for this model — this node does not duplicate that future node's subject. It is genuinely a second, separate obligation, not a detail of this one: a different protocol, a different `.spthy` file, a different set of lemmas, and (per `docs/multi-tenant-relay.md`'s own admission that "today there is no community layer") a model of an architecture not yet built, versus this node's model of an already-implemented, already-shipping protocol. |
| `docs/spec/MultiTenantRelay.tla` and `docs/spec/GitOnObjectStore.tla` — TLA+ models, not Tamarin | Feature #617's own `verification/formal/` track: issues #1369, #1371, #1372 and #1374 (git-object-store.md, multi-tenant-relay.md, stateful-gateway.md and tla-plus.md respectively) |
| The content/scope of the NIP-AB protocol itself as a specification (message shapes, versioning rules, cryptographic-primitive rationale, replay protection) | `crates/buzz-core/src/pairing/NIP-AB.md`, the NIP text this node only cites, never restates |
| Whether the Rust implementation in `crates/buzz-core/src/pairing/` actually matches the model's rules | Not established by anything cited here — see *Limits* |
| General rules for how any corpus node cites a test or a piece of code as evidence | `launchpad/docs/corpus/standards/test-references.md`, `launchpad/docs/corpus/standards/code-references.md` (both `references`-linked above) |
| Creating, updating and retiring any corpus node, including this one | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **Whether the sixteen lemmas currently verify was not independently
  re-executed.** `tamarin-prover` and `maude` are not installed in this
  authoring environment; the "proved" claim rests on
  `crates/buzz-core/src/pairing/NIP-AB.md`'s own text, cited as such. The
  first reader with the tooling installed who runs the command in *How to
  run it* is the first independent confirmation.
- **Whether the Rust implementation under `crates/buzz-core/src/pairing/`
  still matches the model's rules was not checked line-by-line.** The two
  were read for their own self-descriptions, not diffed against each other.
- **`docs/spec/MultiTenantAuth.spthy` was read only enough to confirm it is a
  second, real, substantial Tamarin model with a different subject** (to
  justify not folding it into this node) — its own lemma-by-lemma content was
  not analyzed in the depth this node applies to `NIP-AB.spthy`, since that
  analysis belongs to issue #1370's own future node.
