# Plan — issue #1166: corpus node for the event signature

**Issue:** launchpad-26/buzz#1166 (Feature #609, protocol layer corpus)
**Target:** `launchpad/docs/corpus/layers/protocol/signature.md`
**Node id:** `layers-protocol-signature`
**Template:** `launchpad/docs/corpus/templates/concept.md`
**Worktree:** `__worktrees/task-1166-signature`, branch `task/1166-signature`
**Provenance revision:** `29ca9b189bd3f639ba09c972b57c70538c0860c6` (confirmed with `git cat-file -e`)

## Subject

The `sig` field: a BIP-340 Schnorr signature over the 32-byte event-id digest, under the
x-only key in the event's own `pubkey` field. One concept — what the signature is, what
message it commits to, what it proves, and what it does not.

## Boundaries held (read, link, do not restate)

| Owned elsewhere | Node |
|---|---|
| The accept/reject invariant, its enforcement points, its failure messages | `architecture-principles-signed-events` (merged) |
| Auth-path testing and NIP-42 security verification | `verification-security-authentication` (merged) |
| Signing git objects with a Nostr key | `implementation-crates-git-sign-nostr` (merged) |
| The event id digest itself | issue #1152 (sibling, unmerged — must not be targeted) |
| The event as a whole | issue #1156 (sibling, unmerged — must not be targeted) |

## Steps

1. **Evidence pass.** Open and read `crates/buzz-core/src/verification.rs`,
   `crates/buzz-core/src/error.rs`, `crates/buzz-pair-relay/src/lib.rs`
   (`verify_event_sig` and its one call site), `crates/buzz-relay/src/handlers/ingest.rs`
   (the `spawn_blocking` call site), `crates/buzz-auth/src/nip42.rs`, `Cargo.toml` (the
   `nostr` pin), and `crates/git-sign-nostr/src/lib.rs` (boundary only).
   *Done when:* every claim I intend to write has a file I actually opened, and the
   absences (no vendored `nostr` source, no test for `verify_event_sig`) are established
   by commands I ran.

2. **Relationship targets.** Grep the merged-id list for each candidate and keep only ids
   that appear there. No sibling from Feature #609.
   *Done when:* every `relationships[].target` is present in
   `scratchpad/corpus-merged-ids.txt`.

3. **Draft the node.** Front matter per `node.schema.json` — seven permitted fields,
   `type: layers`, `status: draft`, `origin: launchpad`. Body follows the concept
   template's required sections: definition first, boundary, use cases, scope and
   omissions carrying both a what-is-not-covered table and a separate expected-but-not-
   verified list.
   *Done when:* the file exists and every substantive body claim maps to one ledger entry.

4. **Validate.** `python3 launchpad/project-intelligence/corpus/validate.py`.
   *Done when:* exit status 0.

5. **Self-review, then stamp and commit.** Re-check every ledger entry against its source
   and every DoD bullet of #1166 *before* the stamp run, because editing after the stamp
   clears it. Then run the corpus test suite as the sole foreground command, confirm the
   final line is `OK`, and `git commit -s`. No push, no PR.
   *Done when:* the suite ends `OK` and one signed commit exists on the branch.
