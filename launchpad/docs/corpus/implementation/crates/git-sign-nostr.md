---
id: implementation-crates-git-sign-nostr
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "`git-sign-nostr` is a standalone Unix binary crate (`[[bin]] name = \"git-sign-nostr\"`) with its logic in a co-located library crate (`[lib] name = \"git_sign_nostr\"`), described in its own Cargo.toml as a 'NIP-GS git commit/tag signing program using Nostr secp256k1 keys' and marked `publish = false` as an internal workspace tool."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/Cargo.toml"
  - statement: "The crate's own module doc states it is Unix-only ('Platform: Unix-only (requires file descriptor passing via `--status-fd`)'), and its Cargo.toml confirms this structurally: the `libc` dependency (used for `O_NOFOLLOW`/`fcntl` fd operations) is scoped under `[target.'cfg(unix)'.dependencies]`."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:6"
      - "crates/git-sign-nostr/Cargo.toml:44-45"
  - statement: "The binary is invoked by git as a pluggable `gpg.x509.program` in two modes: signing (`git-sign-nostr --status-fd=<N> -bsau <keyid>`, payload on stdin, armored signature on stdout, GnuPG status lines on fd N) and verification (`git-sign-nostr --status-fd=<N> --verify <sigfile> -`, payload on stdin, status lines on fd N); `parse_args` implements exactly this argument grammar, including duplicate/conflicting-mode rejection and forward-compatible ignoring of unrecognized arguments."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/README.md:37-46"
      - "crates/git-sign-nostr/src/lib.rs:196-282"
      - "docs/nips/NIP-GS.md:46-65"
  - statement: "`load_key` implements NIP-GS's mandated key-loading priority — `NOSTR_PRIVATE_KEY` env var, then `BUZZ_PRIVATE_KEY` env var, then a keyfile at the path named by git config `nostr.keyfile` — accepting hex or NIP-19 bech32 (`nsec1...`), trimming whitespace, and removing the consumed env var from the process environment immediately after reading to shrink the exposure window; this matches NIP-GS's 'Key Loading' section verbatim in ordering and accepted formats."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:397-450"
      - "crates/git-sign-nostr/README.md:29-35"
      - "docs/nips/NIP-GS.md:335-346"
  - statement: "`compute_signing_hash` reproduces NIP-GS's Signing Hash formula (`SHA-256(\"nostr:git:v1:\" || decimal(t) || \":\" || oa_binding || payload)`) byte-for-byte, and the crate's own unit tests (`test_signing_hash_matches_spec`, `test_signing_hash_with_oa_matches_spec`) assert the function's output against the exact hash values published in NIP-GS's own Test Vectors section for the same test key, payload and timestamp."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:895-916"
      - "docs/nips/NIP-GS.md:153-190"
      - "docs/nips/NIP-GS.md:558-570"
      - "crates/git-sign-nostr/src/lib.rs:1809-1826"
  - statement: "`build_envelope` constructs the compact, fixed-field-order JSON envelope (`v, pk, sig, t[, oa]`, no whitespace) by hand with `format!` rather than serde specifically to guarantee byte-exact canonical output, matching NIP-GS's requirement that the signature envelope have exactly one valid byte sequence per set of field values; `do_verify` enforces this on the receiving side by re-running `build_envelope` over the parsed fields and rejecting the signature (`test_verify_rejects_non_canonical_json`) if the reconstruction does not byte-match the decoded input."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:924-935"
      - "crates/git-sign-nostr/src/lib.rs:1174-1188"
      - "docs/nips/NIP-GS.md:113-151"
      - "docs/nips/NIP-GS.md:227-246"
  - statement: "`load_auth_tag` and `verify_oa` implement NIP-GS's optional Owner Attestation (`oa`) field: the auth tag is read from `BUZZ_AUTH_TAG` env var or `nostr.authtag` git config (env var taking precedence), structurally validated (4-element JSON array, 64-hex owner pubkey, 128-hex signature, a constrained conditions grammar), rejected on self-attestation (`oa[0] == pk`), and its embedded signature is verified over the NIP-OA preimage `\"nostr:agent-auth:\" || pk || \":\" || conditions` before being embedded in a new signature — matching NIP-GS's Owner Attestation section and consuming the tag format `docs/nips/NIP-OA.md` (the `auth` tag) defines."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:463-549"
      - "crates/git-sign-nostr/src/lib.rs:1500-1551"
      - "docs/nips/NIP-GS.md:368-476"
      - "docs/nips/NIP-OA.md"
  - statement: "The crate's module doc explicitly states its `TRUST_FULLY` status line is advisory only ('does NOT prove the signer is trusted by any external authority... Callers MUST NOT rely on TRUST_FULLY for security decisions without an external allowlist or owner policy'), and emits an explanatory `NOTATION_DATA advisory-config-match-only` line alongside it; this matches NIP-GS's own Security Considerations note that `TRUST_FULLY` means only 'this is the locally configured signing key', not a PKI trust root."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:24-31"
      - "crates/git-sign-nostr/src/lib.rs:1673-1684"
      - "docs/nips/NIP-GS.md:261-273"
  - statement: "The crate zeroizes secret key material on every exit path: `load_key`/`load_auth_tag` return `Zeroizing<String>`/parsed values, `KeypairGuard` (a RAII wrapper around the signing `Keypair`) calls `non_secure_erase()` on drop, and `do_sign` additionally overwrites the raw `SecretKey`'s stack bytes with `ptr::write_bytes` before dropping it — implementing NIP-GS's 'the program MUST zeroize secret key material from memory after use' requirement, with the module doc's own 'Known Limitations' section disclosing that `secp256k1::SecretKey` upstream lacks `Zeroize`, so some residual copies may persist as a documented, accepted gap rather than a silent one."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:91-110"
      - "crates/git-sign-nostr/src/lib.rs:943-1080"
      - "crates/git-sign-nostr/src/lib.rs:38-44"
      - "crates/git-sign-nostr/src/lib.rs:60-63"
      - "docs/nips/NIP-GS.md:348"
  - statement: "On Unix, keyfile loading (`open_keyfile`) rejects symlinks via `O_NOFOLLOW` (no separate stat-then-open TOCTOU window), then fstats the already-open handle to require permission mode no broader than 0600/0400 and ownership by the current UID — implementing NIP-GS's 'the program MUST verify file permissions are no broader than 0600... If permissions are broader, the program MUST exit with an error' requirement, with an additional UID-ownership check NIP-GS itself does not mandate."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:776-839"
      - "docs/nips/NIP-GS.md:350-352"
  - statement: "The crate's module doc names one deliberate exception to this repository's no-`unsafe`-code rule: 'minimal `unsafe` for Unix fd operations (`from_raw_fd`, `fcntl`) where no safe Rust API exists,' each block documented with its own safety invariants, and states this is 'an accepted exception to the project's no-unsafe rule for this standalone binary.'"
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:49-52"
  - statement: "This crate signs and verifies git commit/tag objects locally (NIP-GS) and is a separate, orthogonal concern from `git-credential-nostr`, which signs a NIP-98 HTTP-auth event to authenticate the `git push`/`git fetch` HTTP request itself; the merged corpus node `architecture-flows-git-push` already records this exact boundary, citing this crate's own README, and `git-credential-nostr`'s README independently confirms its own scope is the NIP-98 credential-helper protocol, not object signing."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/git-push.md"
      - "crates/git-sign-nostr/README.md:37-46"
      - "crates/git-credential-nostr/README.md:41-58"
  - statement: "NIP-GS itself documents that it 'does not require relay changes. Relays are uninvolved — signing and verification happen locally between git and the signing program,' confirming this crate has no server-side counterpart and does not own any part of the object-store/CAS publish path that `architecture-flows-git-push` documents."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-GS.md:40-42"
  - statement: "The crate's verification is a `#[cfg(test)] mod tests` unit-test suite inside `src/lib.rs` (roughly 50 `#[test]` functions), covering NIP-GS spec test-vector reproduction (`test_signing_hash_matches_spec`, `test_signing_hash_with_oa_matches_spec`), a full sign/verify round trip (`test_sign_verify_round_trip`), and rejection paths for a wrong payload, a tampered signature, non-canonical JSON, an invalid/self-attesting owner-attestation pubkey, malformed envelopes (missing/wrong `v`, unknown fields, uppercase hex, out-of-range `t`, wrong-length `sig`), and malformed armor; no `#[ignore]`-gated or live-infrastructure test exists for this crate, and no reference to it was found anywhere under `crates/buzz-test-client/` or `crates/buzz-relay/`, confirming it has no relay-side or e2e counterpart to exercise."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:1791-2508"
      - "crates/git-sign-nostr/src/lib.rs:1808-1814"
      - "crates/git-sign-nostr/src/lib.rs:2055-2064"
      - "crates/git-sign-nostr/src/lib.rs:2092-2116"
  - statement: "At repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3, `docs/nips/NIP-GS.md` has not been given a corpus node id (checked via `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`, which lists no node for it), so no `implements` edge can legally target it; the *Target* section below names it by path instead, per the implementation-reference template's own instruction not to invent an edge to a node id that does not exist."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/implementation-reference.md"
