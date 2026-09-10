---
id: interfaces-nostr-buzz-nips-nip-gs
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "NIP-GS (Git Object Signing with Nostr Keys) defines a detached signature format and verification protocol for signing git commits and tags with Nostr secp256k1 keys, invoked through git's pluggable gpg.x509.program signing-program interface, and is marked draft/optional."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-GS.md:1-13"
  - statement: "The signature envelope is a base64-encoded, compact-serialized JSON object with required fields v (must be 1), pk (64 lowercase hex, a valid BIP-340 x-only pubkey), sig (128 lowercase hex, a BIP-340 Schnorr signature) and t (unix timestamp, integer 0-4294967295), plus an optional oa field (a 3-element NIP-OA owner-attestation array), wrapped in an armor of exactly three lines: `-----BEGIN SIGNED MESSAGE-----`, the base64 line, `-----END SIGNED MESSAGE-----`."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-GS.md:79-151"
  - statement: "The signing hash is SHA-256 of the domain-separated preimage `\"nostr:git:v1:\" || decimal(t) || \":\" || oa_binding || payload_bytes`, where oa_binding is `oa[0] || \":\" || oa[1] || \":\" || oa[2] || \":\"` when oa is present and empty otherwise, so all envelope metadata is cryptographically bound to the signature."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-GS.md:153-184"
  - statement: "crates/git-sign-nostr/src/lib.rs's compute_signing_hash function implements exactly this preimage construction: it feeds the domain separator, the decimal timestamp, a colon, the optional oa_binding (owner pubkey, conditions, owner signature, each followed by a colon) and finally the payload bytes into a SHA-256 engine."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:895-916"
  - statement: "crates/git-sign-nostr/src/lib.rs's own test suite pins compute_signing_hash's output against NIP-GS.md's published test vectors: test_signing_hash_matches_spec asserts the no-oa hash for the spec's 170-byte test payload and t=1700000000 equals a11a32173aa35125aaefaad8854f2eda5a144268a4a355905c841f79ff44aa18, and test_signing_hash_with_oa_matches_spec asserts the with-oa hash (using the spec's owner pubkey, empty conditions, and owner signature) equals b61f1658836a4f63a2d2f5d621014a064435dde0765dd9c1dc79c9530fe879f0 -- both exact values also published in docs/nips/NIP-GS.md's Test Vectors section."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:1808-1827"
      - "docs/nips/NIP-GS.md:558-670"
  - statement: "crates/git-sign-nostr/src/lib.rs's build_envelope function constructs the canonical JSON by hand with format! (field order v, pk, sig, t, then oa if present, no whitespace) rather than via serde, with a comment explaining this is deliberate because serde's own serialization order is not guaranteed to match the byte-exact canonical form NIP-GS's verification step requires."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:918-935"
  - statement: "NIP-GS's verification procedure requires the verifier to reconstruct the canonical JSON string from the parsed field values and reject (ERRSIG, exit 1) if it does not match the base64-decoded string byte-for-byte, preventing envelope malleability such as inserted whitespace."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-GS.md:227-241"
  - statement: "crates/git-sign-nostr/src/lib.rs's test_verify_rejects_non_canonical_json constructs a syntactically valid, cryptographically correctly-signed envelope with one added space after the opening JSON brace and asserts that the verify path (verify_sig) returns an error, confirming the malleability rejection NIP-GS.md requires is actually enforced in code rather than only specified."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:2091-2115"
  - statement: "crates/git-sign-nostr/src/lib.rs implements the sign path as do_sign(key_id, status) and the verify path as do_verify(sig_file, status), each returning Result<(), Error>, dispatched from parse_args's two-armed Mode enum (Mode::Sign{key_id} from -bsau <key>, Mode::Verify{sig_file} from --verify <file> -), matching the CLI Interface section's two argument patterns."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:184-282"
      - "crates/git-sign-nostr/src/lib.rs:943"
      - "crates/git-sign-nostr/src/lib.rs:1099"
      - "docs/nips/NIP-GS.md:505-522"
  - statement: "parse_args silently ignores any argument it does not recognize (a bare comment states this is deliberate, citing the NIP-GS spec's forward-compatibility requirement), and rejects conflicting or missing mode arguments (both -bsau and --verify given, neither given, or --verify given without the trailing stdin `-` marker) as a fatal parse error before any signing or verification is attempted."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:196-282"
  - statement: "run() maps every error path -- both Error::Fatal (parse failure, I/O failure, missing key) and Error::VerifyFailed (cryptographic verification failure) -- to process exit code 1, and returns 0 only when do_sign or do_verify complete without error, so the program's exit-code contract is exactly 0 (success) or 1 (any failure), with no other exit code produced anywhere in run()."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:1726-1783"
  - statement: "load_key checks NOSTR_PRIVATE_KEY, then BUZZ_PRIVATE_KEY, then the git config key nostr.keyfile, in that order, trims and validates each candidate against a 128-byte size cap, and removes the environment variable from the process's own environment immediately after reading it to shrink the exposure window; this matches NIP-GS.md's Key Loading section's stated precedence exactly."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:392-436"
      - "docs/nips/NIP-GS.md:335-346"
  - statement: "load_auth_tag loads the optional NIP-OA owner-attestation tag from BUZZ_AUTH_TAG (a JSON array of 4 strings, using elements 1-3) or the git config key nostr.authtag, matching NIP-GS.md's Loading the Auth Tag section; if neither source is set the oa field is omitted from the envelope, which NIP-GS.md states is not an error."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:463-561"
      - "docs/nips/NIP-GS.md:466-477"
  - statement: "verify_oa implements the NIP-OA attestation check inside NIP-GS verification: it parses the owner pubkey as a BIP-340 key, computes SHA-256 of the preimage `\"nostr:agent-auth:\" || agent_pk || \":\" || conditions`, and verifies the owner signature over that hash against the owner pubkey with secp256k1 Schnorr verification, returning false (logged as a warning, not a hard verification failure of the commit signature itself) on any parse or cryptographic failure."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:1500-1546"
  - statement: "NIP-GS.md states that if the oa owner signature fails NIP-OA verification, the underlying NIP-GS commit signature (sig) may still be valid, and verifiers SHOULD report the commit as signed but the owner authorization as failed/unverified -- i.e. the two verification outcomes are reported as distinct facts, not folded into one pass/fail result."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-GS.md:424-426"
      - "docs/nips/NIP-GS.md:446-453"
  - statement: "determine_trust reports TRUST_FULLY only when git config user.signingkey is set and its normalized hex value equals the verified signature's pk field (case-insensitively), and TRUST_UNDEFINED otherwise, matching NIP-GS.md's stated trust-level rule and its explicit caveat that TRUST_FULLY means only \"this is the locally configured signing key,\" not a global trust assertion."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:1673-1682"
      - "docs/nips/NIP-GS.md:261-273"
  - statement: "crates/git-sign-nostr/README.md documents the git configuration needed to enable NIP-GS signing (gpg.format x509, gpg.x509.program pointing at the built binary, commit.gpgsign/tag.gpgsign true, user.signingkey set to the hex pubkey) and the two invocation shapes git uses to call the program, both consistent with NIP-GS.md's Git Configuration and CLI Interface sections and with parse_args's actual argument handling."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/README.md:1-46"
  - statement: "NIP-GS.md's Invalid Cases section enumerates the malformed-envelope and validation-failure conditions a conforming implementation MUST reject (bad armor, undecodable base64, non-object JSON, duplicate JSON keys, wrong or missing v, unknown JSON keys, malformed oa, self-attesting oa, invalid pk/sig/t shape, oversized JSON, oversized payload, unavailable secret key, mismatched -u <key> argument), each producing ERRSIG and exit code 1 except the two payload/secret-key cases, which fail before any signature is produced."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-GS.md:692-721"
  - statement: "crates/git-sign-nostr/src/lib.rs's test suite exercises several of NIP-GS.md's Invalid Cases directly: test_verify_rejects_wrong_payload, test_verify_rejects_tampered_sig, test_verify_rejects_non_canonical_json, test_parse_envelope_rejects_invalid_oa_pubkey and test_parse_envelope_rejects_self_attestation each assert that the corresponding malformed or tampered input is rejected rather than accepted."
    entry_class: FACT
    evidence:
      - "crates/git-sign-nostr/src/lib.rs:2066-2160"
  - statement: "NIP-GS.md's Relationship to Other NIPs table states that NIP-98 authenticates the pusher over HTTP transport while NIP-GS authenticates the committer of a git object, and that they are complementary rather than overlapping; it also states NIP-OA's oa field embeds a NIP-OA credential in the signature envelope and, with empty conditions, is pure key-to-key identity binding."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-GS.md:839-847"
  - statement: "NIP-GS does not define any Nostr event kind and involves no relay: the signature envelope is embedded directly in a git commit or tag object and never published to a Nostr relay, unlike NIP-01/NIP-29 events."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-GS.md:849-861"
  - statement: "The sibling corpus node interfaces-nostr-buzz-nips-nip-er (file nip-er.md, documenting a different NIP) exists only on the unmerged branch task/997-interfaces-nostr-buzz-nips-nip-gs at the time this node was drafted, and is therefore not a resolvable relationships target on origin/launchpad; this node mentions it by filename in prose only, per this task's own dispatch instructions."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#998 dispatch instructions"
