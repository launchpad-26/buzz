---
id: events-kinds-kind-9-stream-message
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
  - statement: "crates/buzz-core/src/kind.rs defines `pub const KIND_STREAM_MESSAGE: u32 = 9;` with a doc comment stating it is the 'NIP-29 group chat message kind' and documenting the agent-shutdown convention: 'the agent's owner sends a kind:9 message with content \"!shutdown\" and a #p tag mentioning the agent. The harness exits gracefully. This is a convention, not a new event kind — uses regular stream messages.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:474-479"
  - statement: "NIP-01 defines the regular-event kind range as `1000 <= n < 10000 || 4 <= n < 45 || n == 1 || n == 2`, all expected to be stored by relays; kind 9 falls in `4 <= n < 45`."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/01.md"
  - statement: "kind.rs's own classification helpers agree with that range for kind 9: `is_replaceable` matches only `0 | 3 | KIND_CHANNEL_METADATA | 10000..=19999`, `is_parameterized_replaceable` matches only `30000..=39999`, and `is_ephemeral` matches only `20000..=29999` — kind 9 (`KIND_STREAM_MESSAGE`) matches none of them, so Buzz's own code treats it as plain regular, consistent with NIP-01."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:768-786"
  - statement: "NIP-29 requires that 'Events sent by users to groups (chat messages, text notes, moderation events etc) MUST have an h tag with the value set to the group id,' but its own text does not designate any specific kind number for chat messages — it states groups 'may accept any event kind, including chats, threads, long-form articles, calendar, livestreams, market announcements and so on.' Buzz's characterization of kind 9 as 'the NIP-29 group chat message kind' (kind.rs's doc comment) is therefore Buzz's own convention layered on NIP-29's general h-tag rule, not a number NIP-29 itself mandates."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/29.md"
      - "crates/buzz-core/src/kind.rs:474"
  - statement: "`requires_h_channel_scope(kind)` in crates/buzz-relay/src/handlers/ingest.rs includes `KIND_STREAM_MESSAGE` in its match arm, and ingest rejects any such event with no resolvable channel id: 'invalid: channel-scoped events must include an h tag.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:704-733"
      - "crates/buzz-relay/src/handlers/ingest.rs:2460-2464"
  - statement: "`is_global_only_kind(kind)` in ingest.rs does not include `KIND_STREAM_MESSAGE` in its match arm, confirming kind 9 is genuinely channel-scoped rather than forced global despite any stray h tag."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:621-701"
  - statement: "`required_scope_for_kind` maps `KIND_STREAM_MESSAGE` (grouped with KIND_DELETION, KIND_REACTION, KIND_STREAM_MESSAGE_V2 and other stream-message variants) to `Scope::MessagesWrite`, the required auth scope for submitting the event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:470-484"
  - statement: "buzz_core::nip10::parse_thread_markers reads NIP-10 marker tags shaped `[\"e\", <64-hex-event-id>, <relay>, \"root\"]` and `[\"e\", <64-hex-event-id>, <relay>, \"reply\"]`; a malformed id in either position is rejected rather than silently accepted."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/nip10.rs:19-75"
  - statement: "For any kind where requires_h_channel_scope is true (including kind 9) and a channel id is resolved, ingest calls resolve_nip10_thread_meta, which resolves the parent event from the reply e-tag, requires the parent to belong to the same channel, requires the client-supplied root tag to match the ancestry actually stored in thread_metadata (or freshly derived from the parent's own tags), enforces a thread depth cap of 100, and reads an optional [\"broadcast\", \"1\"] tag; an event with no thread markers at all is accepted with no thread metadata (a top-level channel message)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2987-2997"
      - "crates/buzz-relay/src/handlers/ingest.rs:813-902"
  - statement: "For kind 9 specifically (and no other kind — the `if kind_u32 == KIND_STREAM_MESSAGE` guard is exact), ingest additionally calls validate_link_preview_tags, which permits zero or more [\"link-preview\", \"snapshot\", \"1\", <https-canonical-url>, <title>, <site>, <description>, <img-url>, <img-media>, <thumb-url>, <thumb-media>] tags (11 elements, capped at 8 per event, canonical URL must be https with no embedded credentials/fragment and must literally appear in the event content, title/site capped at 300/100 chars with no control characters, description capped at 1000 chars allowing newlines), or exactly one suppression tag [\"link-preview\", \"none\"] with no snapshot tags alongside it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2968-2971"
      - "crates/buzz-relay/src/handlers/ingest.rs:314-371"
  - statement: "Any event kind, including kind 9, that carries one or more [\"imeta\", ...] tags has them validated by validate_imeta_tags and their referenced blobs verified by verify_imeta_blobs before storage — this is a generic ingest step, not kind-9-specific gating."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:2973-2985"
  - statement: "KIND_STREAM_MESSAGE (9) is not a member of AUTHOR_ONLY_KINDS, RESULT_GATED_KINDS, P_GATED_KINDS, or SHARED_GATED_KINDS — the four named access-control sets in kind.rs. It therefore carries none of those kinds' special read restrictions: it is readable by any authenticated member of the channel it is scoped to (subject to ordinary channel-membership/visibility checks), not restricted to its author, a #p-tagged pubkey, or an opt-in 'shared' tag."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:129-133"
      - "crates/buzz-core/src/kind.rs:142"
      - "crates/buzz-core/src/kind.rs:159-169"
      - "crates/buzz-core/src/kind.rs:215"
  - statement: "The `events` table's generated `search_tsv` column is `NULL` only for kinds `1059, 30179, 30300, 30350, 30622, 44100, 44101, 44200`; kind 9 is not in that list, so a kind-9 event's `content` is indexed into `to_tsvector('simple', content)` and is reachable through NIP-50 full-text search like any other unrestricted kind."
    entry_class: FACT
    evidence:
      - "schema/schema.sql:203-227"
  - statement: "check_channel_membership (used for a channel-scoped write, including kind 9) allows the write if the requester is a cached channel member, or — for a non-member — if the channel's stored `visibility` is `\"open\"`; otherwise it returns 'restricted: not a channel member.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:742-772"
  - statement: "buzz-db's insert_thread_metadata (crates/buzz-db/src/store/thread.rs) increments the thread root's `reply_count` (and, per a second SQL statement in the same file, `last_reply_at`/further counters) whenever a reply event — including a kind-9 reply carrying NIP-10 root/reply e-tags — is inserted with resolved thread ancestry."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/thread.rs:214"
      - "crates/buzz-db/src/store/thread.rs:266"
  - statement: "After a thread mutation, crates/buzz-relay/src/handlers/side_effects.rs's emit_live_thread_summary re-reads the thread root's summary from thread_metadata (not an in-memory increment) and fans out a relay-signed, never-persisted kind:39005 overlay event carrying reply_count, descendant_count, last_reply_at and participants, tagged with the root's e/d ids and the channel's h tag; this is fan-out-only because channel-window pages recompute the same summary from thread_metadata on every fetch."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:806-859"
  - statement: "The relay itself authors and signs kind-9 events with its own keypair for moderation DM notices: moderation_notices.rs builds an EventBuilder with Kind::Custom(KIND_STREAM_MESSAGE as u16), tags [[\"h\", <dm_channel_id>], [\"moderation_source\", <source_id>]], signs with `state.relay_keypair`, and inserts it via the normal insert_event path before dispatching it as a persistent event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/moderation_notices.rs:152-183"
  - statement: "crates/buzz-relay/src/workflow_sink.rs constructs and tests events of `Kind::from(KIND_STREAM_MESSAGE as u16)` as workflow-engine output, including nested-reply and root-only-parent thread scenarios — the workflow engine is a second, non-human producer of kind-9 events alongside ordinary member clients and the relay's own moderation-notice path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/workflow_sink.rs:11"
      - "crates/buzz-relay/src/workflow_sink.rs:347-355"
      - "crates/buzz-relay/src/workflow_sink.rs:931-1036"
  - statement: "crates/buzz-relay/src/handlers/event.rs's enqueue_event_created_audit sends a `buzz_audit::AuditAction::EventCreated` entry (detail JSON carries `event_kind` and `channel_id`, actor is the resolved authenticated/triggering principal rather than always the event's signing pubkey) to the per-community hash-chain audit log for every persistently stored event kind that reaches dispatch_persistent_event's two call sites — kind 9 is not special-cased out of this, so a kind-9 stream message generates a generic EventCreated audit entry like any other stored kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs:358"
      - "crates/buzz-relay/src/handlers/event.rs:509"
      - "crates/buzz-relay/src/handlers/event.rs:563-599"
  - statement: "Kind 9 and kind 40002 (KIND_STREAM_MESSAGE_V2) both currently appear, side by side, in kind.rs's ALL_KINDS registry, both require an h tag (requires_h_channel_scope), both map to Scope::MessagesWrite, and no comment on either constant, nor any code path found in ingest.rs, marks kind 9 as deprecated, retired, or rejected in favor of kind 40002 — the two are live, coexisting kinds as of this revision, not a legacy kind superseded by a replacement."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:479-481"
      - "crates/buzz-core/src/kind.rs:700-712"
      - "crates/buzz-relay/src/handlers/ingest.rs:470-484"
      - "crates/buzz-relay/src/handlers/ingest.rs:704-715"
  - statement: "kind.rs's doc comment on KIND_STREAM_MESSAGE_V2 ('V1 used kind:10002 (replaceable range — wrong), then 40002') describes that constant's own prior wrong-range numbering attempts before it settled on 40002 — it is not a statement that kind 9 was ever renumbered to, or superseded by, kind 40002. No search of this repository turned up such a claim; the coexistence of kind 9 and kind 40002 as two independently maintained kinds is read from the code as it stands, not explained by any found history."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/kind.rs:479-481"
    confidence: 0.7
  - statement: "No file under docs/nips/ discusses kind 9 or KIND_STREAM_MESSAGE by name (checked by listing docs/nips/*.md and grepping each for 'kind 9'/'kind:9' literal text, zero matches) — kind 9 has no Buzz-authored custom-NIP proposal document; its governing specification is the external NIP-01 (event envelope, regular-kind range) plus NIP-29 (h-tag group-scoping convention), read directly above, with Buzz's own kind.rs comment supplying the kind-to-convention mapping neither NIP states."
    entry_class: FACT
    evidence:
      - "shell(ls docs/nips/*.md; grep -l 'kind 9\\|kind:9' docs/nips/*.md) -> zero files matched"
  - statement: "Issue #883's Definition of done requires stating the kind number/name and persistent/replaceable/ephemeral classification; defining required/optional tags/content and validation rules; naming producers, consumers, authorization, persistence/fanout/search/audit treatment; and linking the NIP/spec, handler/registry and conformance/tests."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#883 definition of done"
  - statement: "Kind 40002 (KIND_STREAM_MESSAGE_V2) has its own corpus node under active authorship on branch task/877-events-kinds-kind-40002-stream-message-v2 (issue #877), unmerged as of this revision — its wire contract is that node's subject, not restated here, and it is not cited as a `relationships` target because the branch it lives on is not the merge target this validator run resolves against."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#877 (sibling task, unmerged branch, named in this task's own dispatch)"
