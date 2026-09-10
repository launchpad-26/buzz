# Plan — issue #1165: document the REQ message

**Issue:** launchpad-26/buzz#1165 (Feature #609, protocol and networking layer corpus)
**Target:** `launchpad/docs/corpus/layers/protocol/req-message.md`
**Node id:** `layers-protocol-req-message`
**Template:** `launchpad/docs/corpus/templates/concept.md`
**Worktree:** `__worktrees/task-1165-req-message`, branch `task/1165-req-message`
**Provenance revision:** `29ca9b189bd3f639ba09c972b57c70538c0860c6` (`git rev-parse HEAD` in the
worktree; confirmed with `git cat-file -e`, exit 0)

## Subject and boundary

The node's subject is the **REQ wire message** — `["REQ", <subscription_id>, <filter1>, …]`
— its array shape, every validation `ClientMessage::parse`'s REQ arm applies, and every
shape the relay answers a REQ with. It does **not** own filter semantics (#1157), the EOSE
marker (#1150), subscription lifecycle and fan-out (#1167), CLOSE (#1146) or NOTICE (#1160);
those are committed-but-unmerged siblings and must not be targeted by a relationship. The
merged `architecture-flows-historical-query` node owns the ordered flow — link, do not
restate.

## Steps

1. **Verify the evidence claims against source, in the worktree.** `crates/buzz-relay/src/protocol.rs`
   (the `REQ` arm of `ClientMessage::parse`, `MAX_SUB_ID_LENGTH`, `MAX_FILTERS_PER_REQ`, the
   `RelayMessage` formatters and the in-file test module), `crates/buzz-relay/src/connection.rs`
   (`handle_text_message`, `request_rejection_message`, `send_admission_result`),
   `crates/buzz-relay/src/handlers/req.rs` (`handle_req`, every rejection, registration
   position relative to the historical query, `filter_fully_pushable`),
   `crates/buzz-relay/src/handlers/event.rs` (`event_frame_for_sub` and its tests) and
   `crates/buzz-relay/src/nip11.rs` (`relay_limitation`).
   **Done when:** each of the five sibling-supplied claims is individually confirmed or
   refuted against a file opened here, and the NIP-11 advertisement of both limits is
   confirmed in `nip11.rs` rather than inferred from a code comment.

2. **Establish the absences honestly.** Grep for a test that exercises a subscription id
   containing a JSON metacharacter, and for callers of `filter_fully_pushable`.
   **Done when:** both greps have been run for real and their actual results are recorded in
   `identifier(args) -> result` tool-result form, per `validate.py`'s `_TOOL_RESULT_RE`.

3. **Pick relationships from merged ids only.** Grep `corpus-merged-ids.txt` for each
   candidate before writing it.
   **Done when:** every `relationships[].target` has been shown to appear in that file, and no
   #609 sibling id is present.

4. **Write the node** to the target path, following `templates/concept.md`'s required
   sections, with `type: layers`, `status: draft`, `origin: launchpad`, exactly one
   commit-only provenance FACT, and a *Scope and omissions* section carrying both the
   ownership boundary and the separate could-not-verify disclosure.
   **Done when:** the file exists, front matter carries only the seven schema-permitted
   fields, and every substantive body claim has a matching ledger entry.

5. **Validate, self-review, stamp, commit.** Run
   `python3 launchpad/project-intelligence/corpus/validate.py` to exit 0; re-read every
   evidence entry against its source; then run the corpus test suite as the sole foreground
   command and commit with `-s`.
   **Done when:** the validator exits 0, the suite ends `OK`, and the commit exists on
   `task/1165-req-message`.

## Risks

- **Restating a sibling.** The rejection table is message-level (what the client receives)
  and stays that way; the *reason* each rejection fires belongs to the filter, subscription
  and auth nodes and is only named, never explained.
- **Line-number drift.** Citations are bare repo-relative paths; `validate.py` does not check
  line numbers against file length (#1459).
- **Editing after the stamp clears it.** Complete the self-review before the first stamp run.
