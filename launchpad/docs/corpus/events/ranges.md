---
id: events-ranges
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
  - statement: "NIP-01 defines an event's kind field interpretation with four numeric categories: regular for kind n such that 1000<=n<10000 || 4<=n<45 || n==1 || n==2; replaceable for 10000<=n<20000 || n==0 || n==3; ephemeral for 20000<=n<30000; and addressable for 30000<=n<40000."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/01.md"
  - statement: "kind.rs defines PARAM_REPLACEABLE_KIND_MIN = 30000 and PARAM_REPLACEABLE_KIND_MAX = 39999 as the lower and upper bounds of the NIP-33 parameterized replaceable range, and EPHEMERAL_KIND_MIN = 20000 and EPHEMERAL_KIND_MAX = 29999 as the bounds of the ephemeral event range, each as its own named constant rather than an inline literal."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs implements is_ephemeral(kind) as kind >= EPHEMERAL_KIND_MIN && kind <= EPHEMERAL_KIND_MAX, is_replaceable(kind) as matches!(kind, 0 | 3 | KIND_CHANNEL_METADATA | 10000..=19999) with a comment noting NIP-33 parameterized-replaceable kinds use a different replacement key and are handled separately, and is_parameterized_replaceable(kind) as kind >= PARAM_REPLACEABLE_KIND_MIN && kind <= PARAM_REPLACEABLE_KIND_MAX."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs defines no is_regular helper function anywhere in the file; the 'regular' NIP-01 category has no dedicated boolean check and is reachable only as the residual case (not ephemeral, not replaceable, not parameterized-replaceable)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's own unit tests assert the parameterized-replaceable boundary directly (29999 false, 30000 true, 30023 true, 39000 true, 39999 true, 40000 false) and separately assert, by iterating every kind value 0 through 65535, that is_replaceable and is_parameterized_replaceable are never both true for the same kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "KIND_CHANNEL_METADATA = 41 carries the doc comment 'NIP-01: Channel metadata (replaceable). Not used by Buzz today,' yet is one of the four explicit values is_replaceable's own match arm names alongside 0, 3, and 10000..=19999."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs groups many of its own custom kinds under named section comments rather than a single flat list: 'NIP-29 group admin events' (9000, 9001, 9002, 9005, 9007, 9008, 9009, 9021, 9022), 'NIP-43 relay membership admin commands' (9030, 9031, 9032, 9033) paired with 'NIP-43 relay membership announcement events (relay-signed)' (8000, 8001, 13534), 'NIP-IA identity archival requests' (9035, 9036) paired with 'NIP-IA identity archival announcement events (relay-signed)' (8002, 8003, 13535), and 'Buzz community moderation commands' (9040, 9041, 9042, 9043, 9044, described as 'mod-signed, processed like 9030-series: validated + executed directly, never stored as regular events')."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's 'Ephemeral events (20000–29999)' section comment states these kinds go through 'Redis pub/sub only, never stored,' and groups KIND_PRESENCE_UPDATE (20001), KIND_TYPING_INDICATOR (20002), KIND_PAIRING (24134), KIND_AGENT_OBSERVER_FRAME (24200), and KIND_HUDDLE_REACTION (24810) under it; KIND_AUTH (22242), KIND_BLOSSOM_AUTH (24242), KIND_NOSTR_IDENTITY_BINDING (24243), KIND_HTTP_AUTH (27235), and KIND_NIP43_LEAVE_REQUEST (28936) fall in the same 20000-29999 numeric span but are documented individually, each with its own 'never stored' or 'ephemeral' note, rather than under that one section comment."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's 'Direct messages (41000–41999)' section comment groups KIND_DM_OPEN (41010), KIND_DM_ADD_MEMBER (41011), and KIND_DM_HIDE (41012); KIND_DM_CREATED (41001) is documented immediately alongside them in the same source block even though its own number falls outside the 41000-41999 span the comment states."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's 'Agent job protocol (43000–43999)' section comment groups KIND_JOB_REQUEST (43001) through KIND_JOB_ERROR (43006), and states explicitly: 'Not using NIP-90 kinds (5000–6999) — Buzz requires auth chains (depth <= 3, breadth <= 10).'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's 'Forum / social (45000–45999)' section comment groups KIND_FORUM_POST (45001), KIND_FORUM_VOTE (45002), and KIND_FORUM_COMMENT (45003), noting 'V1 used addressable range (30001–30003) — wrong.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's 'Workflow engine (46000–46999)' section comment groups command kinds KIND_WORKFLOW_TRIGGER (46020), KIND_APPROVAL_GRANT (46030), and KIND_APPROVAL_DENY (46031) alongside execution/event kinds KIND_WORKFLOW_TRIGGERED (46001) through KIND_WORKFLOW_APPROVAL_DENIED (46012); is_workflow_execution_kind checks only the contiguous 46001-46012 sub-range ('kind >= KIND_WORKFLOW_TRIGGERED && kind <= KIND_WORKFLOW_APPROVAL_DENIED'), explicitly excluding the three command kinds, with the comment 'These must not trigger workflows (prevents infinite loops).'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs contains a 'User groups (47000–47999)' section comment with no constant defined beneath it anywhere in the file at this revision -- the band is named but currently empty."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's 'System / admin custom range (48000–48999)' section comment groups KIND_AUDIT_ENTRY (48001) and the four huddle kinds KIND_HUDDLE_STARTED (48100), KIND_HUDDLE_PARTICIPANT_JOINED (48101), KIND_HUDDLE_PARTICIPANT_LEFT (48102), KIND_HUDDLE_ENDED (48103), and KIND_HUDDLE_GUIDELINES (48106)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's 'Media (49000–49999)' section comment names only KIND_MEDIA_UPLOAD (49001), documented as 'Internal kind for media upload audit entries. Not a relay event kind.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's 'Stream messaging' section comment groups KIND_STREAM_MESSAGE_V2 (40002) through KIND_STREAM_MESSAGE_DIFF (40008), plus KIND_SYSTEM_MESSAGE (40099) and KIND_CANVAS (40100); KIND_STREAM_MESSAGE (kind 9, the NIP-29 group chat message kind) is documented in the same block as the pre-40000s predecessor these V2+ kinds replaced, with an inline note that agent shutdown uses kind:9 with content '!shutdown' as 'a convention, not a new event kind.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's 'Relay-only sidecar kinds (never client-submitted)' section comment groups KIND_CHANNEL_SUMMARY (40901) and KIND_PRESENCE_SNAPSHOT (40902); the function is_relay_only_kind additionally covers KIND_NIP43_MEMBERSHIP_LIST (13534), KIND_DM_VISIBILITY (30622), KIND_THREAD_SUMMARY (39005), and KIND_WINDOW_BOUNDS (39006) -- four kinds documented individually elsewhere in the file rather than under this section comment, even though the function groups all six behind one client-submission-rejection check."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs defines four named sets governing per-kind read access independently of any numeric range -- AUTHOR_ONLY_KINDS, P_GATED_KINDS, SHARED_GATED_KINDS, RESULT_GATED_KINDS -- whose membership crosses NIP-01 category boundaries freely: P_GATED_KINDS contains both KIND_GIFT_WRAP (1059, NIP-01 regular range) and KIND_AGENT_OBSERVER_FRAME (24200, ephemeral range) in the same list."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs defines is_moderation_command_kind (checks membership in the explicit five-value list 9040, 9041, 9042, 9043, 9044), is_relay_admin_kind (9030, 9031, 9032, 9033), and is_identity_archive_request_kind (9035, 9036) as finite membership checks against an explicit value list, structurally different from is_ephemeral/is_replaceable/is_parameterized_replaceable, which each test a contiguous numeric range with a single inequality."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs cross-checks several of its own newer constants against these range helpers using compile-time assertions -- for example 'const _: () = assert!(is_parameterized_replaceable(KIND_PERSONA));' for kind 30175 -- and a runtime test, no_duplicate_kind_values, asserting every value in the ALL_KINDS constant is unique."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "The numeric span below 8000 that this document labels 'unbanded / NIP-native' -- kinds 0, 1, 3, 5, 7, 9, 41, and the NIP-34/NIP-56 kinds in the 1000s (1059, 1063, 1617 through 1633, 1984) -- is not grouped under any of kind.rs's own named decimal-thousand section comments; each constant in that span is documented individually next to the NIP it implements rather than as a member of a Buzz-authored band."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/kind.rs"
    confidence: 0.75
