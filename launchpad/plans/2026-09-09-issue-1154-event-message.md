Issue #1154 — task: document layers/protocol/event-message.md
Stated size: no `Size` line on the issue; scope stated unambiguously as exactly one
hand-authored canonical corpus document  ->  cap: 5 steps

ALREADY TRUE  (verified against the worktree at the recorded revision, not notes)
  Worktree `__worktrees/task-1154-event-message` branched from `origin/launchpad` at
  `29ca9b189bd3f639ba09c972b57c70538c0860c6`; `git cat-file -e` on that sha exits 0.
  `launchpad/docs/corpus/layers/protocol/` does not exist yet — `ls` on it fails. The
  target file is a create, not an edit.
  `crates/buzz-relay/src/protocol.rs` (458 lines, read in full) carries BOTH directions of
  the `EVENT` message:
    - `ClientMessage::parse`'s `"EVENT"` arm requires `arr.len() >= 2`, errors
      `"EVENT requires event object"` below that, and deserializes `arr[1]` into
      `nostr::Event`, mapping a failure to `"invalid event: {e}"`. It reads `arr[0]` and
      `arr[1]` only — any further array elements are never examined.
    - `RelayMessage::event(sub_id, event)` returns `json!(["EVENT", sub_id, event_json])` —
      three elements, subscription id at index 1, event at index 2.
  `crates/buzz-relay/src/connection.rs`'s `handle_text_message` answers a `ClientMessage::parse`
  failure with `RelayMessage::notice(&format!("invalid message: {e}"))` and returns — no `OK`.
  The same function answers an `EVENT` that cannot acquire a handler-semaphore permit with
  `notice("rate-limited: too many concurrent requests")`, also not an `OK`.
  The same file drops any text frame longer than `state.config.max_frame_bytes` before
  parsing, emitting a hand-built `["NOTICE","error: frame too large (...)"]` and breaking the
  read loop. `crates/buzz-relay/src/config.rs` sets `DEFAULT_MAX_FRAME_BYTES = 512 * 1024`.
  `crates/buzz-relay/src/handlers/event.rs` `handle_event` (read lines 600-760, plus a grep
  showing 20 `RelayMessage::ok` call sites in the file, all outside its test module) answers a
  parsed inbound `EVENT` with an `OK` naming `event.id.to_hex()` on every branch read.
  The live fan-out path does NOT use `RelayMessage::event`: `fan_out_event_to_local_subscribers`
  goes through `fanout_frame_cache` -> `event_frame_bytes_for_sub` -> `event_frame_for_sub`,
  which builds the same frame as `format!(r#"["EVENT","{}",{}]"#, sub_id, event_json)` — string
  interpolation, with no JSON escaping of `sub_id`. `ClientMessage::parse` constrains a REQ
  subscription id only by non-emptiness and a 256-byte limit, not by character.
  `crates/buzz-ws-client/src/message.rs` `parse_relay_message`'s `"EVENT"` arm is the exact
  mirror: `arr[1]` as `subscription_id`, `arr[2]` as the event.
  `RelayMessage` names two unrelated Rust types — a unit struct of formatter functions in
  `buzz-relay`, and an enum of parsed inbound messages in `buzz-ws-client`.
  Independent second implementations of the client shape: `crates/buzz-acp/src/relay.rs`
  (`json!(["EVENT", event])`) and `crates/buzz-test-client/tests/e2e_relay.rs`
  (`json!(["EVENT", &event])`).
  `crates/buzz-relay/src/protocol.rs`'s own tests pin both shapes: `parse_valid_messages`
  parses the 2-element client form, `format_relay_messages` asserts the serialized form has
  `v[0] == "EVENT"`, `v[1] == "sub1"`, `v[2]["id"]`.
  `docs/nips/` holds only Buzz's own two-letter NIPs; `ls docs/nips/NIP-01.md` fails. No
  upstream NIP-01 text is in this repository.
  Relationship targets confirmed present on `origin/launchpad` by
  `git grep -l "^id: <target>$" origin/launchpad -- launchpad/docs/corpus`, one hit each:
  `architecture-flows-event-ingestion`, `architecture-flows-live-fanout`,
  `architecture-flows-http-event-submission`, `architecture-flows-historical-query`,
  `implementation-crates-buzz-relay`, `implementation-crates-buzz-ws-client`,
  `verification-contracts-websocket`.
  No merged corpus node owns the `EVENT` wire shape: `grep -rln '\["EVENT"' launchpad/docs/corpus/`
  returns four nodes, all of which mention a frame in passing while documenting a flow or a crate.

STEP 1  Create `launchpad/docs/corpus/layers/protocol/event-message.md` with front matter    [independent]
        only: `id: layers-protocol-event-message`, `type: layers`, `status: draft`,
        `origin: launchpad`, `audiences: [agent, developer]`, and an `evidence` ledger whose
        first entry is the single commit-only provenance FACT naming
        `29ca9b189bd3f639ba09c972b57c70538c0860c6`.
        done when: the file exists, `python3 -c "import yaml"`-parseable front matter, and
        exactly one commit-only FACT is present.

STEP 2  Write the evidence ledger for every claim the body will make, classified against       [after 1]
        `AGENTS.md`'s rules: FACT only where the cited file was opened and says so; the
        "a client sending the relay->client 3-element shape is rejected" claim as INFERENCE,
        because it is traced through `serde_json::from_value::<Event>` on a JSON string rather
        than executed; the absence of upstream NIP-01 text as a tool-result citation naming the
        `ls` command and its real output; sibling-issue ownership (#1156/#1161/#1165/#1167) as
        TEAM_KNOWLEDGE with `provided_by`.
        done when: every entry's class satisfies the schema's conditional rules (FACT has
        `evidence` and neither `confidence` nor `provided_by`; INFERENCE has both `evidence`
        and `confidence`; TEAM_KNOWLEDGE has `provided_by` and no `confidence`), and every
        FACT's citation is a repo-relative path to a file opened during this task.

STEP 3  Write the body to the `templates/concept.md` required-section list: title,             [after 2]
        Definition (naming both shapes and disambiguating them explicitly, per the template's
        instruction to disambiguate a colliding name in the Definition), a Mermaid visual aid,
        Background, Use cases, a Comparison table of the two directions, Related resources as
        typed `relationships` rather than prose links, and Scope and omissions.
        done when: the body states both wire shapes as the code defines them, states what a
        malformed `EVENT` gets back, and links rather than restates the three merged flow nodes.

STEP 4  Add `relationships` edges only to ids confirmed present on `origin/launchpad` in the    [after 3]
        ALREADY TRUE list above; add no edge to any #609 sibling.
        done when: every `relationships[].target` re-verified by
        `git grep -l "^id: <target>$" origin/launchpad -- launchpad/docs/corpus` returning one hit.

STEP 5  Run `python3 launchpad/project-intelligence/corpus/validate.py`, fix what it names,     [after 4]
        re-read every FACT against its cited file, then run the verify-gate suite as the sole
        foreground command and commit with `-s`.
        done when: the validator exits 0, the unittest run's final line is `OK`, and one commit
        exists on `task/1154-event-message`.
