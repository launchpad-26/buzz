Issue #1151 (Feature #609) — document ephemeral events as a `layers/protocol` corpus concept node
Stated size: no `Size` line in the issue body (corpus-plan `type:task` template carries none) -> cap: 5 steps,
set by the dispatch brief rather than read from the issue.

ALREADY TRUE  (verified against the real code and real command output, not notes)
  Worktree `/home/serina/Launchpad/buzz/__worktrees/task-1151-ephemeral-event`, branch
  `task/1151-ephemeral-event`, branched from `origin/launchpad`. `git rev-parse HEAD` inside the
  worktree reports `29ca9b189bd3f639ba09c972b57c70538c0860c6`; `git cat-file -e` on that sha exits 0.
  `launchpad/docs/corpus/layers/protocol/` **does not exist yet** — `ls` reports "No such file or
  directory", and the merged-id list contains zero `layers/protocol` rows. This node creates the
  directory.

  `crates/buzz-core/src/kind.rs` defines `EPHEMERAL_KIND_MIN = 20000`, `EPHEMERAL_KIND_MAX = 29999`,
  and `pub const fn is_ephemeral(kind) -> kind >= MIN && kind <= MAX` — a pure range test, not a
  per-kind table. **Nine** kinds are declared in that range, in two separate registry blocks
  (this plan's first draft said five; the node's own pre-stamp self-review caught it): the five
  fanned-out ephemeral events `KIND_PRESENCE_UPDATE` 20001, `KIND_TYPING_INDICATOR` 20002,
  `KIND_PAIRING` 24134, `KIND_AGENT_OBSERVER_FRAME` 24200, `KIND_HUDDLE_REACTION` 24810; and
  four credential kinds each doc-commented "not stored" — `KIND_AUTH` 22242,
  `KIND_BLOSSOM_AUTH` 24242, `KIND_NOSTR_IDENTITY_BINDING` 24243, `KIND_HTTP_AUTH` 27235.
  Because the test is arithmetic, `is_ephemeral(22242)` is true, which is why a dedicated
  `KIND_AUTH` equality check sits *before* the `is_ephemeral` branch in both
  `handlers/event.rs` and `buzz-db/src/store/event.rs`.

  Persistence is refused at three distinct call sites in `buzz-db`, each by the same range test:
  `store/event.rs:307`, `store/event.rs:1173`, `runtime/mod.rs:927`, all returning
  `DbError::EphemeralEventRejected(kind)` whose `thiserror` text is "ephemeral events (kind {0}) must
  not be stored" (`crates/buzz-db/src/error.rs`).

  `crates/buzz-relay/src/handlers/event.rs:698` branches on `is_ephemeral(kind_u32)` and routes to
  `handle_ephemeral_event` (line 795), which verifies the signature, optionally updates Redis presence
  state for kind 20001, then Redis-publishes on `EventTopic::Channel(ch_id)` or `EventTopic::Global`
  and directly fans out to local WebSocket subscribers. It returns before `ingest_event` (called at
  line 761) is ever reached — so no database round-trip occurs on this path.

  **The merged node's claim, checked directly.**
  `launchpad/docs/corpus/implementation/crates/buzz-ws-client.md:44` carries a `FACT` stating "the
  relay rejects ephemeral event kinds (20000-29999) over its HTTP surface", citing
  `crates/buzz-cli/src/client.rs`. That file's doc comment on `publish_ephemeral_event` (line 1091)
  does say "The relay rejects ephemeral kinds (20000–29999) over HTTP", so the node quoted its source
  faithfully — the error is upstream of it, in the doc comment.
  The actual transport gate is `crates/buzz-relay/src/handlers/ingest.rs:2193`:
  `if auth.is_http() && (kind_u32 == KIND_GIFT_WRAP || kind_u32 == KIND_PRESENCE_UPDATE)`. Confirmed
  values in `kind.rs`: `KIND_GIFT_WRAP = 1059` (line 60) and `KIND_PRESENCE_UPDATE = 20001` (line 465).
  So the transport gate names two kinds, is not range-based, and blocks one non-ephemeral kind.
  A **second, separate** mechanism does refuse the rest: `required_scope_for_kind`
  (`ingest.rs:437-547`) ends `_ => Err("restricted: unknown event kind")`, and
  `sed -n '437,547p' ... | grep -E "PRESENCE|TYPING|PAIRING|OBSERVER|HUDDLE_REACTION"` returns nothing
  (exit 1) — no ephemeral kind is in that allowlist. `ingest_event` applies it at line 2249. So the
  *outcome* the merged node asserts is coincidentally true, but its stated mechanism and its range
  framing are both wrong, and the gate it implies would also catch kind 1059, which is not ephemeral.
  A second merged node, `architecture-flows-http-event-submission`, already states the gate correctly
  ("Kind 1059 ... and kind 20001 ... are rejected specifically when submitted over the HTTP transport
  (`auth.is_http()`)") — so two merged nodes disagree, and the code is the authority.

  Boundary nodes exist and are merged: `capabilities-presence-presence`,
  `capabilities-presence-typing-indicator`, `layers-data-redis-presence`,
  `layers-data-redis-typing-indicators`, plus `architecture-flows-live-fanout`, which already owns the
  publish-then-fan-out mechanism and explicitly documents the `handle_ephemeral_event` inline path.
  `capabilities-presence-typing-indicator`'s own Boundary section defers the general ephemeral
  mechanism to `architecture-flows-live-fanout` and records that no protocol/interface node exists yet
  — this node fills the concept half of that gap without duplicating the flow.

STEPS

1. Create `launchpad/docs/corpus/layers/protocol/ephemeral-event.md` with front matter only:
   `id: layers-protocol-ephemeral-event`, `type: layers`, `status: draft`, `origin: launchpad`,
   `audiences: [agent, developer]`, and the evidence ledger — exactly one commit-only FACT recording
   `29ca9b189bd3f639ba09c972b57c70538c0860c6`, plus one entry per substantive claim below, each citing
   a bare repo-relative path already opened in ALREADY TRUE. The HTTP-gate discrepancy gets its own
   entry. `operator` is deliberately not in `audiences`: nothing here is a runbook or a tuning surface.
   Done when: the file parses as YAML and every `evidence` string is either a bare path that exists or
   the one `commit <sha>` citation.

2. Write the body against `templates/concept.md`'s required sections — one-sentence definition first,
   then the kind range and its nine declared members split into fanned-out events versus
   credentials, the never-stored invariant and its three
   `buzz-db` enforcement points, the no-database-round-trip delivery path (linked to
   `architecture-flows-live-fanout`, not restated), and a Boundary section naming what the four merged
   presence/typing nodes own.
   Done when: every `##` section the template marks required is present, and no paragraph restates a
   boundary node's canonical content rather than linking to it.

3. Add the *Scope and omissions* section carrying both required halves separately: what the node does
   not cover and who owns it, and — distinctly — what was expected to be verified and could not. The
   second half must record: (a) `test_ephemeral_event_not_stored` in
   `crates/buzz-test-client/tests/e2e_relay.rs` is `#[ignore]` and needs a live relay, so it was read
   and not run; (b) the historical-query consequence (a `REQ` for an ephemeral kind returns nothing
   from storage) is reasoned from the insert guards, not observed, and is classified INFERENCE; (c) the
   `buzz-ws-client` discrepancy is recorded here and deliberately **not** fixed, since the merged node
   and the `buzz-cli` doc comment that seeded it are separate tasks.
   Done when: the section names all three, and the two halves are visibly distinct subsections.

4. Add `relationships` edges only to ids confirmed present in the merged-id list by grep:
   `capabilities-presence-presence`, `capabilities-presence-typing-indicator`,
   `layers-data-redis-presence`, `layers-data-redis-typing-indicators`,
   `architecture-flows-live-fanout`, `architecture-flows-http-event-submission`,
   `implementation-crates-buzz-core` — all `references`. No Feature #609 sibling id is targeted, since
   none is merged.
   Done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 and reports no
   unresolved relationship target.

5. Self-review every DoD bullet and re-check each evidence entry against its source file before
   stamping. Then run the verify-gate suite as the sole foreground command with a 600000 ms timeout,
   confirm the run ends `OK`, and commit with `git commit -s` in a separate call. No push, no PR.
   Done when: the suite prints `OK`, the commit exists, and `git status --short` shows no unstaged
   corpus change.
