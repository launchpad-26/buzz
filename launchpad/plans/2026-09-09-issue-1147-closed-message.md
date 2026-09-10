Issue #1147 (Feature #609) — document the relay→client `CLOSED` message as a corpus concept node
Stated size: no `Size` line on the issue (corpus-plan `type:task` template carries none) -> cap: 5 steps,
set by the batch brief for Feature #609 rather than by the issue.

ALREADY TRUE  (verified against the real repository, not notes)
  Worktree `/home/serina/Launchpad/buzz/__worktrees/task-1147-closed-message`, branch
  `task/1147-closed-message`, created from `origin/launchpad` at
  `29ca9b189bd3f639ba09c972b57c70538c0860c6` (`git rev-parse HEAD` inside the worktree;
  `git cat-file -e` on that sha exits 0).
  `launchpad/docs/corpus/layers/protocol/closed-message.md` does not exist. No node under
  `launchpad/docs/corpus/layers/protocol/` or `layers/networking/` is merged on
  `origin/launchpad` — the whole Feature #609 surface is new, so there is no sibling in
  this Feature that may legally be a `relationships` target.
  `crates/buzz-relay/src/protocol.rs` defines `RelayMessage::closed(sub_id, message)`,
  which serialises `["CLOSED", sub_id, message]`. Every emit site in the tree was
  enumerated with `grep -rn "RelayMessage::closed(" crates/`: `handlers/req.rs` (11),
  `handlers/count.rs` (13), `handlers/close.rs` (1), `handlers/side_effects.rs` (1),
  `connection.rs` (1, via `request_rejection_message`). Each was read.
  The literal reason strings across those sites use exactly four prefixes —
  `auth-required:`, `restricted:`, `error:`, `rate-limited:` — plus the empty string,
  which `handlers/close.rs` sends as the acknowledgement of a client `CLOSE`.
  `crates/buzz-ws-client/src/message.rs` parses `"CLOSED"` into
  `RelayMessage::Closed { subscription_id, message }`, defaulting `message` to `""`.
  `desktop/src/shared/api/relayClosedPolicy.ts` classifies a received CLOSED three ways
  (`retryable` / `rate-limited` / `terminal`) by reason prefix, with
  `relayClosedRecovery.ts` and `relayRateLimitGate.ts` acting on the classification and
  `relayClosedPolicy.test.mjs` covering it.
  `launchpad/docs/corpus/architecture/flows/websocket-authentication.md` (id
  `architecture-flows-websocket-authentication`) is merged and already documents the
  NIP-42 handshake, including the `auth-required:` rejection — so this node links to it
  and must not restate the handshake.
  `verification-contracts-websocket` already records the frame inventory and the
  `handle_close` / `handle_req` auth behaviour at contract level; this node must not
  duplicate that either.
  No `NIP-01.md` exists in this repository — `docs/nips/` holds only Buzz's own
  two-letter NIPs — so the standard's own prefix convention cannot be a `FACT` on a
  repo path.

STEP 1 — Confirm the target set for `relationships`
  Grep the merged-id list for every id this node intends to reference and confirm each
  appears there.
  done-when: `architecture-flows-websocket-authentication`,
  `architecture-flows-websocket-connection`, `implementation-crates-buzz-relay`,
  `implementation-crates-buzz-ws-client`, `implementation-crates-buzz-pair-relay`,
  `verification-contracts-websocket` and `verification-e2e-relay` each appear in
  `corpus-merged-ids.txt`, and no Feature #609 sibling is on the list.

STEP 2 — Write the node's front matter
  `type: layers`, `status: draft`, `origin: launchpad`, `id: layers-protocol-closed-message`,
  audiences `agent` + `developer`. Evidence ledger: exactly one commit-only FACT (the
  provenance entry at `29ca9b18…`); one FACT per source actually opened; INFERENCE for the
  claim that the desktop's terminal-prefix list is deliberately wider than the relay's
  emitted set; TEAM_KNOWLEDGE (`provided_by` naming NIP-01) for the standard's convention,
  since the spec text is not in this repository.
  done-when: no evidence entry cites a file this session did not open, and no second
  commit-only FACT exists.

STEP 3 — Write the body against `templates/concept.md`
  Definition (with the explicit `CLOSE` vs `CLOSED` vs WebSocket close-frame
  disambiguation the template requires), Background, Use cases, Comparison table of the
  reason prefixes, Related resources, Scope and omissions.
  done-when: every required section from the template's *Required sections* list is
  present, `Scope and omissions` carries both the not-covered-and-who-owns-it half and
  the expected-but-could-not-verify half, and no sibling node's canonical content is
  restated.

STEP 4 — Validate
  `python3 launchpad/project-intelligence/corpus/validate.py`
  done-when: exit 0, no schema violation, no unresolvable relationship target.

STEP 5 — Self-review, stamp, commit
  Re-read each evidence entry against its cited source; check every DoD bullet on #1147.
  Then run the corpus test suite as a sole foreground command, confirm `OK`, and commit
  with `-s` in a separate call. No push, no PR.
  done-when: the suite's final line is `OK` and `git log -1` shows the signed-off commit.

NOT DOING
  Documenting `CLOSE` (client→relay) — that is sibling issue #1146.
  Documenting the WebSocket close frame — that is sibling issue #1122.
  Documenting `buzz-pair-relay`'s own CLOSED emission beyond naming it as a boundary.
  Any change to runtime behaviour, any second corpus document, any "while here" cleanup.
