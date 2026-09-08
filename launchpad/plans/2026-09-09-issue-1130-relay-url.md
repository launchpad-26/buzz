# Plan — issue #1130: document the relay URL (corpus node)

**Issue:** launchpad-26/buzz#1130 (parent Feature #609)
**Target:** `launchpad/docs/corpus/layers/networking/relay-url.md`
**Node id:** `layers-networking-relay-url`
**Template:** `launchpad/docs/corpus/templates/concept.md`
**Worktree revision:** `29ca9b189bd3f639ba09c972b57c70538c0860c6` (`origin/launchpad`)

## Scope

One concept node: *the relay URL* — the string identifying a relay to itself and to
its clients, where it is configured, what part of it the relay actually reads, and
how NIP-42 uses it as an anti-relay-substitution check.

Explicitly **not** in scope (owned elsewhere, link only):

| Subject | Owner |
|---|---|
| The NIP-42 handshake sequence and its error mapping | `architecture-flows-websocket-authentication` |
| NIP-42's verification obligations and test coverage | `verification-security-authentication` |
| The `RELAY_URL` row in the relay's environment-variable table | `layers-configuration-relay-configuration` |
| Multi-tenant host resolution as a subject in its own right | `verification-formal-multi-tenant-auth` |

## Steps

1. **Trace the comparison.** Read `crates/buzz-auth/src/nip42.rs` end to end and
   record the exact normalization `normalize_relay_url` applies, its parse-failure
   fallback, and which of its branches its own unit tests cover.
   *Done when:* the rule can be stated without hedging, and the untested branch is named.

2. **Trace what the relay compares against.** Read
   `crates/buzz-relay/src/handlers/auth.rs`, `nip42_expected_relay_url` and
   `nip98_expected_url` in `crates/buzz-relay/src/api/bridge.rs`, and their tests.
   *Done when:* it is established which component of `config.relay_url` reaches the
   comparison and which component comes from the connection's tenant.

3. **Trace configuration and the client side.** Read `RELAY_URL` parsing in
   `crates/buzz-relay/src/config.rs`, the two `.env.example` entries, the startup
   use in `crates/buzz-relay/src/main.rs`, `relay_url_authority`/`normalize_host` in
   `crates/buzz-core/src/tenant.rs`, and the client's tag construction in
   `crates/buzz-ws-client/src/connection.rs` and `message.rs`.
   *Done when:* the divergence between the two host-normalization rules is stated
   from both function bodies, not assumed.

4. **Draft the node** against `templates/concept.md`'s required sections, with
   `type: layers`, `status: draft`, `origin: launchpad`, one commit-only provenance
   FACT, and `relationships` targeting only ids present on `origin/launchpad`
   (verified against `git ls-tree`, not the local tree).
   *Done when:* every FACT cites a file that was opened and says what the statement
   claims, and *Scope and omissions* carries both the boundary table and the
   could-not-verify disclosure.

5. **Validate, stamp, commit.** `python3 launchpad/project-intelligence/corpus/validate.py`
   exits 0; the corpus test suite runs to `OK` in the foreground; commit with `-s`.
   *Done when:* validator exit 0 and one signed commit exists on
   `task/1130-relay-url`. No push, no PR.

## Risks

- **Restating a boundary node.** `architecture-flows-websocket-authentication`
  already states the localhost/trailing-slash normalization. Mitigation: this node's
  centre of gravity is the *URL* — where it comes from, which part is read, and the
  divergence between the two normalizers — not the handshake.
- **Claiming behaviour that was not executed.** No Rust build is run here.
  Mitigation: behavioural claims that rest on a dependency's semantics rather than
  on code read in this repository are INFERENCE or land in the could-not-verify list.