---

# Event kind numeric ranges

Catalogues how Nostr `kind` integers are organized in Buzz: the four numeric
categories NIP-01 itself defines (regular, replaceable, ephemeral, addressable),
how `crates/buzz-core/src/kind.rs` cross-checks a kind number against them in code,
and the further decimal-thousand numeric bands Buzz's own kind registry groups its
custom kinds into. This is a numeric-range lookup, not a per-kind wire-contract
document — see *Scope and omissions* below for where that content lives instead.

## NIP-01 numeric categories (protocol-defined)

These four categories and their boundaries come from the Nostr protocol itself,
not from Buzz. Every kind number, Buzz-defined or not, falls into exactly one.

| Category | NIP-01 rule | Buzz cross-check in `kind.rs` | Notes |
|---|---|---|---|
| Regular | `1000<=n<10000 \|\| 4<=n<45 \|\| n==1 \|\| n==2` | No dedicated helper — reachable only as the residual case (not ephemeral, not replaceable, not parameterized-replaceable) | Most of Buzz's custom kinds at 8000 and above land here by default |
| Replaceable | `10000<=n<20000 \|\| n==0 \|\| n==3` | `is_replaceable(kind)` → `matches!(kind, 0 \| 3 \| KIND_CHANNEL_METADATA \| 10000..=19999)` | Includes kind 41 (`KIND_CHANNEL_METADATA`) explicitly, though its own doc comment states it is "Not used by Buzz today" |
| Ephemeral | `20000<=n<30000` | `is_ephemeral(kind)` → `kind >= EPHEMERAL_KIND_MIN(20000) && kind <= EPHEMERAL_KIND_MAX(29999)` | Never stored — Redis pub/sub only, per `kind.rs`'s own section comment |
| Addressable (parameterized replaceable) | `30000<=n<40000` | `is_parameterized_replaceable(kind)` → `kind >= PARAM_REPLACEABLE_KIND_MIN(30000) && kind <= PARAM_REPLACEABLE_KIND_MAX(39999)` | Keyed by `(pubkey, kind, d_tag)`; latest `created_at` wins |

