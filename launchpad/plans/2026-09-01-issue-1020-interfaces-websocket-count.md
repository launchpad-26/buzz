Issue #1020: document interfaces/websocket/count.md

Stated size: issue #1020 states no explicit Size line -> cap: 5 steps (task-instruction cap).

ALREADY TRUE

- `launchpad/docs/corpus/interfaces/` does not exist in this worktree (checked
  `ls launchpad/docs/corpus/interfaces` -> "No such file or directory"), and the
  target `launchpad/docs/corpus/interfaces/websocket/count.md` does not exist
  either. Nothing to update; this is a create.
- `origin/launchpad`'s corpus tree (`git ls-tree -r --name-only origin/launchpad --
  launchpad/docs/corpus`) contains no interface-shaped node yet -- only
  AGENTS.md, README.md, `agents/invariants.md`, `architecture/**`,
  `development/**` and `standards/**`. `interfaces-nostr-nip-45` (#1015) and
  `interfaces-http-count` (#978) are confirmed NOT present on `origin/launchpad`,
  matching the task brief -- they cannot be `relationships` targets yet.
- `launchpad/docs/corpus/templates/interface.md` already exists (a template does
  exist, contrary to the task brief's caveat) and states plainly that an instance
  node built from it "therefore carries `type: interfaces-events`" -- the schema's
  `type` enum has no separate `interface` value, only the combined
  `interfaces-events` surface (`node.schema.json`'s `type.enum`).
- `crates/buzz-relay/src/handlers/count.rs` (`handle_count`) and
  `crates/buzz-relay/src/protocol.rs` (`ClientMessage::Count`,
  `RelayMessage::count`) are the actual WebSocket COUNT (NIP-45) implementation,
  already read in full. `crates/buzz-relay/src/connection.rs:616-635` dispatches
  a parsed `Count` message to `handle_count`. Valid- and failure-example tests
  already exist: `crates/buzz-test-client/tests/e2e_persona.rs:782-847`
  (`test_persona_count_excludes_foreign_unshared`, a valid COUNT round trip) and
  `crates/buzz-test-client/tests/e2e_event_reminder.rs:1003-1057`
  (`test_ws_count_returns_zero_for_other_users_reminders`, a CLOSED
  `"restricted:"` rejection). No new test needs to be written; the node cites
  these.
- Candidate `relationships` targets already merged on `origin/launchpad` and
  confirmed present: `architecture-flows-websocket-connection`,
  `architecture-flows-websocket-authentication`, `architecture-containers-relay`.
  All three are plausibly relevant (WS lifecycle this message rides on, the
  NIP-42 auth `handle_count` requires, the container this interface is part of).

STEP 1 -- Draft the node body and front matter [independent] <- RUNS HERE

Write `launchpad/docs/corpus/interfaces/websocket/count.md` following
`templates/interface.md`'s required sections (Interface description,
Operations, Contract and stability, Boundary, Relationships, Scope and
omissions), with `type: interfaces-events`, `status: draft`, `origin:
launchpad`, and one `evidence` entry per substantive claim, each citing a real
path/line opened during research (`count.rs`, `protocol.rs`, `connection.rs`,
`req.rs`'s `p_gated_filters_authorized`, `nip11.rs`'s `SUPPORTED_NIPS`,
`docs/multi-tenant-relay.md`'s `O.WS.COUNT` observational-interface entry, the
two test files above). No `relationships` target `interfaces-nostr-nip-45` or
`interfaces-http-count` (unmerged); `references`/`part-of` may target the three
already-merged ids named above.

done when: the file exists at that path, `python3 -c "import
yaml,sys; yaml.safe_load(open(sys.argv[1]).read().split('---')[1])"
launchpad/docs/corpus/interfaces/websocket/count.md` parses without error, and
every DoD bullet in issue #1020 (inputs/messages, outputs/responses,
error/rejection behavior, auth/authz, versioning/compatibility,
ordering/idempotency, link to NIP-45, one valid + one failure example) has a
corresponding section or sentence in the body.

STEP 2 -- Validate against the corpus checker [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
worktree root.

done when: the command exits 0 (UNVERIFIED notices are acceptable; any FAIL
line is not, and any FAIL not caused by this new node is escalated as a
separate finding rather than silently patched).

STEP 3 -- Run the corpus test suite (the commit gate) [needs 2]

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
-p "test_*.py"` as the sole command in its own call.

done when: the command prints `OK` on stderr/stdout with no failures or errors.

STEP 4 -- Self-review against the issue's DoD line by line [needs 3]

Re-read the diff against every Definition-of-done bullet in issue #1020;
confirm exactly one hand-authored corpus document was created, no second
canonical document exists, every evidence entry's cited source was actually
opened, and `validate.py` still exits 0.

done when: each DoD bullet is checked off against a specific line/section in
the drafted node, in the final report.

STEP 5 -- Commit [needs 4]

`git add` the node and this plan file; `git commit -s` with the message
`docs(corpus): document WebSocket COUNT interface (#1020)`.

done when: `git log -1 --format=%H` on the worktree branch shows a new commit
containing exactly those two files, and `git log -1 --format=%B` includes a
`Signed-off-by` trailer (added automatically by `-s`, or by the repo's
commit-msg hook).

PARALLEL

None of steps 2-5 can run before the step before it; this is a single-node,
single-author task with no independent parallel track. Step 1 is the only
`[independent]` step.

GATES

- `python3 launchpad/docs/corpus/../../project-intelligence/corpus/validate.py`
  (i.e. `launchpad/project-intelligence/corpus/validate.py`) must exit 0 before
  committing.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
  -p "test_*.py"` must print `OK` before committing -- this is the commit gate
  referenced in the task brief; if a stamp/hook rejects the commit despite this
  passing, that is reported as a finding, not routed around.
- No `git commit --no-verify`.

BUDGET

One node, one plan file, one commit. No code changes, no test changes, no
second corpus document. Expected total tool-call budget: under 40 calls
end-to-end (research already largely done before this plan was written).

OPEN

- Whether `interfaces-events` nodes documenting a protocol-level message (COUNT)
  rather than a single event kind should also `references` a future
  `interfaces-nostr-nip-45` node once #1015 merges -- left for a later edit,
  per `AGENTS.md`'s rule that relationships may only target ids present on the
  branch being merged into.
- Whether NIP-45's absence from `nip11.rs`'s `SUPPORTED_NIPS` (verified: 45 is
  not in `&[1, 2, 10, 11, 16, 17, 23, 25, 29, 33, 38, 42, 50, 56]`) is a known
  gap or an oversight is not decided by this task -- the node records it as a
  FACT and an open discrepancy, not as something this task resolves.

LEFT OUT

- Editing or duplicating `interfaces/nostr/nip-45.md` (#1015) or
  `interfaces/http/count.md` (#978) content -- out of scope per the issue and
  per `AGENTS.md`'s one-idea-per-node rule; this node prose-links by filename
  instead of by unresolvable `relationships` target.
- Any change to `crates/buzz-relay` runtime behavior, including fixing the
  NIP-11 `SUPPORTED_NIPS` gap noted above -- documentation only, per the
  issue's own "Out of scope" list.
- Generated corpus indexes -- none exist yet for this subtree; not touched.
