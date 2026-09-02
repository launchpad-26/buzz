Issue #1018 — task: document interfaces/websocket/auth.md
Stated size: no `Size` line on the issue -> cap: 5 steps (single hand-authored
corpus document, one worktree, no code changes — matches the dispatcher's own
5-step cap for this task shape).

ALREADY TRUE (verified against git and the worktree, not notes)
  - Worktree exists at
    __worktrees/task-1018-interfaces-websocket-auth, branch
    task/1018-interfaces-websocket-auth, HEAD == origin/launchpad ==
    c34e62d16781dac3fa45cdedf0f09d4e1d8bbe8f (`git rev-parse HEAD` confirms).
  - `launchpad/docs/corpus/interfaces/` does not exist anywhere in this
    worktree or on `origin/launchpad` (`git ls-tree -r --name-only
    origin/launchpad -- launchpad/docs/corpus` lists no `interfaces/` path;
    `find launchpad/docs/corpus -ipath "*interfaces*"` in the worktree matches
    only `templates/interface.md`). The target file
    `launchpad/docs/corpus/interfaces/websocket/auth.md` does not exist yet.
  - `launchpad/docs/corpus/schema/node.schema.json`, `AGENTS.md`, and
    `templates/interface.md` already read in full this session. `type`'s
    13-member enum has no plain "interface" value; the combined
    `interfaces-events` value is the schema-correct choice, confirmed by
    `templates/interface.md`'s own "A note on `type`" section, which states a
    node built from that template "carries `type: interfaces-events`".
  - No node with id `interfaces-nostr-nip-42` or `events-kinds-kind-22242-auth`
    exists on `origin/launchpad`'s corpus tree at this revision (`git grep`
    for both ids returns nothing) — confirming the dispatcher's warning that
    #1014's and the kind-22242 sibling task's nodes are unmerged. No
    `relationships` entries will target them; they will be prose-linked by
    filename instead.
  - A closely related but distinctly-scoped node already exists and is
    merged: `launchpad/docs/corpus/architecture/flows/websocket-authentication.md`
    (id `architecture-flows-websocket-authentication`, type `architecture`).
    It documents the NIP-42 challenge/response as an ordered, stateful flow
    (trigger/preconditions/termination, 15 numbered interaction steps, gate
    order, failure table). This task's node is interface-shaped instead:
    the message contract itself (what `["AUTH", ...]` looks like on the wire
    in each direction, what a caller may rely on staying true) — it will
    cross-link that flow node by filename/id in prose and in its Boundary
    section rather than restate the interaction sequence.
  - Primary sources already opened and read this session, with the exact
    facts needed for the node's evidence ledger:
    - `crates/buzz-relay/src/protocol.rs` — `ClientMessage::parse` handles
      `"AUTH"` by deserializing `arr[1]` as a signed `Event`
      (`ClientMessage::Auth(Event)`); `RelayMessage::auth_challenge`,
      `RelayMessage::ok` format the two relay-to-client frames as
      `["AUTH", <challenge:string>]` and
      `["OK", <event_id>, <accepted:bool>, <message>]`. Both directions have
      `#[cfg(test)]` coverage in the same file
      (`parse_valid_messages`, `format_relay_messages`).
    - `crates/buzz-ws-client/src/message.rs` — the client-library mirror:
      `RelayMessage::Auth { challenge }` parses the relay's `["AUTH", ...]`
      frame; `OkResponse { event_id, accepted, message }` parses `["OK",
      ...]`; `build_auth_event` constructs the signed kind:22242 `Event` via
      `EventBuilder::auth(challenge, relay_url)`, optionally attaching a
      NIP-OA `auth` tag.
    - `crates/buzz-relay/src/connection.rs` — `AUTH_TIMEOUT = 5s`
      (line 29); `AuthState` enum (`Pending{challenge}`, `Authenticated(..)`,
      `Failed`); `handle_connection` sends the challenge frame before
      registering the connection with the connection manager, and an
      `auth_timeout_task` cancels the connection if `AuthState` is not
      `Authenticated` after 5s.
    - `crates/buzz-ws-client/src/connection.rs` — `AUTH_CHALLENGE_TIMEOUT_SECS
      = 20`, `AUTH_OK_TIMEOUT_SECS = 20` (lines 17, 20); `authenticate()`
      waits on both in sequence.
    - `crates/buzz-core/src/kind.rs:77` — `pub const KIND_AUTH: u32 = 22242;`
      with the doc comment "NIP-42 auth event — never stored (carries bearer
      tokens)".
    - `crates/buzz-auth/src/nip42.rs` — `generate_challenge()` (32 CSPRNG
      bytes, hex-encoded); `verify_nip42_event` checks kind ==
      `Kind::Authentication`, Schnorr signature, `challenge` tag match,
      `relay` tag match, and `created_at` within the doc-commented ±60s
      window, in that order.
    - `crates/buzz-relay/src/handlers/auth.rs` — exact client-visible
      rejection strings for the AUTH-message-level failures: `"auth-required:
      already authenticated"`, `"auth-required: authentication already
      failed"`, `"auth-required: verification failed"`,
      `"blocked: you are banned from this community"`, `"error: internal
      error checking restriction state"`, `"restricted: not a relay member"`.