`kind.rs`'s own tests assert the parameterized-replaceable boundary directly
(29999 false, 30000 true, 39999 true, 40000 false) and separately assert that
`is_replaceable` and `is_parameterized_replaceable` never agree on the same kind,
across every value 0 through 65535.

## Generated versus authored: what the numbers below add

The table above is everything NIP-01 itself mandates about kind numbering. It says
nothing about how a relay should subdivide its own custom kind space within those
four bands — that division is Buzz's own, evidenced only by `kind.rs`'s inline
section comments, not required by any specification. The table above is
**protocol-generated**; the table below is **Buzz-authored convention**, and no
NIP requires any of it to hold.

## Buzz-authored custom numeric bands

Each row is one of `kind.rs`'s own named section comments (or, where a range has
no shared section header, the numeric span its individual constants occupy in the
same source block).

| Numeric band | NIP-01 category | Domain | Representative kinds | Source comment |
|---|---|---|---|---|
| 8000–8003, 13534–13535 | Regular (relay-signed announcements; 13534/13535 are replaceable by stated convention, not `is_replaceable`) | NIP-43 relay membership + NIP-IA identity archival announcements | `KIND_NIP43_MEMBER_ADDED`=8000, `KIND_NIP43_MEMBER_REMOVED`=8001, `KIND_IA_ARCHIVED`=8002, `KIND_IA_UNARCHIVED`=8003, `KIND_NIP43_MEMBERSHIP_LIST`=13534, `KIND_IA_ARCHIVED_LIST`=13535 | "NIP-43 relay membership announcement events (relay-signed)" / "NIP-IA identity archival announcement events (relay-signed)" |
| 9000–9022 | Regular | NIP-29 group admin, moderation, join/leave | `KIND_NIP29_PUT_USER`=9000 … `KIND_NIP29_LEAVE_REQUEST`=9022 | "NIP-29 group admin events" |
| 9030–9036 | Regular | NIP-43 relay admin commands (9030–9033) + NIP-IA archive requests (9035–9036) | `RELAY_ADMIN_ADD_MEMBER`=9030 … `KIND_IA_UNARCHIVE_REQUEST`=9036 | "NIP-43 relay membership admin commands" / "NIP-IA identity archival requests" |
| 9040–9044 | Regular | Buzz community moderation commands | `KIND_MODERATION_BAN`=9040 … `KIND_MODERATION_RESOLVE_REPORT`=9044 | "Buzz community moderation commands" |
| 10000–19999 | Replaceable | NIP-51/NIP-65 user lists + agent profile | `KIND_MUTE_LIST`=10000, `KIND_PIN_LIST`=10001, `KIND_NIP65_RELAY_LIST_METADATA`=10002, `KIND_BOOKMARK_LIST`=10003, `KIND_EMOJI_LIST`=10030, `KIND_AGENT_PROFILE`=10100 | individual doc comments, each stating "(replaceable" |
| 20000–29999 | Ephemeral | Presence, typing, pairing, agent telemetry, auth handshakes | `KIND_PRESENCE_UPDATE`=20001, `KIND_TYPING_INDICATOR`=20002, `KIND_PAIRING`=24134, `KIND_AGENT_OBSERVER_FRAME`=24200, `KIND_HUDDLE_REACTION`=24810, plus individually-documented `KIND_AUTH`=22242, `KIND_BLOSSOM_AUTH`=24242, `KIND_NOSTR_IDENTITY_BINDING`=24243, `KIND_HTTP_AUTH`=27235, `KIND_NIP43_LEAVE_REQUEST`=28936 | "Ephemeral events (20000–29999) — Redis pub/sub only, never stored" |
| 30000–39999 | Addressable | NIP-33/NIP-51/NIP-29 parameterized-replaceable custom state | `KIND_FOLLOW_SET`=30000, `KIND_BOOKMARK_SET`=30003, `KIND_EMOJI_SET`=30030, `KIND_LONG_FORM`=30023, `KIND_USER_STATUS`=30315, `KIND_READ_STATE`=30078, `KIND_AGENT_ENGRAM`=30174, `KIND_PERSONA`=30175, `KIND_TEAM`=30176, `KIND_MANAGED_AGENT`=30177, `KIND_TEAM_CATALOG`=30178, `KIND_PRIVATE_MANAGED_AGENT`=30179, `KIND_EVENT_REMINDER`=30300, `KIND_PUSH_LEASE`=30350, `KIND_GIT_REPO_ANNOUNCEMENT`=30617, `KIND_GIT_REPO_STATE`=30618, `KIND_PROJECT`=30621, `KIND_WORKFLOW_DEF`=30620, `KIND_DM_VISIBILITY`=30622, `KIND_NIP29_GROUP_METADATA`=39000 … `KIND_NIP29_GROUP_ROLES`=39003, `KIND_THREAD_SUMMARY`=39005, `KIND_WINDOW_BOUNDS`=39006 | individual doc comments, each stating "(parameterized replaceable" |
| 40001–40100 | Regular | Buzz stream messaging + canvas + system message | `KIND_STREAM_MESSAGE_V2`=40002 … `KIND_STREAM_MESSAGE_DIFF`=40008, `KIND_SYSTEM_MESSAGE`=40099, `KIND_CANVAS`=40100 | "Stream messaging" (`KIND_STREAM_MESSAGE`=9 documented alongside as the pre-40000s predecessor) |
| 40901–40902 | Regular, relay-only | Relay-signed sidecar projections | `KIND_CHANNEL_SUMMARY`=40901, `KIND_PRESENCE_SNAPSHOT`=40902 | "Relay-only sidecar kinds (never client-submitted)" |
| 41000–41999 | Regular | Direct messages | `KIND_DM_OPEN`=41010, `KIND_DM_ADD_MEMBER`=41011, `KIND_DM_HIDE`=41012 (`KIND_DM_CREATED`=41001 documented in the same block, outside this numeric span) | "Direct messages (41000–41999)" |
| 42000 | Regular | Product feedback | `KIND_PRODUCT_FEEDBACK`=42000 | inline comment, no shared section header |
| 43000–43999 | Regular | Agent job protocol | `KIND_JOB_REQUEST`=43001 … `KIND_JOB_ERROR`=43006 | "Agent job protocol (43000–43999)" |
| 44100–44200 | Regular | Member notifications + agent turn metrics | `KIND_MEMBER_ADDED_NOTIFICATION`=44100, `KIND_MEMBER_REMOVED_NOTIFICATION`=44101, `KIND_AGENT_TURN_METRIC`=44200 | individual inline comments, no shared section header |
| 45000–45999 | Regular | Forum / social | `KIND_FORUM_POST`=45001, `KIND_FORUM_VOTE`=45002, `KIND_FORUM_COMMENT`=45003 | "Forum / social (45000–45999)" |
| 46000–46999 | Regular | Workflow engine — commands (46020, 46030–46031) + execution events (46001–46012) | `KIND_WORKFLOW_TRIGGER`=46020, `KIND_APPROVAL_GRANT`=46030, `KIND_APPROVAL_DENY`=46031; `KIND_WORKFLOW_TRIGGERED`=46001 … `KIND_WORKFLOW_APPROVAL_DENIED`=46012 | "Workflow engine (46000–46999)"; `is_workflow_execution_kind` covers only 46001–46012 |
| 47000–47999 | Regular (reserved) | User groups — no kind defined at this revision | none | "User groups (47000–47999)" (comment only) |
| 48000–48999 | Regular | System / admin custom range | `KIND_AUDIT_ENTRY`=48001, `KIND_HUDDLE_STARTED`=48100 … `KIND_HUDDLE_GUIDELINES`=48106 | "System / admin custom range (48000–48999)" |
| 49000–49999 | Regular | Media | `KIND_MEDIA_UPLOAD`=49001 (internal audit kind, "Not a relay event kind") | "Media (49000–49999)" |

