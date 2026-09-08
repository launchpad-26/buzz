# Plan — issue #1160: document the `NOTICE` message

**Issue:** launchpad-26/buzz#1160 (`type:task`, parent Feature #609)
**Target:** `launchpad/docs/corpus/layers/protocol/notice-message.md`
**Node id:** `layers-protocol-notice-message`
**Template:** `launchpad/docs/corpus/templates/concept.md`
**Base:** `origin/launchpad` @ `29ca9b189bd3f639ba09c972b57c70538c0860c6`
**Worktree:** `__worktrees/task-1160-notice-message` on `task/1160-notice-message`

## Subject

`["NOTICE", <message>]` — the relay→client human-readable message. Its defining
property is that it is the one relay response carrying **no correlation handle**:
`OK` names an event id, `CLOSED` names a subscription id, `NOTICE` names nothing,
so a client cannot tie it back to the frame that caused it.

## Size

Small — one new Markdown node, no code change, no generated output.

## Steps

1. **Evidence sweep (done before this plan was written).** Enumerate every
   `NOTICE` emission in `crates/`, read each site, read the client-side handling in
   `crates/buzz-ws-client/`, `crates/buzz-acp/`, `desktop/src/shared/api/`,
   `web/src/shared/lib/`. Record absences with real command results.
   *Done when:* the enumerated set is closed and each site has been opened.

2. **Write the front matter** against `launchpad/docs/corpus/schema/node.schema.json`:
   `type: layers`, `status: draft`, `origin: launchpad`, audiences `agent`/`developer`,
   one provenance FACT citing `29ca9b18…`, one ledger entry per substantive body claim,
   classes assigned per `AGENTS.md` (FACT only where a file was opened).
   *Done when:* every claim in the drafted body has a matching entry and no second
   commit-only FACT exists.

3. **Write the body** to `templates/concept.md`'s required sections — definition
   first, boundary, background, use cases, comparison against `OK`/`CLOSED`, and a
   `Scope and omissions` section carrying both what is not covered (and who owns it)
   and what could not be verified.
   *Done when:* the file exists and restates no sibling node's canonical content.

4. **Relationships** — `references` edges only to ids confirmed present in
   `corpus-merged-ids.txt`: `verification-contracts-websocket`,
   `implementation-crates-buzz-relay`, `implementation-crates-buzz-ws-client`,
   `implementation-crates-buzz-acp`. No Feature #609 sibling (none merged).
   *Done when:* each target has been grepped out of the merged-ids list.

5. **Validate, self-review, stamp, commit.**
   *Done when:* `python3 launchpad/project-intelligence/corpus/validate.py` exits 0,
   the unittest suite ends `OK`, and one signed commit exists. No push, no PR.

## Out of scope

- The `OK` message (#1161) and the `CLOSED` message (#1147) — committed siblings,
  not merged; contrast only, never document their behaviour.
- `buzz-pair-relay`'s independent `make_notice` emitter — a different binary; noted
  as a boundary, not documented.
- `ModerationNotice` in `crates/buzz-relay/src/handlers/moderation_notices.rs` — an
  unrelated concept that shares the word; disambiguated, not documented.
- Any runtime behaviour change.