---

# NIP-GS (Git Object Signing with Nostr Keys): interface

This node documents **NIP-GS**, a Buzz-originated custom Nostr Improvement
Proposal that is not a wire protocol between a Buzz client and the relay, but a
**local signing-program interface** between `git` and an external program: git
invokes the program as its configured `gpg.x509.program` to sign or verify a
detached signature over a git commit or tag object, using a Nostr secp256k1
keypair (BIP-340 Schnorr) instead of GPG, SSH, or an x509 certificate authority.
The signature envelope travels inside the git object itself (its `gpgsig`
header) — it is never sent to, or seen by, a Buzz relay. The specification is
`docs/nips/NIP-GS.md`; the reference implementation of both sides (signing
program and verification program, the same binary in different modes) is
`crates/git-sign-nostr`.

Buzz's primary product API is Nostr events over WebSocket (see
`interfaces-nostr-buzz-nips-nip-er`'s neighboring subject matter and this
repository's own `AGENTS.md`), and NIP-GS is deliberately outside that surface:
it defines no event kind, and the relay plays no part in it.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Sign | `crates/git-sign-nostr/src/lib.rs` `do_sign` (invoked via `-bsau <key>` per NIP-GS.md's CLI Interface section) | Reads the git object payload from stdin, computes the signing hash, produces a BIP-340 Schnorr signature, writes the armored envelope to stdout, and writes `SIG_CREATED` to the status fd. |
| Verify | `crates/git-sign-nostr/src/lib.rs` `do_verify` (invoked via `--verify <file> -` per NIP-GS.md's CLI Interface section) | Reads the git object payload from stdin, parses and validates the signature file's envelope, recomputes the signing hash, verifies the Schnorr signature, optionally verifies the NIP-OA `oa` attestation, and writes `GOODSIG`/`BADSIG`/`ERRSIG` plus trust-level status lines. |
| Key loading | `crates/git-sign-nostr/src/lib.rs` `load_key` | Checked in order: `NOSTR_PRIVATE_KEY` env var, `BUZZ_PRIVATE_KEY` env var, `nostr.keyfile` git config path. Accepts hex or NIP-19 `nsec1...`. |
| Owner-attestation loading | `crates/git-sign-nostr/src/lib.rs` `load_auth_tag` | Checked in order: `BUZZ_AUTH_TAG` env var (JSON array of 4 strings), `nostr.authtag` git config. Absent is not an error — the `oa` envelope field is simply omitted. |
| Owner-attestation verification | `crates/git-sign-nostr/src/lib.rs` `verify_oa` | Verifies the NIP-OA Schnorr signature at `oa[2]` over `SHA-256("nostr:agent-auth:" \|\| pk \|\| ":" \|\| conditions)` against the owner pubkey at `oa[0]`, per `docs/nips/NIP-GS.md`'s Owner Attestation section. |
| Trust determination | `crates/git-sign-nostr/src/lib.rs` `determine_trust` | Compares the verified `pk` against git's own `user.signingkey` config to decide `TRUST_FULLY` vs `TRUST_UNDEFINED`. |

## Contract and stability

**Versioning.** The envelope carries an explicit schema version field, `v`,
which MUST be the integer `1` for this version of the protocol; any other
value is rejected (`ERRSIG`, exit 1). `docs/nips/NIP-GS.md` reserves later
values (`v=2`, etc.) for future field sets, and states that for `v=1`, `v`,
`pk`, `sig`, `t` and `oa` are the *only* permitted keys — an unrecognized key
is rejected rather than silently ignored, so the envelope cannot be silently
extended without a version bump.

**Error and rejection behavior.** Every invalid-input condition NIP-GS.md's
Invalid Cases section enumerates resolves to one of two observable outcomes,
both implemented in `crates/git-sign-nostr/src/lib.rs`'s `run()`: process exit
code `1` (the only non-zero exit code the program produces) plus, for
verification failures specifically, a `[GNUPG:] ERRSIG` or `[GNUPG:] BADSIG`
status line git's own signature-verification code parses. Exit code `0` is
produced only when `do_sign`/`do_verify` complete without error. A secret-key
load failure or an oversized payload during signing MUST NOT write anything to
stdout, because git treats any stdout content as signature data.

**Ordering / idempotency.** Signing is not idempotent by construction: each
invocation records the current wall-clock timestamp as `t`, and (unless a
deterministic nonce scheme is used) a fresh BIP-340 nonce, so re-signing the
same payload twice produces two different — but both individually valid —
signatures. There is no ordering guarantee or sequence number in the protocol;
a signed git object's validity does not depend on any other signed object.
`docs/nips/NIP-GS.md`'s Security Considerations explicitly notes a signed
object "is valid wherever it appears" (replay across repositories is
intentional, matching GPG-signed-commit behavior), which is the ordering
posture callers should rely on: *content-addressed validity*, not sequence.

**Authentication / authorization.** The interface authenticates *who signed*
(the `pk` field, a Nostr secp256k1 identity) via BIP-340 Schnorr signature
verification over a domain-separated hash (`"nostr:git:v1:"` prefix), never
via a bearer credential or session. Authorization of an *agent acting on
behalf of an owner* is a separate, optional layer: the `oa` field embeds a
NIP-OA attestation proving a human owner authorized the signing key, verified
independently of the commit signature itself (`verify_oa`). A verified `sig`
and a verified `oa` are reported as two distinct facts — "signed by `<pk>`"
and "authorized by `<owner-pubkey>`" — never conflated into one boolean, per
`docs/nips/NIP-GS.md`'s Trust Display guidance and the "signature may still be
valid, owner attestation may not" case in Invalid Cases.

## Boundary

This node does not describe:
- **NIP-OA's own attestation contract** (what a NIP-OA `auth` tag means, how it
  is issued, and its conditions grammar) beyond the one field NIP-GS embeds and
  re-verifies (`oa`) — NIP-OA's own specification is the authority for that,
  and this node cites it only where NIP-GS's envelope depends on it.
- **NIP-01/NIP-29's own event-signing contract**, which uses the same
  secp256k1 keys but a different hash preimage (domain separation) and is the
  wire format for Buzz's actual Nostr-over-WebSocket product surface; NIP-GS
  signs git objects, never Nostr events, and defines no event kind.
- **A field-by-field, parameter-by-parameter reference catalogue** of every
  status-line format byte layout — those exact formats are fully specified in
  `docs/nips/NIP-GS.md`'s Status Line Formats subsection and are cited here,
  not re-derived.
- **`crates/git-credential-nostr`**, a separate crate handling git's HTTP
  credential-helper interface (authenticating the *pusher* over transport),
  which this node did not inspect; NIP-GS.md's own Relationship to Other NIPs
  table names NIP-98 (not NIP-GS) as that surface's authenticator and states
  NIP-98 and NIP-GS are complementary, not overlapping.

## Valid example

Using the spec's deterministic test vector (secret key `0x...03`, no auxiliary
randomness): signing the 170-byte test git-commit payload at `t=1700000000`
produces signing hash
`a11a32173aa35125aaefaad8854f2eda5a144268a4a355905c841f79ff44aa18` and the
armored envelope:

