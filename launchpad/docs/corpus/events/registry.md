---
id: events-registry
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
  - statement: "crates/buzz-core/src/kind.rs states in its own module doc comment that it 'is the authoritative source for Buzz kind numbers,' and that every constant is u32 because 'NIP-01 specifies kind as an unsigned integer, and u32 covers the full range without truncation.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs defines a pub const ALL_KINDS: &[u32] array containing exactly 130 distinct kind constants, described in its own doc comment as 'All registered kind constants — used for duplicate detection and iteration.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs defines exactly three additional kind constants that are NOT members of the ALL_KINDS array: KIND_AUTH = 22242 (doc comment: 'NIP-42 auth event — never stored'), KIND_NOSTR_IDENTITY_BINDING = 24243 (doc comment: 'Buzz custom one-time identity binding proof (ephemeral, not stored)'), and KIND_PUSH_LEASE = 30350 (doc comment: 'NIP-PL: encrypted push lease ... The source event contains endpoint-bearing NIP-44 ciphertext and is readable only by its authenticated author'). All three are excluded from ALL_KINDS while still being defined, referenced-elsewhere constants; KIND_PUSH_LEASE is additionally a member of AUTHOR_ONLY_KINDS despite this exclusion. This was found by mechanically diffing every `pub const NAME: u32 = N` declaration in the file against the ALL_KINDS array body, not assumed from the array's own doc comment."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's no_duplicate_kind_values unit test asserts every value in ALL_KINDS is unique, by inserting each into a HashSet and asserting every insert succeeds."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's is_replaceable function returns true exactly for kind 0, kind 3, KIND_CHANNEL_METADATA (41), and the range 10000..=19999 (NIP-01's replaceable range); is_parameterized_replaceable returns true exactly for the range 30000..=39999 (NIP-33); is_ephemeral returns true exactly for the range 20000..=29999. All other kind values are classified 'regular' by this document, since kind.rs defines no fourth helper naming that category explicitly."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs defines four named access-control sets over kind values: AUTHOR_ONLY_KINDS = [KIND_EVENT_REMINDER, KIND_PUSH_LEASE, KIND_PRIVATE_MANAGED_AGENT]; P_GATED_KINDS = [KIND_AGENT_OBSERVER_FRAME, KIND_MEMBER_ADDED_NOTIFICATION, KIND_MEMBER_REMOVED_NOTIFICATION, KIND_GIFT_WRAP, KIND_DM_VISIBILITY, KIND_AGENT_TURN_METRIC]; SHARED_GATED_KINDS = [KIND_PERSONA, KIND_TEAM_CATALOG]; RESULT_GATED_KINDS = [KIND_DM_VISIBILITY, KIND_AGENT_TURN_METRIC]. Membership was extracted directly from each array's literal body, with source-code comments stripped programmatically before parsing to avoid mis-parsing an inline comment as a member."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs defines five additional boolean-returning classification helpers over specific kind subsets, each backed by a literal matches!(...) list rather than a range: is_relay_only_kind (KIND_NIP43_MEMBERSHIP_LIST, KIND_CHANNEL_SUMMARY, KIND_PRESENCE_SNAPSHOT, KIND_DM_VISIBILITY, KIND_THREAD_SUMMARY, KIND_WINDOW_BOUNDS); is_command_kind (KIND_WORKFLOW_DEF, KIND_DM_OPEN, KIND_DM_ADD_MEMBER, KIND_DM_HIDE, KIND_WORKFLOW_TRIGGER, KIND_APPROVAL_GRANT, KIND_APPROVAL_DENY); is_moderation_command_kind (KIND_MODERATION_BAN, KIND_MODERATION_UNBAN, KIND_MODERATION_TIMEOUT, KIND_MODERATION_UNTIMEOUT, KIND_MODERATION_RESOLVE_REPORT); is_relay_admin_kind (RELAY_ADMIN_ADD_MEMBER, RELAY_ADMIN_REMOVE_MEMBER, RELAY_ADMIN_CHANGE_ROLE, RELAY_ADMIN_SET_WORKSPACE_PROFILE); and is_identity_archive_request_kind (KIND_IA_ARCHIVE_REQUEST, KIND_IA_UNARCHIVE_REQUEST). A sixth, is_workflow_execution_kind, is a range check (KIND_WORKFLOW_TRIGGERED..=KIND_WORKFLOW_APPROVAL_DENIED, i.e. 46001..=46012) rather than a literal list."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "At the recorded revision, no file matching kind-*.md exists anywhere under launchpad/docs/corpus, so no per-kind instance corpus node exists yet for this registry to link to."
    entry_class: FACT
    evidence:
      - "find(path='launchpad/docs/corpus', name='kind-*.md') -> no output, run at commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "node.schema.json's type enum contains interfaces-events as the dedicated value for the corpus's combined interface/event surface, and the merged corpus-template-event-kind node states that 'a real corpus node instance authored from this template -- documenting one actual Buzz event kind -- would most plausibly take node.schema.json's interfaces-events type, since that is the enum's own dedicated value for the corpus's protocol/interface surface.'"
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/event-kind.md"
  - statement: "This registry node, documenting the full set of registered event kinds rather than one instance, takes the same interfaces-events surface value the event-kind template reasons a single-kind instance node would take, since both describe the same corpus surface (the protocol/interface layer) at different granularities."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/event-kind.md"
    confidence: 0.75
  - statement: "Issue #885's Definition of Done requires this node to be structured for lookup rather than narrative teaching, contain only facts supported by current source, label generated versus authored values, define scope and omissions explicitly, and link the authoritative source (crates/buzz-core/src/kind.rs)."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#885 definition of done"
  - statement: "Parent Feature #616 states this task's objective as creating launchpad/docs/corpus/events/registry.md as the single canonical reference node for the event kind registry."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#885, Parent PRD #616"
---

# Event kind registry: reference

This node catalogues every Nostr `kind` integer Buzz's relay currently registers or
defines, as a single lookup table keyed by kind number. It exists so that a reader —
human or agent — who needs to know what a given `kind` value means, which range it
falls in, and whether it carries any special access-control gating can answer that in
one place, without opening `crates/buzz-core/src/kind.rs` and re-deriving the answer
from its constants, doc comments and helper functions by hand. This node does not
replace `kind.rs` — it is a hand-authored transcription of it, checked against it at
one revision, and it is `kind.rs` itself that governs at runtime. Where a per-kind
instance node (a `kind-*.md` document under this same `events/` directory, following
`corpus-template-event-kind`) exists for one of the rows below, this table would link
to it in the *Corpus node* column; none exist yet, so that column is omitted from the
table entirely below rather than populated with placeholder dashes.

**Ordering.** The table below is sorted by kind number ascending — the natural order
for a reader doing numeric lookup (`what is kind 30622?`) — rather than by `kind.rs`'s
own declaration order, which groups constants topically (standard NIP kinds, Buzz
command kinds, moderation commands, workflow engine, and so on) rather than
numerically. A reader who wants the topical grouping should read `kind.rs` directly;
this table optimizes for the lookup case its own `id` names.

## Registry

**Columns.** *Kind* is the literal `u32` value. *Constant* is the exact name of the
`pub const` in `crates/buzz-core/src/kind.rs` (some historical/administrative
constants are named `RELAY_ADMIN_*` rather than `KIND_*`; both are real registered
values). *Delivery* is one of `regular`, `replaceable`, `param-replaceable`
(NIP-33 parameterized-replaceable, 30000–39999), or `ephemeral` (20000–29999), computed
directly from `kind.rs`'s own `is_replaceable` / `is_parameterized_replaceable` /
`is_ephemeral` helpers rather than re-derived from the NIP-01 ranges independently — a
value that is `param-replaceable` by range but that helper's own doc comment notes
uses a different replacement key (including the `d` tag) than plain `replaceable`.
*Access notes* flags membership in `kind.rs`'s four read-visibility sets
(`author-only` = `AUTHOR_ONLY_KINDS`, `p-gated` = `P_GATED_KINDS`, `shared-gated` =
`SHARED_GATED_KINDS`, `result-gated` = `RESULT_GATED_KINDS`) and one negative fact
(`not in ALL_KINDS`, for the three constants noted above). An empty *Access notes*
cell means the kind is not a member of any of those four sets — it does not mean no
access control applies to it at all; see *Scope and omissions* below. *Purpose* is
the kind's own doc comment in `kind.rs`, truncated to its first sentence where the
comment ran longer; the full comment in `kind.rs` is authoritative if this table's
truncation ever looks incomplete.

| Kind | Constant | Delivery | Access notes | Purpose |
|---|---|---|---|---|
| 0 | `KIND_PROFILE` | replaceable |  | NIP-01: User profile metadata. |
| 1 | `KIND_TEXT_NOTE` | regular |  | NIP-01: Short text note. |
| 3 | `KIND_CONTACT_LIST` | replaceable |  | NIP-02: Contact list / follow list. |
| 5 | `KIND_DELETION` | regular |  | NIP-09: Event deletion request. |
| 7 | `KIND_REACTION` | regular |  | NIP-25: Content is emoji char or `+`/`-`. |
| 9 | `KIND_STREAM_MESSAGE` | regular |  | NIP-29 group chat message kind. |
| 41 | `KIND_CHANNEL_METADATA` | replaceable |  | NIP-01: Channel metadata (replaceable). Not used by Buzz today. |
| 1059 | `KIND_GIFT_WRAP` | regular | p-gated | NIP-17: Outer envelope for private DMs — hides sender, content, timestamp. |
| 1063 | `KIND_FILE_METADATA` | regular |  | NIP-94: File metadata attachment. |
| 1617 | `KIND_GIT_PATCH` | regular |  | NIP-34: Patch (git format-patch output). |
| 1618 | `KIND_GIT_PULL_REQUEST` | regular |  | NIP-34: Pull request. |
| 1619 | `KIND_GIT_PR_UPDATE` | regular |  | NIP-34: Pull request update (tip commit change). |
| 1621 | `KIND_GIT_ISSUE` | regular |  | NIP-34: Issue. |
| 1630 | `KIND_GIT_STATUS_OPEN` | regular |  | NIP-34: Status — Open. |
| 1631 | `KIND_GIT_STATUS_MERGED` | regular |  | NIP-34: Status — Applied / Merged. |
| 1632 | `KIND_GIT_STATUS_CLOSED` | regular |  | NIP-34: Status — Closed. |
| 1633 | `KIND_GIT_STATUS_DRAFT` | regular |  | NIP-34: Status — Draft. |
| 1984 | `KIND_REPORT` | regular |  | NIP-56: Report an event, pubkey, or blob to relay moderators (kind:1984). |
| 8000 | `KIND_NIP43_MEMBER_ADDED` | regular |  | NIP-43: Member added announcement (relay-signed). |
| 8001 | `KIND_NIP43_MEMBER_REMOVED` | regular |  | NIP-43: Member removed announcement (relay-signed). |
| 8002 | `KIND_IA_ARCHIVED` | regular |  | NIP-IA: Archived-identity delta (relay-signed). |
| 8003 | `KIND_IA_UNARCHIVED` | regular |  | NIP-IA: Unarchived-identity delta (relay-signed). |
| 9000 | `KIND_NIP29_PUT_USER` | regular |  | NIP-29: Add a user to a group. |
| 9001 | `KIND_NIP29_REMOVE_USER` | regular |  | NIP-29: Remove a user from a group. |
| 9002 | `KIND_NIP29_EDIT_METADATA` | regular |  | NIP-29: Edit group metadata. |
| 9005 | `KIND_NIP29_DELETE_EVENT` | regular |  | NIP-29: Delete an event from a group. |
| 9007 | `KIND_NIP29_CREATE_GROUP` | regular |  | NIP-29: Create a new group. |
| 9008 | `KIND_NIP29_DELETE_GROUP` | regular |  | NIP-29: Delete a group. |
| 9009 | `KIND_NIP29_CREATE_INVITE` | regular |  | NIP-29: Create an invite to a group. |
| 9021 | `KIND_NIP29_JOIN_REQUEST` | regular |  | NIP-29: Request to join a group. |
| 9022 | `KIND_NIP29_LEAVE_REQUEST` | regular |  | NIP-29: Request to leave a group. |
| 9030 | `RELAY_ADMIN_ADD_MEMBER` | regular |  | NIP-43: Add a pubkey to the relay member list. |
| 9031 | `RELAY_ADMIN_REMOVE_MEMBER` | regular |  | NIP-43: Remove a pubkey from the relay member list. |
| 9032 | `RELAY_ADMIN_CHANGE_ROLE` | regular |  | NIP-43: Change the role of an existing relay member. |
| 9033 | `RELAY_ADMIN_SET_WORKSPACE_PROFILE` | regular |  | Buzz: Set the workspace profile (icon). Admin/owner-signed command. |
| 9035 | `KIND_IA_ARCHIVE_REQUEST` | regular |  | NIP-IA: Request that the relay archive a target identity. |
| 9036 | `KIND_IA_UNARCHIVE_REQUEST` | regular |  | NIP-IA: Request that the relay unarchive a target identity. |
| 9040 | `KIND_MODERATION_BAN` | regular |  | Moderation: ban a pubkey from the community (`p` tag target, optional `expiration` + `reason` tags). |
| 9041 | `KIND_MODERATION_UNBAN` | regular |  | Moderation: lift a community ban (`p` tag target). |
| 9042 | `KIND_MODERATION_TIMEOUT` | regular |  | Moderation: timeout (write-block) a pubkey until an `expiration` tag timestamp (`p` tag target, optional `reason`). |
| 9043 | `KIND_MODERATION_UNTIMEOUT` | regular |  | Moderation: clear a timeout early (`p` tag target). |
| 9044 | `KIND_MODERATION_RESOLVE_REPORT` | regular |  | Moderation: resolve a report (`report` tag = report event id hex, `status` tag = resolved\|dismissed, `action` tag = delete\|kick\|ban\|timeout\|dismiss\|escalate — see `handlers/moderation_commands.rs` for the pinned vocabulary). |
| 10000 | `KIND_MUTE_LIST` | replaceable |  | NIP-51: Mute list (replaceable, 10000–19999 range) — pubkeys/events/threads/words a user has muted. |
| 10001 | `KIND_PIN_LIST` | replaceable |  | NIP-51: Pin list (replaceable) — events the user has pinned to their profile. |
| 10002 | `KIND_NIP65_RELAY_LIST_METADATA` | replaceable |  | NIP-65: Relay list metadata (replaceable) — read/write relay preferences for the outbox model. |
| 10003 | `KIND_BOOKMARK_LIST` | replaceable |  | NIP-51: Bookmark list (replaceable) — events/articles/hashtags/URLs the user has bookmarked. |
| 10030 | `KIND_EMOJI_LIST` | replaceable |  | NIP-51: Emoji list (replaceable) — user preferred emojis and pointers to emoji sets. |
| 10100 | `KIND_AGENT_PROFILE` | replaceable |  | Agent metadata + owner reference (replaceable, agent-authored). |
| 13534 | `KIND_NIP43_MEMBERSHIP_LIST` | replaceable |  | NIP-43: Relay membership list snapshot (relay-signed, replaceable by convention). |
| 13535 | `KIND_IA_ARCHIVED_LIST` | replaceable |  | NIP-IA: Archived identities list snapshot (relay-signed, replaceable). |
| 20001 | `KIND_PRESENCE_UPDATE` | ephemeral |  | Ephemeral: user presence update (online/away/offline). |
| 20002 | `KIND_TYPING_INDICATOR` | ephemeral |  | Ephemeral: typing indicator for a channel. |
| 22242 | `KIND_AUTH` | ephemeral | not in ALL_KINDS | NIP-42 auth event — never stored (carries bearer tokens). |
| 24134 | `KIND_PAIRING` | ephemeral |  | NIP-AB: Device pairing event. Ephemeral — relay may discard after delivery. |
| 24200 | `KIND_AGENT_OBSERVER_FRAME` | ephemeral | p-gated | Ephemeral: owner-scoped encrypted agent observer telemetry and control frame. |
| 24242 | `KIND_BLOSSOM_AUTH` | ephemeral |  | BUD-01: Blossom upload auth (used in upload.rs, not stored). |
| 24243 | `KIND_NOSTR_IDENTITY_BINDING` | ephemeral | not in ALL_KINDS | Buzz custom one-time identity binding proof (ephemeral, not stored). |
| 24810 | `KIND_HUDDLE_REACTION` | ephemeral |  | Ephemeral: huddle emoji reaction burst. Channel-scoped to the ephemeral huddle channel with an `h` tag; never stored in the timeline. |
| 27235 | `KIND_HTTP_AUTH` | ephemeral |  | NIP-98: HTTP auth event (used in nip98.rs, not stored). |
| 28936 | `KIND_NIP43_LEAVE_REQUEST` | ephemeral |  | NIP-43: User leave request (user-signed, ephemeral). |
| 30000 | `KIND_FOLLOW_SET` | param-replaceable |  | NIP-51: Follow set (parameterized replaceable, 30000–39999 range) — named curated lists of pubkeys. |
| 30003 | `KIND_BOOKMARK_SET` | param-replaceable |  | NIP-51: Bookmark set (parameterized replaceable) — named curated bookmark collections. |
| 30023 | `KIND_LONG_FORM` | param-replaceable |  | NIP-23: Long-form content (articles, blog posts, RFCs). |
| 30030 | `KIND_EMOJI_SET` | param-replaceable |  | NIP-51 / NIP-30: Emoji set (parameterized replaceable). |
| 30078 | `KIND_READ_STATE` | param-replaceable |  | NIP-78 / NIP-RS: Per-client read state blob for cross-device read position sync. |
| 30174 | `KIND_AGENT_ENGRAM` | param-replaceable |  | NIP-AE: Agent Engram (parameterized replaceable, agent-authored). |
| 30175 | `KIND_PERSONA` | param-replaceable | shared-gated | NIP-AP: Agent Persona (parameterized replaceable, owner-authored). |
| 30176 | `KIND_TEAM` | param-replaceable |  | NIP-AP: Agent Team (parameterized replaceable, owner-authored). |
| 30177 | `KIND_MANAGED_AGENT` | param-replaceable |  | NIP-AP: Managed Agent (parameterized replaceable, owner-authored). |
| 30178 | `KIND_TEAM_CATALOG` | param-replaceable | shared-gated | NIP-AP: Team Catalog projection (parameterized replaceable, owner-authored). |
| 30179 | `KIND_PRIVATE_MANAGED_AGENT` | param-replaceable | author-only | NIP-PMA: owner-encrypted private managed-agent aggregate. |
| 30300 | `KIND_EVENT_REMINDER` | param-replaceable | author-only | NIP-ER: Event Reminder (parameterized replaceable, author-only). |
| 30315 | `KIND_USER_STATUS` | param-replaceable |  | NIP-38: User status (general, music, or custom d-tag). |
| 30350 | `KIND_PUSH_LEASE` | param-replaceable | not in ALL_KINDS, author-only | NIP-PL: encrypted push lease (parameterized replaceable, author-only). |
| 30617 | `KIND_GIT_REPO_ANNOUNCEMENT` | param-replaceable |  | NIP-34: Repository announcement (parameterized replaceable, d-tag = repo-id). |
| 30618 | `KIND_GIT_REPO_STATE` | param-replaceable |  | NIP-34: Repository state — current branch/tag refs (parameterized replaceable, d-tag = repo-id). |
| 30620 | `KIND_WORKFLOW_DEF` | param-replaceable |  | Workflow definition (parameterized replaceable, d=workflow_uuid). |
| 30621 | `KIND_PROJECT` | param-replaceable |  | NIP-MP: Multi-repo project — a named grouping of `kind:30617` repository announcements (parameterized replaceable, d=project slug). |
| 30622 | `KIND_DM_VISIBILITY` | param-replaceable | p-gated, result-gated | NIP-DV: per-viewer DM visibility snapshot (relay-signed, parameterized replaceable, d=viewer_pubkey). |
| 39000 | `KIND_NIP29_GROUP_METADATA` | param-replaceable |  | NIP-29: Addressable group metadata state. |
| 39001 | `KIND_NIP29_GROUP_ADMINS` | param-replaceable |  | NIP-29: Addressable group admins list. |
| 39002 | `KIND_NIP29_GROUP_MEMBERS` | param-replaceable |  | NIP-29: Addressable group members list. |
| 39003 | `KIND_NIP29_GROUP_ROLES` | param-replaceable |  | NIP-29: Addressable group roles definition. |
| 39005 | `KIND_THREAD_SUMMARY` | param-replaceable |  | Thread summary overlay: `e`/`d` tag = root event id, content = `{reply_count, descendant_count, last_reply_at, participants}`. |
| 39006 | `KIND_WINDOW_BOUNDS` | param-replaceable |  | Window bounds overlay: `d` tag = `<channel_id>:<request-cursor-or-head>`, content = `{has_more, next_cursor}`. |
| 40002 | `KIND_STREAM_MESSAGE_V2` | regular |  | V1 used kind:10002 (replaceable range — wrong). |
| 40003 | `KIND_STREAM_MESSAGE_EDIT` | regular |  | V1 used kind:10004 (replaceable range + NIP-51 collision — wrong). |
| 40004 | `KIND_STREAM_MESSAGE_PINNED` | regular |  | A stream message that has been pinned in a channel. |
| 40005 | `KIND_STREAM_MESSAGE_BOOKMARKED` | regular |  | A stream message that has been bookmarked by a user. |
| 40006 | `KIND_STREAM_MESSAGE_SCHEDULED` | regular |  | A stream message scheduled for future delivery. |
| 40007 | `KIND_STREAM_REMINDER` | regular |  | A reminder attached to a stream message or time. |
| 40008 | `KIND_STREAM_MESSAGE_DIFF` | regular |  | A diff/patch message showing file changes (unified diff format). |
| 40099 | `KIND_SYSTEM_MESSAGE` | regular |  | System message for channel state changes (join, leave, rename, etc.). |
| 40100 | `KIND_CANVAS` | regular |  | Canvas (shared document) for a channel. |
| 40901 | `KIND_CHANNEL_SUMMARY` | regular |  | Channel metadata with computed fields (relay-signed sidecar). |
| 40902 | `KIND_PRESENCE_SNAPSHOT` | regular |  | Bulk presence state (relay-signed sidecar). |
| 41001 | `KIND_DM_CREATED` | regular |  | A new direct-message conversation was created. |
| 41010 | `KIND_DM_OPEN` | regular |  | Open/create DM (p-tags = participants). |
| 41011 | `KIND_DM_ADD_MEMBER` | regular |  | Add member to group DM. |
| 41012 | `KIND_DM_HIDE` | regular |  | Hide DM from sidebar. |
| 42000 | `KIND_PRODUCT_FEEDBACK` | regular |  | Buzz product feedback submission. Accepted at ingest, sidecarred to the deployment feedback table, and never stored or fanned out as an event. |
| 43001 | `KIND_JOB_REQUEST` | regular |  | An agent job was requested. |
| 43002 | `KIND_JOB_ACCEPTED` | regular |  | An agent accepted a job request. |
| 43003 | `KIND_JOB_PROGRESS` | regular |  | Progress update for an in-flight agent job. |
| 43004 | `KIND_JOB_RESULT` | regular |  | Final result of a completed agent job. |
| 43005 | `KIND_JOB_CANCEL` | regular |  | A job cancellation was requested. |
| 43006 | `KIND_JOB_ERROR` | regular |  | An agent job failed with an error. |
| 44100 | `KIND_MEMBER_ADDED_NOTIFICATION` | regular | p-gated | Relay-signed notification: the target pubkey was added to a channel. |
| 44101 | `KIND_MEMBER_REMOVED_NOTIFICATION` | regular | p-gated | Relay-signed notification: the target pubkey was removed from a channel. |
| 44200 | `KIND_AGENT_TURN_METRIC` | regular | p-gated, result-gated | NIP-AM: Agent Turn Metric — durable per-turn token-usage record (agent-authored). |
| 45001 | `KIND_FORUM_POST` | regular |  | A forum post (thread root). |
| 45002 | `KIND_FORUM_VOTE` | regular |  | A vote on a forum post. |
| 45003 | `KIND_FORUM_COMMENT` | regular |  | A comment reply on a forum post. |
| 46001 | `KIND_WORKFLOW_TRIGGERED` | regular |  | A workflow was triggered by a matching event. |
| 46002 | `KIND_WORKFLOW_STEP_STARTED` | regular |  | A workflow step began execution. |
| 46003 | `KIND_WORKFLOW_STEP_COMPLETED` | regular |  | A workflow step completed successfully. |
| 46004 | `KIND_WORKFLOW_STEP_FAILED` | regular |  | A workflow step failed. |
| 46005 | `KIND_WORKFLOW_COMPLETED` | regular |  | The entire workflow completed successfully. |
| 46006 | `KIND_WORKFLOW_FAILED` | regular |  | The entire workflow failed. |
| 46007 | `KIND_WORKFLOW_CANCELLED` | regular |  | The workflow was cancelled before completion. |
| 46010 | `KIND_WORKFLOW_APPROVAL_REQUESTED` | regular |  | A workflow step is waiting for human approval. |
| 46011 | `KIND_WORKFLOW_APPROVAL_GRANTED` | regular |  | A pending workflow approval was granted. |
| 46012 | `KIND_WORKFLOW_APPROVAL_DENIED` | regular |  | A pending workflow approval was denied. |
| 46020 | `KIND_WORKFLOW_TRIGGER` | regular |  | Trigger workflow execution. |
| 46030 | `KIND_APPROVAL_GRANT` | regular |  | Grant pending approval. |
| 46031 | `KIND_APPROVAL_DENY` | regular |  | Deny pending approval. |
| 48001 | `KIND_AUDIT_ENTRY` | regular |  | An audit log entry was recorded. |
| 48100 | `KIND_HUDDLE_STARTED` | regular |  | A huddle (audio/video session) was started. |
| 48101 | `KIND_HUDDLE_PARTICIPANT_JOINED` | regular |  | A participant joined a huddle. |
| 48102 | `KIND_HUDDLE_PARTICIPANT_LEFT` | regular |  | A participant left a huddle. |
| 48103 | `KIND_HUDDLE_ENDED` | regular |  | A huddle ended. |
| 48106 | `KIND_HUDDLE_GUIDELINES` | regular |  | Huddle channel guidelines/rules document. |
| 49001 | `KIND_MEDIA_UPLOAD` | regular |  | Internal kind for media upload audit entries. Not a relay event kind. |

**Row count.** 133 rows: the 130 constants in `ALL_KINDS` plus the three constants
documented in *Generated versus authored* below that `kind.rs` defines but omits from
that array. Verified by mechanically counting `pub const NAME: u32 = N` declarations
in `kind.rs` (excluding the four `_MIN`/`_MAX` range-bound constants, which describe a
range rather than register a kind) and cross-checking against `ALL_KINDS`'s own length.

## Derived classification helpers

Beyond the per-row *Delivery* and *Access notes* columns above, `kind.rs` defines six
further boolean-returning functions that group kinds by role rather than by number
range or read-visibility. These are listed here because a reader relying only on the
table above would not otherwise learn a kind belongs to one of these groups:

| Helper | Members |
|---|---|
| `is_relay_only_kind` | `KIND_NIP43_MEMBERSHIP_LIST`, `KIND_CHANNEL_SUMMARY`, `KIND_PRESENCE_SNAPSHOT`, `KIND_DM_VISIBILITY`, `KIND_THREAD_SUMMARY`, `KIND_WINDOW_BOUNDS` — client submission of these kinds must be rejected. |
| `is_command_kind` | `KIND_WORKFLOW_DEF`, `KIND_DM_OPEN`, `KIND_DM_ADD_MEMBER`, `KIND_DM_HIDE`, `KIND_WORKFLOW_TRIGGER`, `KIND_APPROVAL_GRANT`, `KIND_APPROVAL_DENY` — Buzz command kinds requiring transactional execution. |
| `is_moderation_command_kind` | `KIND_MODERATION_BAN`, `KIND_MODERATION_UNBAN`, `KIND_MODERATION_TIMEOUT`, `KIND_MODERATION_UNTIMEOUT`, `KIND_MODERATION_RESOLVE_REPORT` (kinds 9040–9044). |
| `is_relay_admin_kind` | `RELAY_ADMIN_ADD_MEMBER`, `RELAY_ADMIN_REMOVE_MEMBER`, `RELAY_ADMIN_CHANGE_ROLE`, `RELAY_ADMIN_SET_WORKSPACE_PROFILE` (kinds 9030–9033). |
| `is_identity_archive_request_kind` | `KIND_IA_ARCHIVE_REQUEST`, `KIND_IA_UNARCHIVE_REQUEST` — only the user-signed request kinds; the relay-signed delta/snapshot kinds (8002/8003/13535) are intentionally excluded since the relay emits them, never ingests them. |
| `is_workflow_execution_kind` | A range check, `KIND_WORKFLOW_TRIGGERED..=KIND_WORKFLOW_APPROVAL_DENIED` (46001–46012 inclusive), not a literal list like the other five helpers. |

## Generated versus authored

**Everything in this document is hand-authored**, including this table. No part of
this file is produced by a generator, and none of it is exempt from the corpus's
Markdown-only rule for that reason (`AGENTS.md`: every non-`.md` file under the corpus
root is rejected today, because no generator exists yet to reproduce corpus content
from source — issue `#1316`).

**What is authored versus generated inside `kind.rs` itself, which this table
transcribes:** every `pub const` declaration, its numeric value, and its doc comment
are hand-authored Rust source. `ALL_KINDS`, `AUTHOR_ONLY_KINDS`, `P_GATED_KINDS`,
`SHARED_GATED_KINDS`, and `RESULT_GATED_KINDS` are hand-authored literal arrays — nothing
in `kind.rs` computes their membership; an engineer adding a new kind edits these arrays
by hand, and the `no_duplicate_kind_values` test (plus the compile-time
`is_replaceable`/`is_parameterized_replaceable` assertions further down the file) is
the only mechanical check that catches a mistake in that hand-editing. This document's
own table is therefore two authoring steps removed from the wire protocol: a human
wrote the Rust constant and array membership, and a human (via this task) transcribed
those into Markdown rows. **Nothing here is generated in the corpus's own sense of the
word** (a `generated/` projection reproducible from another canonical source) — a
future generator producing this table mechanically from `kind.rs` is explicitly out of
scope for this task (see *Scope and omissions*), and if one is ever built, this
document's own provenance section is where that fact belongs.

## Boundary

This node does not describe:

- **Any single kind's full wire contract** — its exact tag shape and cardinality, its
  content-field encoding, a worked example JSON event, or its versioning history
  beyond the one-line note `kind.rs`'s own doc comment carries (e.g. `KIND_STREAM_MESSAGE_V2`'s
  "V1 used kind:10002 ... wrong"). That is a per-kind instance node's job, per
  `corpus-template-event-kind`'s *Required sections* — none of those instance nodes
  exist yet for any kind in this table.
