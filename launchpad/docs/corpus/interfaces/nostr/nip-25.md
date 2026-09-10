---
id: interfaces-nostr-nip-25
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "node.schema.json's type enum has no bare 'interface' value; the value for an interface-shaped node is the single combined token interfaces-events, and templates/interface.md's own 'A note on type' section states a node built from that template 'carries type: interfaces-events'."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/interface.md"
  - statement: "buzz-core/src/kind.rs declares KIND_REACTION as u32 = 7 with the doc comment 'NIP-25: Content is emoji char or `+`/`-`.', and separately declares KIND_HUDDLE_REACTION = 24810 as an ephemeral, never-stored, channel-scoped huddle emoji-reaction burst distinct from kind:7."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "required_scope_for_kind maps KIND_REACTION (and KIND_DELETION, KIND_GIFT_WRAP, and several stream/forum kinds) to Scope::MessagesWrite, the same scope ordinary channel messages require to be submitted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "A reaction event carries no h tag of its own; the reactions_do_not_require_h_tag test asserts requires_h_channel_scope(KIND_REACTION) is false, and derive_reaction_channel instead resolves channel_id by looking up the target event named in the reaction's e tag and reusing that event's channel_id (Some for a channel message, None for a global/project event)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "derive_reaction_channel returns NoTarget when no valid 64-hex e tag is present, and NotFound when the e tag names a target event id absent from this community; both cases surface before the reaction-specific insert logic runs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "The ingest pipeline's ban/timeout restriction check runs before the reaction-specific branch, and a DB error while checking that restriction state fails closed with an Internal error rather than admitting the write."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "The reaction ingest branch extracts the target event id from the last e tag (accepting only 64-character lowercase hex), rejecting with 'invalid: reaction must reference a target event via e tag' when absent and 'invalid: malformed reaction target id' when the hex fails to decode."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Reaction content defaults to '+' when empty (matching NIP-25's own convention), and validate_reaction_emoji accepts any content up to 64 characters; content over 64 characters is accepted only as a NIP-30 custom-emoji shortcode of the form ':shortcode:' whose normalized form matches the content exactly and which carries a matching [\"emoji\", shortcode, url] tag, otherwise it is rejected with 'invalid: reaction emoji exceeds 64 characters (got N)' or 'invalid: long custom emoji reaction shortcode must be canonical lowercase'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "buzz-db's reaction.rs module doc comment states the storage invariant directly: 'One reaction per user per emoji per event. Soft-delete via removed_at.' The ADD_REACTION_SQL statement enforces this with INSERT ... ON CONFLICT (community_id, event_created_at, event_id, pubkey, emoji) DO UPDATE ... WHERE reactions.removed_at IS NOT NULL, which the add_reaction doc comment states exists to 'eliminate the TOCTOU race where two concurrent adds both see no existing row and then race to INSERT.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/reaction.rs"
  - statement: "At the ingest layer, inserting a kind:7 event whose (target, actor, emoji) tuple is already active returns ReactionEventInsertOutcome::Duplicate, which the handler turns into IngestResult { accepted: false, message: \"duplicate: reaction already exists\" } without storing a second event; a genuinely new reaction returns IngestResult { accepted: true, message: String::new() }; and a target event absent or soft-deleted at insert time returns ReactionEventInsertOutcome::TargetMissing, rejected as 'invalid: reaction target event not found'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-db/src/store/reaction.rs"
  - statement: "IngestError has exactly three variants, each with a doc comment stating its WebSocket and HTTP surfacing: Rejected (client error -- WS: OK false, HTTP: 400), AuthFailed (auth/scope error -- WS: OK false, HTTP: 401/403), Internal (server error -- WS: OK false, HTTP: 500). Every reaction-specific rejection in this node uses the Rejected variant, so it surfaces as HTTP 400 / WS OK-false, never as an auth or server error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Removing a reaction is a NIP-09 kind:5 deletion event whose e tag names the reaction's own kind:7 event id, not a NIP-25-specific removal message; side_effects.rs's deletion handler special-cases a deleted target of kind:7 by calling remove_reaction_by_source_event_id first, falling back to deriving (target, actor, emoji) from the reaction event itself (via effective_message_author, to handle legacy relay-signed reactions) and removing by that tuple if the id-based removal was missed."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "buzz-sdk's builders.rs provides build_reaction (kind 7, e tag only, emoji content up to 64 chars, returns SdkError::EmojiTooLong otherwise), build_custom_emoji_reaction (kind 7, e tag plus an [\"emoji\", shortcode, url] tag, content \":shortcode:\"), and build_remove_reaction (kind 5, e tag naming the reaction event id) -- typed constructors for the same three operations the CLI and relay implement."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs"
  - statement: "buzz-cli's reactions.rs implements three subcommands: cmd_add_reaction (builds and submits a kind:7 event via buzz_sdk::build_reaction or build_custom_emoji_reaction, then prints the normalized write response), cmd_remove_reaction (queries the caller's own kind:7 reactions on the target event via a {\"kinds\":[7],\"#e\":[...],\"authors\":[...]} filter, matches by emoji content, then submits a kind:5 deletion built by build_remove_reaction), and cmd_get_reactions (queries {\"kinds\":[7],\"#e\":[...]} with no author filter and groups results client-side into {emoji, count, pubkeys} summaries sorted by emoji)."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/reactions.rs"
  - statement: "Root AGENTS.md documents buzz-cli's stability contract in prose: normal reads return sig-stripped/normalized JSON, writes return {event_id, accepted, message}, and HTTP auth accepts NIP-98 (Authorization: Nostr <base64>) alongside a dev-mode X-Pubkey header per HttpAuthMethod's two variants -- the same write-response and auth surface a reaction add/remove goes through, since reactions have no bespoke auth or response shape of their own."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Parent Feature #616 and issue #1011 both scope this node to the interfaces/nostr/nip-25.md path as a single canonical interface node, distinct from events/kinds/kind-7-reaction.md (issue #882's sibling node documenting the kind:7 wire contract itself)."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1011 definition of done"
  - statement: "events/kinds/kind-7-reaction.md does not exist anywhere in this worktree or on origin/launchpad at the recorded revision, so it cannot be a schema-valid relationships target here; it is referenced in this node's Boundary section by filename/issue number only."
    entry_class: FACT
    evidence:
      - "find_files('launchpad/docs/corpus/**/kind-7-reaction.md') -> no match against this worktree at commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "The NIP-25 specification is maintained upstream in the nostr-protocol/nips repository; this node links to it pinned at a specific commit rather than restating its text, and the exact wire-shape claims above were independently verified against this repository's own code and tests rather than by fetching that document in this session."
    entry_class: INFERENCE
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/24b2ae9fdfeb4e5c0d3be854df5977b81afe1983/25.md"
    confidence: 0.6
relationships:
  - type: implements
    target: corpus-template-interface
  - type: references
    target: architecture-flows-websocket-authentication
  - type: part-of
    target: architecture-containers-relay
---

# NIP-25 Reactions: interface

Upstream [NIP-25](https://github.com/nostr-protocol/nips/blob/24b2ae9fdfeb4e5c0d3be854df5977b81afe1983/25.md) defines a
Nostr "reaction" event (kind:7): a signed event whose content is an emoji (or the
bare `+`/`-` shorthand, or empty defaulting to `+`) and whose `e` tag names the event
being reacted to. Buzz implements the full lifecycle of this event kind across three
surfaces that exchange it with each other: the relay's generic Nostr ingest pipeline
(WebSocket `EVENT` frames and HTTP `POST /events`, both reachable via `POST /query`
for reads), `buzz-sdk`'s typed event builders, and `buzz-cli`'s `reactions` subcommand
group. A reaction is removed the same way any Nostr event is removed under NIP-09 — a
kind:5 deletion event naming the reaction's own event id — not through a
NIP-25-specific removal message.

## Operations

| Operation | Defined in | Summary |
|---|---|---|
| Add a reaction | Relay: reaction branch of the ingest pipeline in `crates/buzz-relay/src/handlers/ingest.rs`. SDK: `buzz_sdk::build_reaction` / `build_custom_emoji_reaction` in `crates/buzz-sdk/src/builders.rs`. CLI: `cmd_add_reaction` in `crates/buzz-cli/src/commands/reactions.rs` (`buzz reactions add <event> <emoji> [--emoji-url <url>]`). | Sign and submit a kind:7 event with a target `e` tag; content is `+`, `-`, an emoji (max 64 chars), or a NIP-30 `:shortcode:` paired with a matching `["emoji", shortcode, url]` tag. |
| Remove a reaction | SDK: `buzz_sdk::build_remove_reaction`. CLI: `cmd_remove_reaction` in `crates/buzz-cli/src/commands/reactions.rs` (`buzz reactions remove <event> <emoji>`), which first queries the caller's own kind:7 reactions to find the matching event id. Relay-side removal: `crates/buzz-relay/src/handlers/side_effects.rs`'s deletion handler. | Submit a NIP-09 kind:5 deletion whose `e` tag names the reaction's own kind:7 event id; the relay soft-deletes the corresponding `reactions` row (`removed_at`). |
| Query reactions on an event | `POST /query` (or WebSocket `REQ`) with a NIP-01 filter `{"kinds":[7],"#e":["<event id>"]}`. CLI: `cmd_get_reactions` in `crates/buzz-cli/src/commands/reactions.rs` (`buzz reactions get <event>`). | Returns matching kind:7 events; the CLI additionally groups them client-side into `{emoji, count, pubkeys}` summaries. |

## Contract and stability

- **Authentication/authorization.** A reaction submission goes through the same
  authenticated write path as every other event: `required_scope_for_kind` maps
  `KIND_REACTION` to `Scope::MessagesWrite`, the identical scope ordinary channel
  messages require (`crates/buzz-relay/src/handlers/ingest.rs`). HTTP callers
  authenticate via NIP-98 (`Authorization: Nostr <base64>`) or a dev-mode `X-Pubkey`
  header (`HttpAuthMethod`, `crates/buzz-relay/src/handlers/ingest.rs`); WebSocket
  callers authenticate via NIP-42. A banned or timed-out actor's restriction state is
  checked before the reaction-specific branch runs, and a database error while
  checking it fails closed (`IngestError::Internal`) rather than admitting the write.
- **Channel scoping.** A reaction carries no `h` tag of its own — the
  `reactions_do_not_require_h_tag` test in `crates/buzz-relay/src/handlers/ingest.rs`
  confirms `requires_h_channel_scope(KIND_REACTION)` is `false`. Instead,
  `derive_reaction_channel` resolves `channel_id` from the target event named in the
  `e` tag: a reaction on a channel message becomes channel-scoped, a reaction on a
  channel-less event (e.g. a global note, or a project issue/PR root) is stored with
  `channel_id = None`.
- **Ordering/idempotency.** `crates/buzz-db/src/store/reaction.rs` states the
  invariant directly: "One reaction per user per emoji per event. Soft-delete via
  `removed_at`." The `reactions` table's `ON CONFLICT (community_id,
  event_created_at, event_id, pubkey, emoji) DO UPDATE ... WHERE
  reactions.removed_at IS NOT NULL` clause makes add-reaction safe under concurrent
  writers (its doc comment: "eliminate the TOCTOU race where two concurrent adds
  both see no existing row and then race to INSERT") and makes re-adding a
  previously-removed reaction reactivate the same row rather than create a new one.
  At the event-ingest layer, a duplicate active `(target, actor, emoji)` tuple is
  rejected as a no-op rather than stored a second time (see Outputs below).
- **Outputs/responses.** A newly accepted reaction returns
  `IngestResult { event_id, accepted: true, message: String::new() }`. A duplicate
  active reaction returns `IngestResult { event_id, accepted: false, message:
  "duplicate: reaction already exists" }` without storing a second kind:7 event.
  Both shapes match root `AGENTS.md`'s documented write-response contract
  (`{event_id, accepted, message}`) — reactions define no bespoke response shape.
  `buzz reactions get` returns `{"reactions": [{"emoji", "count", "pubkeys"}, ...]}`.
- **Error/rejection behavior.** Every reaction-specific rejection below is
  `IngestError::Rejected`, whose doc comment states its surfacing as "WS: OK false,
  HTTP: 400" (never an auth or server error) — none of these are `AuthFailed` or
  `Internal`:
  - `"invalid: reaction must reference a target event via e tag"` — no valid
    64-hex `e` tag present.
  - `"invalid: malformed reaction target id"` — the `e` tag's content is not valid
    hex.
  - `"invalid: reaction target event not found"` — the `e` tag names a target
    event id absent from this community (checked both before channel derivation,
    via `derive_reaction_channel`'s `NotFound`, and again at insert time via
    `ReactionEventInsertOutcome::TargetMissing`, which also covers a target
    soft-deleted between the two checks).
  - `"invalid: reaction emoji exceeds 64 characters (got N)"` — content over 64
    characters that is not a well-formed custom-emoji shortcode.
  - `"invalid: long custom emoji reaction shortcode must be canonical lowercase"`
    — a `:shortcode:` whose normalized form does not match the content exactly.
- **Versioning/compatibility.** The kind number (7) and the `e`-tag target
  reference are fixed by upstream NIP-25 itself and are not something Buzz
  versions independently. Buzz layers one additional convention on top — the
  NIP-30 custom-emoji shortcode format — enforced by `validate_reaction_emoji`;
  there is no other Buzz-specific reaction schema version to track.

## Boundary

This node does not describe:

- **`KIND_HUDDLE_REACTION` (24810).** This is a distinct, ephemeral,
  never-stored, channel-scoped huddle emoji-reaction burst
  (`crates/buzz-core/src/kind.rs`) — unrelated to NIP-25's persisted kind:7
  reaction, despite the similar name.
- **kind:7's own wire-level tag/content contract**, the way an event-kind node
  would describe it (kind number, tag shape, content semantics as the subject's
  primary identity). That is `events/kinds/kind-7-reaction.md`'s territory
  (issue #882). At this repository revision that node does not exist on
  `origin/launchpad` — it lives on an unmerged branch — so it is named here by
  filename only, per `AGENTS.md`'s rule that a `relationships` target must
  already resolve on the branch being merged into.
- **Field-by-field, domain-expert-depth cataloguing** of every `buzz reactions
  --help` flag — the reference/API-Reference-depth gap `#1346`/`#1532` describe
  as unresolved, not this template's job.
- **The upstream NIP-25 specification's own full text**, including any
  guidance beyond what `validate_reaction_emoji` implements. The spec document
  is the authority for the convention itself; this node cites the code that
  implements it, not a restatement of the spec.

## Relationships

- `implements`: `corpus-template-interface` — this node is an instance of the
  interface template.
- `references`: `architecture-flows-websocket-authentication` — the
  authentication path a reaction submission goes through is documented there,
  not restated here.
- `part-of`: `architecture-containers-relay` — the relay is the container that
  hosts every operation this node describes.

## Examples

**Valid.** Adding a plain reaction via the CLI:

```
buzz reactions add 3f1c...a9 "🎉"
```

builds and submits a kind:7 event with `content: "🎉"` and `tags: [["e",
"3f1c...a9"]]` (the target must be a real, non-deleted event id in this
community). A newly accepted reaction returns:

```json
{"event_id": "b7e2...d4", "accepted": true, "message": ""}
```

**Failure.** Submitting a kind:7 event with no target `e` tag (e.g. via `POST
/events` with `{"kind": 7, "content": "+", "tags": []}` correctly signed):
the ingest pipeline rejects it before any storage occurs, returning HTTP 400 /
WebSocket `OK false` with:

```json
{"accepted": false, "message": "invalid: reaction must reference a target event via e tag"}
```

## Scope and omissions

**This node covers** the NIP-25 reaction interface as Buzz implements it: adding,
removing and querying kind:7 reactions across the relay ingest pipeline,
`buzz-sdk`'s typed builders, and `buzz-cli`'s `reactions` subcommand group; the
authentication/authorization path a reaction submission uses; how channel scoping
is derived from the reaction's target rather than carried directly; the
dedup/idempotency guarantee one reaction per `(target, actor, emoji)` tuple; every
rejection message this pipeline can produce and its HTTP/WS surfacing; and the
NIP-09-based removal path.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| kind:7's own wire contract (tag shape, content semantics as primary subject) | `events/kinds/kind-7-reaction.md` (issue #882, unmerged at this revision) |
| Field-by-field CLI flag reference for `buzz reactions` | `#1346`/`#1532` (reference / API-Reference-depth gap, undecided) |
| The front-matter contract itself | `node.schema.json` |
| Creating, updating and retiring a node procedurally | `AGENTS.md` |

**Expected but not verified when this node was written:**

- **The upstream NIP-25 specification text itself was not fetched in this
  session.** The wire-shape claims above (content is emoji/`+`/`-`, `e` tag
  names the target, NIP-30 custom-emoji convention) are backed by this
  repository's own source doc comments, builder implementation, and tests, not
  by reading `nostr-protocol/nips/25.md` directly.
- **Whether other Nostr relay implementations treat `-` as a semantically
  distinct "dislike" reaction, surfaced differently to clients, was not
  checked.** Buzz's own ingest and query paths treat `+`, `-`, and any other
  emoji content uniformly as reaction content with no special-cased dislike
  handling.
- **The exact HTTP status code path was read from `IngestError`'s own doc
  comments, not from an end-to-end HTTP request/response capture** — the doc
  comments state the mapping (`Rejected` -> 400, `AuthFailed` -> 401/403,
  `Internal` -> 500) but this node does not independently confirm the router
  wires each variant to exactly that status at every call site.
