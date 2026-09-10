# Plan — issue #1161: document the `OK` message

**Issue:** launchpad-26/buzz#1161 (Feature #609, protocol and networking layer corpus)
**Target:** `launchpad/docs/corpus/layers/protocol/ok-message.md`
**Node id:** `layers-protocol-ok-message`
**Template:** `launchpad/docs/corpus/templates/concept.md`
**Worktree:** `__worktrees/task-1161-ok-message` on `task/1161-ok-message`
**Provenance revision:** `29ca9b189bd3f639ba09c972b57c70538c0860c6` (`git rev-parse HEAD` in
this worktree; confirmed with `git cat-file -e`, exit 0)

## Subject

`["OK", <event_id>, <true|false>, <message>]` — the relay's per-event acceptance
verdict, and the machine-readable reason prefixes it carries. One concept: the
acknowledgement frame's contract. Not the ingest pipeline that decides the verdict
(owned by `architecture-flows-event-ingestion`), and not the other wire messages.

## Steps

1. **Evidence sweep — done before this plan was written.** Enumerated every
   `RelayMessage::ok(` call site in `crates/` (30 total; 28 outside the test module,
   2 inside `protocol.rs`'s `#[cfg(test)] mod tests`) and read each. Read
   `crates/buzz-relay/src/protocol.rs` (the constructor and its serialization),
   `crates/buzz-relay/src/handlers/event.rs`, `crates/buzz-relay/src/handlers/auth.rs`,
   `crates/buzz-relay/src/state.rs`, `crates/buzz-relay/src/handlers/ingest.rs`
   (`IngestResult`/`IngestError`), `crates/buzz-relay/src/handlers/command_executor.rs`,
   `crates/buzz-ws-client/src/message.rs` (the parser),
   `crates/buzz-cli/src/commands/mod.rs` and `mem.rs` (a consumer that reads the
   message on an accepted write), and `desktop/src/shared/api/relayClosedPolicy.ts`.
   *Done when:* the reason-prefix set is derived from the emit sites, not assumed.

2. **Write the plan** (this file). *Done when:* the file exists and states the
   subject, the boundary and the provenance revision.

3. **Draft the node** against `templates/concept.md`'s required sections, with
   `type: layers`, `id: layers-protocol-ok-message`, `status: draft`,
   `origin: launchpad`. Body must carry a definition-first opening, the two-part
   verdict (`accepted` flag + `message` string), the enumerated prefix vocabulary
   with emit sites, the accepted-but-non-empty-message cases, and a
   *Scope and omissions* section carrying both a boundary statement and an
   explicitly-labelled could-not-verify disclosure.
   *Done when:* every substantive claim in the body has an `evidence` entry whose
   citation is a file this agent opened.

4. **Relationships** — only ids confirmed present in the merged-id list:
   `architecture-flows-event-ingestion`, `implementation-crates-buzz-relay`,
   `implementation-crates-buzz-ws-client`,
   `architecture-flows-websocket-authentication`. No Feature #609 sibling.
   *Done when:* each target is grepped out of the merged-id list before it is written.

5. **Validate, self-review, stamp, commit.** Run
   `python3 launchpad/project-intelligence/corpus/validate.py` to exit 0; re-read
   every evidence entry against its cited source; then run the corpus test suite as a
   sole foreground command and `git commit -s`. No push, no PR.
   *Done when:* the validator exits 0 and the suite's final line is `OK`.

## Out of scope

- The ingest pipeline's decision logic — `architecture-flows-event-ingestion` owns it.
- `EVENT`, `NOTICE`, `CLOSED`, `EOSE`, `COUNT`, `AUTH` frames and the event id itself
  — separate unmerged Feature #609 tasks (#1154, #1160, #1147, #1152).
- Changing any runtime behaviour, including the two defects noted as follow-up
  candidates in the report.