### Unbanded / NIP-native kinds (below 8000)

*INFERENCE, confidence 0.75 — reasoned from the absence of a grouping comment in
`kind.rs`, not stated there directly.* Kinds 0, 1, 3, 5, 7, 9, and 41, plus the
NIP-34/NIP-56 kinds in the 1000s (1059, 1063, 1617–1633, 1984), are not grouped
under any Buzz-authored decimal-thousand section comment. Each is documented
individually, next to the NIP it implements, rather than as a member of a Buzz
band: `KIND_PROFILE`=0, `KIND_TEXT_NOTE`=1, `KIND_CONTACT_LIST`=3,
`KIND_DELETION`=5, `KIND_REACTION`=7, `KIND_STREAM_MESSAGE`=9,
`KIND_CHANNEL_METADATA`=41, `KIND_GIFT_WRAP`=1059, `KIND_FILE_METADATA`=1063,
`KIND_GIT_PATCH`=1617, `KIND_GIT_PULL_REQUEST`=1618, `KIND_GIT_PR_UPDATE`=1619,
`KIND_GIT_ISSUE`=1621, `KIND_GIT_STATUS_OPEN`=1630, `KIND_GIT_STATUS_MERGED`=1631,
`KIND_GIT_STATUS_CLOSED`=1632, `KIND_GIT_STATUS_DRAFT`=1633,
`KIND_REPORT`=1984.