---

# Event kind 9 — stream message

The original Buzz channel chat-message event kind: a regular (non-replaceable,
non-ephemeral) Nostr event, scoped to one NIP-29 group/channel via an `h` tag,
carrying a member's or the relay's plaintext chat content. It coexists today
with kind 40002 (`KIND_STREAM_MESSAGE_V2`, documented separately — see
*Relationship to kind 40002* below) rather than being superseded by it.

## Kind identity

| | |
|---|---|
| Kind number | `9` |
| Constant | `KIND_STREAM_MESSAGE` in `crates/buzz-core/src/kind.rs` |
| Corpus type | `interfaces-events` |
| Delivery classification | Regular (stored, non-replaceable) |
| Status | Implemented and actively used today |

## Referenced specification

- **NIP-01** (`nostr-protocol/nips`, `01.md`, pinned at commit
  `dabfcb2aaecf4fa374eda8b1232ab303a03f60ba`) is the primary source for the
  event envelope and the regular-kind range `4 <= n < 45` that kind 9 falls
  inside.
- **NIP-29** (same repository, `29.md`, same pin) is the source for the `h`-tag
  channel-scoping requirement Buzz applies to kind 9. NIP-29's own text does
  **not** designate kind 9 (or any specific kind) as the group chat message —
  it permits groups to "accept any event kind." The "kind 9 = chat message"
  mapping is Buzz's own convention, stated in `kind.rs`'s doc comment, layered
  on top of NIP-29's general `h`-tag rule.