STEP 1 [independent] Re-confirm the two boundary facts the node's Boundary
section depends on, since they are load-bearing and were read once already:
(a) re-open `crates/buzz-relay/src/handlers/event.rs`/`req.rs`/`count.rs` far
enough to quote each handler's own AuthState-gate rejection string for
EVENT/REQ/COUNT (these are downstream consumers of AUTH's outcome, not part
of the AUTH message contract itself, and must be named as "not covered" with
a citation, not asserted from memory); (b) confirm no corpus node id
`interfaces-nostr-nip-42` or `events-kinds-kind-22242-auth` exists on
`origin/launchpad` at the commit this plan will actually build from (re-run
the `git grep`/`git ls-tree` check immediately before drafting, not reuse
this plan's snapshot, since sibling tasks may merge concurrently).
  done when: both citations are written down with exact file paths and quoted
  strings, and the id-existence re-check's command output is captured
  verbatim (not paraphrased) immediately before Step 2 begins.

STEP 2 [needs 1] ← RUNS HERE. Write
`launchpad/docs/corpus/interfaces/websocket/auth.md`: front matter (id
`interfaces-websocket-auth`, type `interfaces-events`, status `draft`, origin
`launchpad`, audiences `[agent, developer, reviewer]`, no `relationships` per
Step 1(b)'s re-check, full evidence ledger with one entry per substantive
claim, classified FACT/INFERENCE/TEAM_KNOWLEDGE per `AGENTS.md`'s rules) and
body following `templates/interface.md`'s required sections: Interface
description (the WebSocket AUTH message boundary specifically — the
`["AUTH", ...]` frame in both directions plus its `OK` acknowledgement — not
the whole connection lifecycle); Operations (client->relay `["AUTH",
<signed kind:22242 event>]`, relay->client `["AUTH", "<challenge>"]`
challenge frame, relay->client `["OK", <event_id>, <accepted>, <message>]`
acknowledgement, each row citing the code symbol that defines it); Contract
and stability (the 5s server-side / 20s+20s client-side timeout asymmetry,
the ±60s timestamp window, the never-stored invariant on kind:22242, the
one-AUTH-per-outcome state-machine rule with no re-verification on a second
attempt); at least one valid example (a successful `AUTH`/`OK true` pair) and
one failure example (a rejected `AUTH`/`OK false` pair, e.g. challenge
mismatch); Boundary (explicitly not the NIP-42 protocol contract itself —
`interfaces/nostr/nip-42.md`, unmerged; not the kind:22242 event's own tag/
content schema — the kind-22242 event-kind node, unmerged; not the full
connection-lifecycle flow, ordering of the ban/allowlist/membership gates, or
per-message-type enforcement on EVENT/REQ/COUNT — the merged
`architecture-flows-websocket-authentication` node); Relationships (none
declared, reasoned in prose); Scope and omissions (gap table plus the
"expected but not verified" list, naming anything from Step 1 that stayed a
citation rather than a fully independent re-derivation).
  done when: the file exists, is schema-shaped per `node.schema.json`, and
  contains every required section named above with no section left as a
  placeholder.

STEP 3 [needs 2] Run `python3
launchpad/project-intelligence/corpus/validate.py` from the repository root.
Fix whatever it reports (schema errors, unresolved relationship targets,
broken citation paths) and re-run until it exits 0. Treat any FAIL not
caused by this node as a fresh finding to report, not something to route
around.
  done when: the command's own exit code is 0, observed directly from this
  session's own invocation (not assumed from a prior run).

STEP 4 [needs 3] Self-review the diff against issue #1018's Definition-of-done
checklist line by line: exactly one hand-authored canonical document; schema-
valid front matter with stable id/type/status/origin/audiences/evidence;
one independently maintainable node with no second concept folded in;
every substantive claim traceable and FACT/INFERENCE/TEAM_KNOWLEDGE not
conflated; links to implementation/verification/spec/neighboring nodes
without duplicating their canonical content; checked against the recorded
revision; validate.py clean; inputs/messages, outputs/responses, error/
rejection behavior defined; auth/authorization, versioning/compatibility,
ordering/idempotency defined where applicable; authoritative spec link
present (upstream NIP-42); at least one valid and one failure example
present.
  done when: each checklist bullet is confirmed against the actual file
  content (quoting the section that satisfies it), not asserted from memory
  of having written it.

STEP 5 [needs 4] Run `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole
command in its own tool call and confirm it prints `OK`; only then, in a
separate call, `git add` the node and this plan and `git commit -s`. If the
commit is rejected for a missing gate stamp, stop and report that as a
finding rather than touching any stamp file or using `--no-verify`.
  done when: the unittest run prints `OK` and the subsequent commit succeeds
  with `git rev-parse HEAD` resolving to a new commit on
  `task/1018-interfaces-websocket-auth`, or the rejection is reported
  verbatim as a `BLOCKED` finding.

PARALLEL: none — a single new file in a single worktree, and every step from
2 onward depends on its immediate predecessor's output (evidence -> draft ->
validate -> self-review -> commit). Step 1's two re-checks are independent of
each other and could in principle run as parallel subagents, but this is a
single-agent session and they are cheap enough to do sequentially.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit
0 (Step 3). `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print `OK`
before any commit (Step 5). This task's own instructions explicitly scope out
opening a PR or running the downstream review-code/review-adjudicate/
review-final gates — those are left for whatever process picks this branch
up next, not this session.

BUDGET: Step 2 (writing the body) is where the budget goes — the interface
template's required sections (Operations table, Contract and stability,
Boundary, worked examples) need real drafting grounded in the sources listed
under ALREADY TRUE, not templated filler. Steps 1, 3, 4, 5 are each a single
command or a short re-read and should be quick by comparison.

OPEN: Whether the merged `architecture-flows-websocket-authentication` node
should itself gain a `references` (or similar) edge pointing at this new
interface node is not this task's to decide — that would be an edit to an
existing merged node, and this issue's own "Out of scope" section rules out
"changing runtime product behavior" and "broad while-here cleanup"; a docs-
only forward edge is arguably neither, but it is still a second file's
content decision this plan defers rather than silently makes. Whether
`interfaces-events` (the only schema-legal choice) reads as a slightly odd
label for a node that is unambiguously interface-shaped is inherited from
`node.schema.json`'s own enum, not something this task can change.

LEFT OUT: Declaring `relationships` toward `interfaces-nostr-nip-42` or
`events-kinds-kind-22242-auth` — both confirmed unmerged in ALREADY TRUE, and
a relationship target that resolves in a worktree but not on `origin/launchpad`
is a hard CI error per `AGENTS.md`'s own node-creation step 9. Restating the
NIP-42 protocol contract, the kind:22242 event's own tag/content schema, or
the full connection-lifecycle interaction sequence — all three already have a
better home (the unmerged NIP-42/kind-22242 nodes and the merged flow node,
respectively) and duplicating them here would violate the issue's own
"Creating or materially editing a second hand-authored canonical corpus
document" out-of-scope line. Opening a PR, running review-code/review-tests/
review-adjudicate/review-final, or merging anything — this task's own
instructions say not to.