---

# git-sign-nostr: implementation reference

`git-sign-nostr` (`crates/git-sign-nostr`) is a standalone, Unix-only binary
that git invokes as a pluggable signing/verification backend
(`gpg.x509.program`) to sign and verify git commit and tag objects with a
Nostr secp256k1 keypair, using BIP-340 Schnorr signatures. It claims to
realize [NIP-GS](../../../../../docs/nips/NIP-GS.md) ("Git Object Signing
with Nostr Keys") — the wire format, signing-hash construction, key-loading
priority, owner-attestation embedding, and GnuPG status-line protocol this
node's *Implementation surface* table below maps section by section.

## Target

**`docs/nips/NIP-GS.md`** — a `draft`, `optional` NIP defining a signature
format and verification protocol for signing git commits/tags with Nostr
keys via git's `gpg.x509.program` interface. It has no corpus node id at
this node's recorded revision; open it directly at the path above. The
optional owner-attestation (`oa`) field it defines embeds a
[NIP-OA](../../../../../docs/nips/NIP-OA.md) `auth` tag, which this crate
also consumes directly (see *Implementation surface*) but does not itself
implement end-to-end (NIP-OA's own attestation-issuance flow is out of this
crate's scope).

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `Cargo.toml` `[[bin]]`/`[lib]` split, `publish = false` | Crate identity: internal workspace tool, not a published library | Binary name `git-sign-nostr` matches the `gpg.x509.program` path git invokes |
| `parse_args` (`src/lib.rs`) | NIP-GS "CLI Interface": `--status-fd`, `-bsau <key>` (sign), `--verify <file> -` (verify), unrecognized-argument tolerance | Rejects conflicting/duplicate mode flags; requires the trailing `-` stdin marker in verify mode |
| `load_key` (`src/lib.rs`) | NIP-GS "Key Loading": `NOSTR_PRIVATE_KEY` > `BUZZ_PRIVATE_KEY` > `nostr.keyfile` git config, hex or `nsec1...` bech32 | Consumed env vars are removed from the process environment immediately after reading |
| `open_keyfile` / `read_keyfile_secure` (`src/lib.rs`) | NIP-GS keyfile permission requirement (no broader than 0600) | Adds `O_NOFOLLOW` symlink rejection and current-UID ownership check, both beyond NIP-GS's own text |
| `compute_signing_hash` (`src/lib.rs`) | NIP-GS "Signing Hash": `SHA-256("nostr:git:v1:" \|\| decimal(t) \|\| ":" \|\| oa_binding \|\| payload)` | Verified byte-for-byte against NIP-GS's own published test vectors |
| `do_sign` (`src/lib.rs`) | NIP-GS "Signing Procedure" steps 1-8 | Loads key, computes hash, signs with BIP-340 Schnorr, writes armored signature + `SIG_CREATED` status line |
| `build_envelope` (`src/lib.rs`) | NIP-GS canonical JSON envelope: fixed field order `v, pk, sig, t[, oa]`, no whitespace | Hand-built with `format!`, not serde, to guarantee byte-exact output |
| `armor` (`src/lib.rs`) | NIP-GS armor format: `-----BEGIN SIGNED MESSAGE-----\n<base64>\n-----END SIGNED MESSAGE-----\n` | |
| `do_verify` / `parse_envelope` / `parse_armor` (`src/lib.rs`) | NIP-GS "Verification Procedure" steps 1-11, including the canonical-reconstruction non-malleability check | Rejects wrong payload, tampered signature, non-canonical JSON, malformed/unknown envelope fields, oversized inputs |
| `load_auth_tag` / `verify_oa` / `enforce_conditions` (`src/lib.rs`) | NIP-GS "Owner Attestation" (optional `oa` field): structural validation, self-attestation rejection, NIP-OA preimage signature verification, `created_at</>` condition enforcement | Consumes the NIP-OA `auth` tag format from `BUZZ_AUTH_TAG` env var or `nostr.authtag` git config |
| `determine_trust` (`src/lib.rs`) | NIP-GS trust determination: `TRUST_FULLY` iff verified `pk` matches `user.signingkey`, else `TRUST_UNDEFINED` | Advisory only, per both this crate's module doc and NIP-GS's own Security Considerations |
| `StatusWriter` and the `[GNUPG:]`-prefixed status lines throughout `do_sign`/`do_verify` | NIP-GS "Status Line Formats": `SIG_CREATED`, `GOODSIG`, `BADSIG`, `VALIDSIG`, `ERRSIG`, `TRUST_*`, plus `NOTATION_NAME`/`NOTATION_DATA` for OA status | Falls back to stderr when `--status-fd` is absent or unusable, per NIP-GS |
| `KeypairGuard`, `Zeroizing<String>` usage, explicit `ptr::write_bytes` in `do_sign` | NIP-GS "the program MUST zeroize secret key material from memory after use" | Module doc discloses a known residual-copy limitation from `secp256k1::SecretKey` lacking `Zeroize` upstream |

## Divergences

No behavioral divergence from NIP-GS's normative (MUST-level) requirements
was found while reading `src/lib.rs` against the spec's Specification,
Signing Procedure, Verification Procedure, Key Loading, and Owner
Attestation sections in full. Two additions beyond what NIP-GS itself
requires were found and are recorded here as strengthenings, not gaps:

- **Keyfile ownership check.** NIP-GS requires only that keyfile
  permissions be no broader than 0600; `open_keyfile` additionally requires
  the file be owned by the process's current UID, which NIP-GS does not
  mandate.
- **Trust-model disclosure.** NIP-GS's Security Considerations already
  describes `TRUST_FULLY` as advisory-only; this crate goes further by
  emitting an explicit `NOTATION_DATA advisory-config-match-only` status
  line so a caller can detect the advisory nature machine-readably, not
  only by reading documentation.

One NIP-GS SHOULD-level (non-normative) behavior was not verified: whether
`kind=` conditions in an owner-attestation tag are silently ignored
end-to-end exactly as NIP-GS's "Conditions in Git Context" section
recommends, versus this crate's `has_kind_clause` check, which emits a
`stderr` warning rather than silently ignoring — both are spec-compliant
(NIP-GS says SHOULD ignore, not MUST), but this is a stricter-than-required
choice rather than a verified match, and is named in *Scope and omissions*
below rather than asserted as a checked equivalence.

## Verification

The crate's own `#[cfg(test)] mod tests` block in `src/lib.rs` (roughly 50
`#[test]` functions) is the only automated verification found for this
crate. It is exercised by a plain `cargo test -p git-sign-nostr` (no special
infrastructure required — no live relay, no Postgres/Redis, no `#[ignore]`
gates were found in this module, unlike the `#[ignore]`-gated e2e coverage
`architecture-flows-git-push` documents for the surrounding push-transport
flow). Representative tests: `test_signing_hash_matches_spec` and
`test_signing_hash_with_oa_matches_spec` reproduce NIP-GS's own published
hash test vectors exactly; `test_sign_verify_round_trip` exercises a full
sign-then-verify cycle; `test_verify_rejects_wrong_payload`,
`test_verify_rejects_tampered_sig`, and `test_verify_rejects_non_canonical_json`
cover the negative/malleability paths; the `test_envelope_rejects_*` and
`test_armor_rejects_*` families cover malformed-input handling field by
field. No test in this suite, and no reference to this crate anywhere under
`crates/buzz-test-client/` or `crates/buzz-relay/`, exercises this program
as git actually invokes it (as a real `gpg.x509.program` subprocess against
a live `git commit`/`git verify-commit`) — see *Scope and omissions*.

## Relationships

- references: architecture-flows-git-push — that merged node documents the
  git-push transport flow and already records, as one of its own evidence
  entries, the exact boundary this node restates: NIP-98 push-transport
  auth versus NIP-GS object signing are independent, orthogonal concerns.

No `implements` edge is declared. `docs/nips/NIP-GS.md` — the spec this
crate realizes — has no corpus node id at this node's recorded revision;
see *Target* above and the evidence ledger's final entry for how that was
checked.

## Scope and omissions

**This node covers** what `git-sign-nostr` is responsible for (signing and
verifying git commit/tag objects locally against NIP-GS, as a
`gpg.x509.program` subprocess git invokes), its public entry points
(the sign and verify CLI invocations, both consumed only by git itself —
this crate exposes no library API intended for other crates to call; its
`[lib]` target exists solely so the binary and its test module share code),
its important dependencies (`nostr` for key parsing/Schnorr signing,
`zeroize` for secret erasure, `libc` for Unix fd handling, `chrono` for
status-line date formatting, `base64`/`serde_json` for the envelope), and a
section-by-section mapping of its code to the NIP-GS requirements it
realizes.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| NIP-98 HTTP push-transport authentication (`git-credential-nostr`) | A separate implementation-reference node for `git-credential-nostr`, documented by a different issue in this same batch |
| The `git push` HTTP transport, policy callback, and object-store CAS publish flow | `architecture-flows-git-push` (merged) |
| NIP-OA's own attestation-issuance side (how an `auth` tag is produced in the first place) | `docs/nips/NIP-OA.md` itself, and whatever future corpus node documents its issuing implementation |
| Whether promoting `docs/nips/NIP-GS.md` to its own corpus node is warranted, and adding the resulting `implements` edge back to this node | Unresolved; not filed as its own task here — an author hitting this gap should check for an existing issue before filing a new one |

**Expected but not verified when this node was written:**

- **The crate was not built or run.** No `cargo test -p git-sign-nostr` was
  executed in this session; every claim about test behavior and coverage
  above is sourced from reading the test source directly, not from a
  passing run.
- **No real `git commit`/`git verify-commit` round trip against a
  configured `gpg.x509.program` was exercised.** The unit-test suite
  exercises the crate's internal sign/verify functions directly, not the
  full external-process invocation contract (argument parsing from a real
  git subprocess call, actual fd inheritance for `--status-fd`, git's own
  parsing of the emitted status lines). Whether git's real invocation
  matches what `parse_args` and `StatusWriter` assume was read, not
  executed.
- **Whether `has_kind_clause`'s stderr warning for `kind=` conditions is
  the intended behavior** versus NIP-GS's SHOULD-level silent-ignore
  recommendation was not resolved — both are spec-compliant, and this is
  named as an open, unverified equivalence in *Divergences* above rather
  than asserted as checked.