- No Buzz-authored `docs/nips/NIP-XX.md` proposal exists for kind 9 — it needs
  none, because both governing rules (the envelope range, the scoping tag) are
  fully specified by the two NIPs above; Buzz's only addition is the
  kind-to-convention mapping recorded in `kind.rs`.

## Kind range and delivery classification

Kind 9 sits in NIP-01's regular range (`4 <= n < 45`). Buzz's own classifier
functions agree: `is_replaceable(9)`, `is_parameterized_replaceable(9)`, and
`is_ephemeral(9)` are all `false` — kind 9 is a plain regular, stored,
non-replaceable event, matching NIP-01's own classification with no drift
between the spec and the code.

## Tag shape

| Tag | Cardinality | Purpose |
|---|---|---|
| `h` | **Exactly one, required** | NIP-29 group/channel id. `requires_h_channel_scope` includes kind 9; an event of this kind with no resolvable `h` tag is rejected at ingest with `invalid: channel-scoped events must include an h tag`. |
| `e` (NIP-10 marker) | Zero, or a `root`/`reply` pair | `["e", <64-hex-event-id>, <relay>, "root"]` and `["e", <64-hex-event-id>, <relay>, "reply"]`. When present, ingest resolves and validates full thread ancestry (parent must exist in the same channel, the client's claimed root must match server-side ancestry, depth capped at 100). Absent entirely, the message is a top-level channel post with no thread metadata. |
| `broadcast` | Zero or one | `["broadcast", "1"]` — read by `resolve_nip10_thread_meta` alongside thread resolution; carried through to stored `ThreadMetadataOwned.broadcast`. |
| `p` | Zero or more | No kind-9-specific cardinality rule was found; used by convention for the agent-shutdown case below (mentioning the target agent). |
| `link-preview` | Zero or more, **kind-9-specific validation** | Either zero-or-more `["link-preview", "snapshot", "1", <https-canonical-url>, <title>, <site>, <description>, <img-url>, <img-media>, <thumb-url>, <thumb-media>]` tags (max 8 per event; canonical URL must be `https`, carry no credentials or fragment, and literally appear in `content`; title ≤300 chars, site ≤100 chars, description ≤1000 chars allowing newlines, none may contain other control characters), or exactly one suppression tag `["link-preview", "none"]` with no snapshot tags alongside it. This validation (`validate_link_preview_tags`) runs only for kind 9 — no other kind is gated by it. |
| `imeta` | Zero or more | Generic ingest-wide validation (`validate_imeta_tags` + `verify_imeta_blobs`) applies identically to every kind that carries one; not kind-9-specific. |

## Content field semantics

Plaintext. No structured JSON envelope is enforced for kind 9's `content` at
ingest (contrast kind 0's `content` being pre-validated as JSON). One
documented convention exists: the agent-shutdown message, where the event's
owner publishes a kind-9 event with `content` exactly `"!shutdown"` and a `#p`
tag mentioning the target agent; the agent harness treats this as a graceful
shutdown signal. `kind.rs`'s own comment is explicit that this is "a
convention, not a new event kind — uses regular stream messages," so no
different validation path exists for it.

## Access control and storage model

- **Not a member of any of the four named access-control sets** in `kind.rs`
  (`AUTHOR_ONLY_KINDS`, `RESULT_GATED_KINDS`, `P_GATED_KINDS`,
  `SHARED_GATED_KINDS`). A kind-9 event is readable by any authenticated member
  of the channel it is scoped to (or any reader, for a channel whose stored
  `visibility` is `"open"`, via `check_channel_membership`'s
  member-OR-open-visibility check) — the community/channel boundary is the
  only gate, not a per-kind privacy rule.
- **Required auth scope**: `Scope::MessagesWrite`, via `required_scope_for_kind`.
- **Channel-scoped, not global**: `is_global_only_kind(9)` is `false`; a stray
  `h` tag is not stripped or ignored the way it is for genuinely global kinds.
- **Full-text searchable**: kind 9 is not among the kinds whose `search_tsv`
  column is forced `NULL` (`1059, 30179, 30300, 30350, 30622, 44100, 44101,
  44200`), so its content is indexed into Postgres FTS (`to_tsvector('simple',
  content)`) and reachable through NIP-50 `search` filters like any other
  unrestricted kind.
- **Thread counters**: a reply carrying resolved NIP-10 ancestry causes
  `insert_thread_metadata` to increment the thread root's `reply_count` (and
  related counters/timestamps) in the same transaction as the insert. A
  separate, fan-out-only side effect (`emit_live_thread_summary`) then
  re-reads the root's summary from `thread_metadata` and publishes a
  relay-signed, never-persisted kind:39005 overlay event so subscribed clients
  can update badge counts without refetching — this overlay is a live
  broadcast, not a second source of truth; channel-window pages recompute the
  same summary from `thread_metadata` directly.
- **Audit**: every persistently stored event, kind 9 included, generates a
  generic `AuditAction::EventCreated` entry in the per-community hash-chain
  audit log (`buzz-audit`), carrying the event's kind and channel id in its
  detail JSON and the resolved acting principal (not necessarily the event's
  signing pubkey — see *Producers* below) as actor. This is a kind-agnostic
  audit path, not kind-9-specific instrumentation.

## Producers

- **Ordinary community members**, via any client that submits a kind-9 event
  through the normal ingest path (WebSocket or `POST /events`), subject to
  `Scope::MessagesWrite` and channel-membership/open-visibility checks.
- **The relay itself**, for moderation DM notices: `moderation_notices.rs`
  constructs a kind-9 `EventBuilder`, signs it with the relay's own keypair,
  tags it `["h", <dm_channel_id>]` and `["moderation_source", <source_id>]`,
  and inserts it through the same `insert_event` path used for client events.
  For audit purposes, the resolved actor recorded is the human/triggering
  principal, not the relay's own signing pubkey.
- **The workflow engine** (`buzz-workflow`), via `crates/buzz-relay/src/
  workflow_sink.rs`, which builds kind-9 events (including nested-reply and
  root-only-parent thread shapes) as workflow output posted into a channel.

## Consumers

- **Any client subscribed to the channel** the event is scoped to (`h` tag),
  via the relay's live fan-out path, and any client issuing a historical
  `REQ`/`POST /query` filter that matches the kind and channel/thread.
- **`buzz-cli`**'s `messages` subcommands (e.g. `messages thread`) read stored
  kind-9 events as part of the normalized event-read surface described in this
  repository's root `AGENTS.md`; this node does not restate that CLI contract
  — it belongs to an interface-scoped corpus node, not this event-kind node
  (see *Scope and omissions*).
- **NIP-50 full-text search** (`buzz-search`), since kind 9's content is FTS
  indexed.
- **The per-community audit log** (`buzz-audit`), via the generic
  `EventCreated` entry described above.

## Worked example

A top-level channel message with a suppressed link preview:

```json
{
  "id": "…",
  "pubkey": "…",
  "created_at": 1735689600,
  "kind": 9,
  "tags": [
    ["h", "3fae2c1a-9b7e-4d3a-8c1f-6e2b9a0d4f11"],
    ["link-preview", "none"]
  ],
  "content": "Standup notes are in the canvas, no link this time.",
  "sig": "..."
}
```

A threaded reply carrying a link-preview snapshot:

```json
{
  "id": "…",
  "pubkey": "…",
  "created_at": 1735689700,
  "kind": 9,
  "tags": [
    ["h", "3fae2c1a-9b7e-4d3a-8c1f-6e2b9a0d4f11"],
    ["e", "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2", "", "root"],
    ["e", "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b3", "", "reply"],
    ["link-preview", "snapshot", "1", "https://example.com/post", "Example Post", "example.com", "A short description.", "https://media.example.com/img/abc.png", "image/png", "", ""]
  ],
  "content": "See https://example.com/post — matches the earlier discussion.",
  "sig": "..."
}
```

The agent-shutdown convention, unthreaded and channel-scoped like any other
kind-9 event:

```json
{
  "id": "…",
  "pubkey": "…",
  "created_at": 1735689800,
  "kind": 9,
  "tags": [
    ["h", "3fae2c1a-9b7e-4d3a-8c1f-6e2b9a0d4f11"],
    ["p", "7c2e1a9b4f3d8c6e2b9a0d4f117c2e1a9b4f3d8c6e2b9a0d4f117c2e1a9b4f3d"]
  ],
  "content": "!shutdown",
  "sig": "..."
}
```

## Relationship to kind 40002

Kind 40002 (`KIND_STREAM_MESSAGE_V2`) is a separate, later-numbered kind that
also requires an `h` tag and also maps to `Scope::MessagesWrite`. Both appear
side by side in `kind.rs`'s kind registry today, and nothing found in this
repository — no code path, no doc comment on either constant — marks kind 9 as
deprecated or rejected in favor of kind 40002. `kind.rs`'s own comment on
`KIND_STREAM_MESSAGE_V2` ("V1 used kind:10002 (replaceable range — wrong),
then 40002") describes *that* constant's own prior wrong-range numbering
history, not a migration away from kind 9. This node therefore reports the two
as coexisting kinds, not an original/superseded pair — with medium-high
confidence, since no explanation of *why* both exist was found (see *Scope and
omissions*).

Kind 40002's own wire contract — its tag shape, content semantics and
access-control model — is documented in a separate corpus node
(`events-kinds-kind-40002-stream-message-v2`, issue #877), authored on an
unmerged sibling branch at the time this node was written. No `relationships`
edge is declared to it here: that id does not resolve against this repository
branch's actual merge target (`origin/launchpad`), and a target that only
resolves on a branch other than the one being merged into is exactly the
trap `AGENTS.md`'s *Creating a node* step 9 warns against. Once kind 40002's
node merges, a `references` edge between the two would be a reasonable
follow-up.

## Scope and omissions

**This node covers** kind 9's identity, governing specification, range
classification, tag shape, content semantics, access-control/storage
treatment, producers, consumers, and its current coexistence with kind 40002.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Kind 40002's own wire contract | `events-kinds-kind-40002-stream-message-v2` (issue #877, unmerged at this revision) |
| The `buzz-cli` `messages` subcommand surface that reads/posts kind-9 events | An interface-scoped corpus node (per `templates/event-kind.md`'s boundary against the interface template), not authored here |
| Why kind 9 and kind 40002 coexist as two independently maintained kinds, rather than one having superseded the other | Not settled by any source found while authoring this node — reported above as an inference, not a fact |
| Kind:39005 (thread-summary overlay) and kind:40099 (`KIND_SYSTEM_MESSAGE`, channel state-change notices) as event kinds in their own right | Their own corpus event-kind nodes, not yet authored |
| Conformance/tests beyond the specific ingest.rs unit tests cited above (e.g. any dedicated integration test for kind-9 thread depth limits or link-preview edge cases beyond what this node's evidence cites) | Not exhaustively enumerated here — the `crates/buzz-relay/src/handlers/ingest.rs` test module (`mod tests`) is the closest map, but this node did not read every test in it |

**No `relationships` in this node's front matter**, for the same reason
`events-kinds-kind-40002-stream-message-v2` cannot be cited: at the time of
authoring, `origin/launchpad`'s `launchpad/docs/corpus` tree carries no other
event-kind node, and the only candidate sibling (kind 40002's node) lives on an
unmerged branch and does not resolve against the actual merge target.

**Expected but not verified when this node was written:**

- **Why kind 9 and kind 40002 coexist** — no PR, issue, or code comment
  explaining the design decision was found; this is stated as an open
  question, not resolved by inference beyond what the code shows.
- **Whether every `ingest.rs` unit test touching `KIND_STREAM_MESSAGE` was
  read.** A representative sample (link-preview suppression/snapshot cases)
  was opened to confirm the tag-shape claims above; the full test module was
  not read line by line.
- **Whether any operator-facing tool queries `buzz-audit`'s `EventCreated`
  entries per kind** — the generic audit path was confirmed to fire for kind
  9, but no consumer of that specific audit data was found or checked.