- **Why a kind's access-control membership is what it is**, beyond naming the set it
  belongs to. `kind.rs`'s own doc comments sometimes state the reason (e.g.
  `SHARED_GATED_KINDS`'s comment names why `KIND_TEAM` is deliberately excluded); this
  table does not restate that reasoning per row, only the membership fact itself.
- **How a caller produces or consumes an event of a given kind** — a `buzz-cli`
  subcommand, a `buzz-sdk` builder function, or an HTTP route. That is an interface
  node's job (`corpus-template-event-kind`'s own boundary section names this same
  split against a filed sibling issue, `#1342`), not this registry's.
- **Any kind, range, or helper not present in `crates/buzz-core/src/kind.rs` at the
  recorded revision.** If a future revision adds, removes, or renumbers a kind, this
  table is stale until re-verified against that revision — see *Scope and omissions*.

## Relationships

**None declared.** At the recorded revision no `kind-*.md` per-kind instance node
exists anywhere under `launchpad/docs/corpus` (confirmed directly, not assumed — see
the evidence ledger above), so there is no node this registry could `references` or
sit `part-of` without the target failing `AGENTS.md`'s own merge-target resolution
rule. The templates this document's shape draws on
(`corpus-template-reference`, `corpus-template-event-kind`) are meta-documents about
how to *write* a node, not the registry's own subject matter, so this document cites
them as sources consulted while writing rather than declaring a schema
`relationships` edge to either. The first `kind-*.md` instance node authored against
`corpus-template-event-kind` is the natural moment to add a `references` (or
`part-of`) edge from that node back to this one, or from this one forward to it —
neither exists to check today.