## Range-classification helpers in `kind.rs`

| Helper | What it tests |
|---|---|
| `is_ephemeral(kind)` | Contiguous range: `EPHEMERAL_KIND_MIN..=EPHEMERAL_KIND_MAX` (20000–29999) |
| `is_replaceable(kind)` | Explicit value set: `0 \| 3 \| KIND_CHANNEL_METADATA \| 10000..=19999` |
| `is_parameterized_replaceable(kind)` | Contiguous range: `PARAM_REPLACEABLE_KIND_MIN..=PARAM_REPLACEABLE_KIND_MAX` (30000–39999) |
| `is_workflow_execution_kind(kind)` | Contiguous sub-range within the 46000s band: `KIND_WORKFLOW_TRIGGERED..=KIND_WORKFLOW_APPROVAL_DENIED` (46001–46012) |
| `is_moderation_command_kind(kind)` | Finite membership list: `{9040, 9041, 9042, 9043, 9044}` |
| `is_relay_admin_kind(kind)` | Finite membership list: `{9030, 9031, 9032, 9033}` |
| `is_identity_archive_request_kind(kind)` | Finite membership list: `{9035, 9036}` |
| `is_relay_only_kind(kind)` | Finite membership list spanning multiple bands: `{13534, 40901, 40902, 30622, 39005, 39006}` |