```
-----BEGIN SIGNED MESSAGE-----
eyJ2IjoxLCJwayI6ImY5MzA4YTAxOTI1OGMzMTA0OTM0NGY4NWY4OWQ1MjI5YjUzMWM4NDU4MzZmOTliMDg2MDFmMTEzYmNlMDM2ZjkiLCJzaWciOiJjMzUwNjIxNDhkOTViODIwMDY4YzE4YWI5Y2Y2OWE4ZGQyMzIyYzYwNjg5MDM2NmQwODRkZjc2MTc1NzBiOTZiN2ExYWNhMGE4ZmNhYmIyZWI0MDMyZWJiZGY1YjQzZTZiZjg2MzNlMGQ4NWJjZWNjZTI4YTllMDg3MDViODc1ZiIsInQiOjE3MDAwMDAwMDB9
-----END SIGNED MESSAGE-----
```

decoding to `{"v":1,"pk":"f9308a...36f9","sig":"c35062...b875f","t":1700000000}`.
`crates/git-sign-nostr/src/lib.rs`'s `test_signing_hash_matches_spec` pins the
hash value above against this exact vector.

## Failure example

`crates/git-sign-nostr/src/lib.rs`'s `test_verify_rejects_non_canonical_json`
takes the same valid, correctly-signed envelope above and inserts a single
space after the opening JSON brace (`{ "v":1,...` instead of `{"v":1,...`)
before base64-encoding and armoring it. The signature bytes are still
cryptographically valid over the original hash, but verification rejects the
envelope anyway: `docs/nips/NIP-GS.md`'s canonical-JSON-reconstruction rule
requires the base64-decoded bytes to exactly match the JSON the verifier
reconstructs from the parsed field values (compact, no whitespace, fixed field
order), and the space breaks that byte-for-byte match — the same
envelope-malleability defense that stops an attacker from re-signing-looking
whitespace injection.