## Scope and omissions

**This node covers** every `kind` integer `crates/buzz-core/src/kind.rs` defines at
commit `650354eab8d41ab6ce1a71de079a6c6d95c69052` — both the 130 in `ALL_KINDS` and the
3 defined-but-excluded from it — with its constant name, NIP-01 delivery
classification, named access-control set membership, and a one-line purpose drawn
from its own doc comment. It also covers the six derived classification helpers that
group kinds by role rather than by number or read-visibility.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Any single kind's full wire contract (tag shape, content encoding, worked example) | A future `kind-*.md` instance node per `corpus-template-event-kind`; none exist yet |
| The consumer-facing operation surface (CLI/SDK/HTTP) built on top of a kind | An interface-shaped corpus node, per `corpus-template-event-kind`'s own boundary note and issue `#1342` |
| *Why* a kind's access-control membership is what it is, beyond the membership fact | The per-kind instance node, or `kind.rs`'s own doc comment where one already states it |
| A mechanically generated version of this table, kept in sync with `kind.rs` automatically | Not built; `AGENTS.md` states no generator exists yet for any corpus content (`#1316`) |
| Kinds referenced only in external NIP text but never defined as a Buzz constant (e.g. Nostr kinds Buzz does not implement) | Out of scope by definition — this registry only covers what `kind.rs` itself registers |

**Expected but not verified when this node was written:**

- **Whether the three constants excluded from `ALL_KINDS` (`KIND_AUTH`, `KIND_NOSTR_IDENTITY_BINDING`,
  `KIND_PUSH_LEASE`) are excluded deliberately by design or as an oversight** was not
  established from any comment, commit message, or linked issue — `kind.rs`'s own doc
  comments explain *why each kind is never stored*, which is consistent with either
  explanation, but neither this table nor its author found text confirming the
  exclusion itself (as opposed to the non-storage behavior) was intentional.
- **No per-kind instance node has been authored yet from `corpus-template-event-kind`
  for any row in this table.** Whether this registry's own shape holds up once the
  first such instance node exists and needs to link back to it is untested.
- **This table was not re-run against any revision after `650354eab8d41ab6ce1a71de079a6c6d95c69052`.**
  A kind added, removed, or renumbered after that commit will not appear here until
  this node is next updated, per `AGENTS.md`'s own *Updating a node* procedure.