The first three test a contiguous numeric range with one inequality; the rest test
membership in an explicit, finite list of kind values and do not correspond to any
single contiguous band.

## Boundary — what this document does not classify

- **Access-control set membership** (`AUTHOR_ONLY_KINDS`, `P_GATED_KINDS`,
  `SHARED_GATED_KINDS`, `RESULT_GATED_KINDS`) is orthogonal to numeric range —
  `P_GATED_KINDS` mixes a regular kind (`KIND_GIFT_WRAP`=1059) with an ephemeral
  one (`KIND_AGENT_OBSERVER_FRAME`=24200) in the same list. Documenting these sets
  belongs to a future access-control-focused reference or to the individual
  event-kind nodes that name their own membership, not to a numeric-range
  document.
- **`is_command_kind`, `is_shared_gated_kind`, `event_is_shared`,
  `is_unshared_gated_event`** are behavioral predicates over tag shape and
  access control, not range classifiers, and are out of scope here for the same
  reason.
- **A kind's tag shape, content-field semantics, and worked example** are the
  subject of a per-kind `kind-*.md` node built from `corpus-template-event-kind`
  (`launchpad/docs/corpus/templates/event-kind.md`) — no such instance node
  exists in the corpus yet.
- **Renumbering history** recorded as inline `kind.rs` comments (e.g. "V1 used
  kind:10001 (replaceable range — wrong), then 40001") is not reproduced here;
  read `kind.rs` directly for a given kind's own history.

## Relationships

None declared. At the recorded revision the corpus carries no merged node whose
subject is Nostr event kinds, NIP-01, or a numeric-range convention — the two
existing `interfaces-events`-typed nodes (`corpus-template-event-kind`,
`corpus-template-interface`) are templates describing how to *write* an
instance node, not reference-shaped subject matter this document would cite as a
dependency. The first real `kind-*.md` instance node is the natural moment to add
a `references` (or `implements`, from that node's own side) edge back to this
document, once one exists.

## Scope and omissions

**This document covers** the four NIP-01 numeric categories (regular,
replaceable, ephemeral, addressable), Buzz's own `kind.rs` cross-check helpers and
constants for them, and the further decimal-thousand numeric bands `kind.rs`'s
own section comments organize its custom kinds into — labeled explicitly as an
authored convention, not a protocol requirement.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| A given kind's tag shape, content-field semantics, access-control model, and worked example | `launchpad/docs/corpus/templates/event-kind.md`, and the per-kind instance nodes it will produce (none exist yet) |
| The four access-control sets and their membership predicates | A future access-control-focused reference or the individual event-kind nodes that name their own membership; not yet filed as its own corpus task at time of writing |
| Kind renumbering history | `crates/buzz-core/src/kind.rs`'s own inline comments, read directly |
| The interface/consumer-facing operation surface built on top of a kind (a CLI subcommand, an SDK builder, an HTTP route) | `launchpad/docs/corpus/templates/interface.md` and its future instance nodes |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**No `relationships` in this node's own front matter.** See *Relationships* above
for what was checked and why nothing currently in the corpus is a fit.

**Expected but not verified when this node was written:**

- **No real `kind-*.md` instance node has been authored yet** from
  `corpus-template-event-kind`, so whether this range document and a future
  per-kind node duplicate any content, or leave a gap between them, is untested.
- **Whether every band listed above is exhaustive of `kind.rs` at this revision**
  was checked by reading the file in full once, not by a mechanical diff against
  `ALL_KINDS`; a kind added after the recorded revision is not reflected here
  until this node is next updated.