## Scope and omissions

**This node covers** NIP-GS's signature envelope shape, the signing/verifying
operations and their status-line and exit-code contract, key and
owner-attestation loading order, the authentication/authorization split
between the commit signature and the optional NIP-OA attestation, and one
valid and one failure example, each grounded in both the specification text
and the `crates/git-sign-nostr` implementation and its own test suite.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| NIP-OA's own attestation/conditions contract | NIP-OA's specification (`docs/nips/NIP-OA.md`, not opened for this node beyond the fields NIP-GS embeds) |
| `crates/git-credential-nostr`'s HTTP credential-helper interface | Not inspected for this node; NIP-GS.md names NIP-98 as that surface's authenticator |
| Per-type corpus standards for `interfaces-events` nodes | Unlanded per `launchpad/docs/corpus/AGENTS.md`'s own gap table (somewhere in #1307-#1351) |

**Expected but not verified when this node was written:**
- **No live end-to-end test was run** (configuring real git config, invoking
  `git commit -S` against a built `git-sign-nostr` binary, and running `git
  verify-commit`) — every claim above is grounded in the specification text
  and in the crate's own unit tests, not in an observed live git invocation.
- **`docs/nips/NIP-OA.md` and `crates/git-credential-nostr` were not opened**
  for this node; the two Boundary bullets naming them rest on what
  `docs/nips/NIP-GS.md`'s own text says about each, not on independently
  reading either.
- **No `relationships` edges are declared.** `launchpad/docs/corpus/interfaces/`
  does not exist on `origin/launchpad` at the recorded revision, and the one
  candidate sibling, `interfaces-nostr-buzz-nips-nip-er`, exists only on an
  unmerged branch — so no target resolves. This is the same situation the
  corpus's own `AGENTS.md` describes for its first node, and the same
  resolution: declare none now, and add the edge once a sibling merges.
