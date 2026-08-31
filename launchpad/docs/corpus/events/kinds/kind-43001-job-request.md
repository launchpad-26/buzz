---
id: events-kinds-kind-43001-job-request
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a8b5021efb92264e724366d08b47b2a3839eb90a."
    entry_class: FACT
    evidence:
      - "commit a8b5021efb92264e724366d08b47b2a3839eb90a"
  - statement: "crates/buzz-core/src/kind.rs defines KIND_JOB_REQUEST as the u32 constant 43001, in a section headed 'Agent job protocol (43000-43999)' whose comment reads 'Not using NIP-90 kinds (5000-6999) -- Buzz requires auth chains (depth <= 3, breadth <= 10)', alongside sibling constants KIND_JOB_ACCEPTED = 43002, KIND_JOB_PROGRESS = 43003, KIND_JOB_RESULT = 43004, KIND_JOB_CANCEL = 43005, KIND_JOB_ERROR = 43006."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "KIND_JOB_REQUEST's own doc comment in kind.rs is exactly one line, 'An agent job was requested.' -- it states no tag shape, content shape, or access-control detail inline, unlike several newer kinds in the same file (e.g. KIND_AGENT_TURN_METRIC's multi-line comment naming its exact tag cardinality and encryption model)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs's is_ephemeral (true for 20000<=kind<=29999), is_replaceable (true only for kind in {0, 3, 41, 10000..=19999}), and is_parameterized_replaceable (true for 30000<=kind<=39999) each evaluate false for 43001, because 43001 falls in none of their match arms."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "NIP-01, pinned at commit dabfcb2aaecf4fa374eda8b1232ab303a03f60ba, defines exactly four numeric kind categories -- regular (1000<=n<10000 || 4<=n<45 || n==1 || n==2), replaceable (10000<=n<20000 || n==0 || n==3), ephemeral (20000<=n<30000), and addressable (30000<=n<40000) -- and contains no sentence stating a default or fallback rule for any kind numbered 40000 or higher; the document's own closing line is 'These are just conventions and relay implementations may differ.' Kind 43001 therefore sits outside every one of NIP-01's four stated numeric ranges, including 'regular'."
    entry_class: FACT
    evidence:
      - "https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/01.md"
  - statement: "Because is_ephemeral, is_replaceable, and is_parameterized_replaceable are the only three special-case predicates Buzz's kind model defines and none matches 43001, Buzz's own implementation treats kind 43001 as an ordinary persistent (stored), non-replaceable event by the absence of any special classification -- even though NIP-01's own numeric ranges do not literally reach a kind this high."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/kind.rs"
    confidence: 0.85
  - statement: "43001 is not a member of any of kind.rs's four access-control sets: AUTHOR_ONLY_KINDS, RESULT_GATED_KINDS, P_GATED_KINDS, and SHARED_GATED_KINDS -- each list's full contents were read directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "crates/buzz-relay/src/handlers/ingest.rs's is_global_only_kind and requires_h_channel_scope functions each enumerate an explicit, finite set of kinds; KIND_JOB_REQUEST (43001) is a member of neither. For such a kind the ingest pipeline's default path runs: channel_id = extract_channel_id(&event), which reads an optional NIP-29 'h' tag if the event carries one and otherwise leaves channel_id as None (global/channel-less) -- an 'h' tag is honored when present but never required for this kind."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "schema/schema.sql's events.search_tsv GENERATED ALWAYS column expression forces a NULL tsvector only for kind IN (1059, 30179, 30300, 30350, 30622, 44100, 44101, 44200); 43001 is not in that list, so a stored kind:43001 event's content is indexed by the ordinary to_tsvector('simple', content) branch and is discoverable through NIP-50 full-text search like any non-privacy-gated kind."
    entry_class: FACT
    evidence:
      - "schema/schema.sql"
  - statement: "crates/buzz-relay/src/handlers/event.rs's dispatch_persistent_event is the generic, kind-agnostic post-commit dispatch seam for every stored (non-ephemeral) event -- its own doc comment calls it schedule for 'post-commit delivery/side effects for a stored event'. It unconditionally calls enqueue_event_created_audit, which logs a buzz_audit::AuditAction::EventCreated entry recording the resolved actor pubkey, the event id, and the event kind. No kind-specific audit branch exists for 43001 or any of its five sibling job-protocol kinds."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "crates/buzz-db/src/store/feed.rs's build_activity_query includes KIND_JOB_REQUEST -- together with KIND_JOB_PROGRESS and KIND_JOB_RESULT, but not KIND_JOB_ACCEPTED, KIND_JOB_CANCEL, or KIND_JOB_ERROR -- in the kind filter for the Home Feed's channel-scoped 'activity' query, subject to the same accessible-channel visibility filter as stream messages and forum posts."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/feed.rs"
  - statement: "crates/buzz-relay/src/handlers/event.rs's bounded_kind_label function assigns the range 43001..=43006 its own literal per-kind metrics-label bucket (kind.to_string()), rather than folding it into the catch-all 'other' bucket used for unrecognized kinds -- confirming the relay's metrics path already recognizes the whole job-protocol range as a distinct, intentional group."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "desktop/src/shared/constants/kinds.ts defines KIND_JOB_REQUEST = 43001 and includes it in both CHANNEL_TIMELINE_CONTENT_KINDS (rendered as its own timeline row) and NON_CONVERSATIONAL_UNREAD_KINDS (visible in the timeline but excluded from a channel's unread-badge count, alongside its five sibling job kinds and KIND_SYSTEM_MESSAGE)."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/constants/kinds.ts"
  - statement: "desktop/src/features/home/lib/inbox.ts and desktop/src/features/home/ui/FeedSection.tsx each render the Home Feed headline 'Job requested' for an item of kind 43001, and desktop/src/features/search/ui/SearchResultItem.tsx separately labels a search hit of kind 43001 'Agent job'."
    entry_class: FACT
    evidence:
      - "desktop/src/features/home/lib/inbox.ts"
      - "desktop/src/features/home/ui/FeedSection.tsx"
      - "desktop/src/features/search/ui/SearchResultItem.tsx"
  - statement: "desktop/src/features/notifications/lib/sound.ts states directly: 'The agent job protocol (kinds 43001-43006) is defined and queryable but nothing emits the events yet -- buzz-acp publishes plain stream messages.' Its job-lifecycle notification-sound slots are wired (resolver, defaults, settings) but render disabled behind a 'coming soon' badge for exactly this reason -- kind 43001 itself has no dedicated sound slot; the four coming-soon slots cover job_accepted, job_progress, job_result, and job_error only."
    entry_class: FACT
    evidence:
      - "desktop/src/features/notifications/lib/sound.ts"
  - statement: "mobile/lib/shared/relay/nostr_models.dart defines jobRequest = 43001 and includes it in channelTimelineContentKinds; mobile/lib/features/activity/activity_provider.dart's ActivityNotifier queries kinds [43001, 43002, 43003, 43004, 43005, 43006] filtered by a '#p' tag equal to the viewer's own pubkey, documented inline as 'agent job lifecycle events addressed to me'; mobile/lib/features/activity/feed_item.dart renders the headline 'Job requested' for kind 43001, matching desktop's inbox.ts/FeedSection.tsx headline text exactly."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/nostr_models.dart"
      - "mobile/lib/features/activity/activity_provider.dart"
      - "mobile/lib/features/activity/feed_item.dart"
  - statement: "Because the only consumer-side code found that queries kind 43001 by tag (mobile's ActivityNotifier) filters on a '#p' tag equal to the viewer's own pubkey and documents this as events 'addressed to me', a job request is evidently expected to carry a 'p' tag naming the agent (or human) asked to perform the job -- but no ingest-side validation enforcing a 'p' tag specifically for kind 43001 was found in ingest.rs, so this is a consumer-side expectation rather than a relay-enforced or producer-confirmed tag rule."
    entry_class: INFERENCE
    evidence:
      - "mobile/lib/features/activity/activity_provider.dart"
      - "crates/buzz-relay/src/handlers/ingest.rs"
    confidence: 0.7
  - statement: "No file under docs/nips/ names kind 43001 or the job-request/job-protocol concept. A direct grep of every docs/nips/*.md file for '43001' returned zero matches, and a grep for 'job' returned only an incidental hit inside NIP-PL.md's unrelated discussion of durable push-delivery 'jobs' -- a different concept (push notification delivery, not agent work requests)."
    entry_class: FACT
    evidence:
      - "shell(grep -rl '43001' docs/nips/*.md) -> no matches; shell(grep -li 'job' docs/nips/*.md) -> NIP-PL.md only, unrelated push-delivery-jobs usage"
  - statement: "launchpad/docs/corpus/architecture/context/ai-agent.md (merged on origin/launchpad, id architecture-context-ai-agent) names 43000-43999 as 'an agent job protocol (KIND_JOB_REQUEST / KIND_JOB_ACCEPTED / KIND_JOB_PROGRESS / KIND_JOB_RESULT), through which one agent (or a human) can request work from an agent as a distinct concept from an ordinary chat message,' and its own Scope and omissions table names exactly this gap: 'The agent job protocol's (KIND_JOB_REQUEST family) message shapes, auth-chain depth/breadth rules, and NIP-90-vs-Buzz rationale | A future interfaces/events-level corpus node, not yet authored.' This node is that node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/context/ai-agent.md"
  - statement: "Checked immediately before finalizing this node's front matter (git fetch origin launchpad; git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus): the merge target already carries launchpad/docs/corpus/templates/event-kind.md (id corpus-template-event-kind) and launchpad/docs/corpus/architecture/context/ai-agent.md (id architecture-context-ai-agent), and carries no launchpad/docs/corpus/events/ path at all -- so this is a new node, not an edit, and both relationship targets below resolve on the branch this change will merge into."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus', run '2026-09-01') -> templates/event-kind.md(id=corpus-template-event-kind), architecture/context/ai-agent.md(id=architecture-context-ai-agent) present; no events/ path present"
  - statement: "Issue #879's Definition of done requires this node to state the event kind number/name and its persistent/replaceable/ephemeral classification; to define required/optional tags/content and validation rules; to name producers, consumers, authorization, and persistence/fanout/search/audit treatment; and to link the relevant NIP/spec, handler/registry, and conformance/tests -- taken as this node's own scope rather than re-derived from parent Feature #616 or PRD #602."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#879 definition of done"
relationships:
  - type: implements
    target: corpus-template-event-kind
  - type: references
    target: architecture-context-ai-agent
---

# Event kind 43001 — job request

`KIND_JOB_REQUEST = 43001`, the constant `crates/buzz-core/src/kind.rs` names for it,
in the "Agent job protocol (43000-43999)" range: one agent or human asks another agent
to perform a unit of work, as an event distinct from an ordinary chat message. This
node describes the kind's wire contract and Buzz's current implementation of it — not
the feature built on top of it, and not the five sibling kinds in the same protocol
range.

## Scope and authority

**This node covers** kind 43001 itself: its persistence classification, its tag and
content shape as currently implemented (and, honestly, as currently *unspecified*
beyond what the codebase enforces), its access-control and storage treatment, and
which parts of the relay, `buzz-db`, desktop, and mobile already touch it as
producers, consumers, or both.

**Its authority is derived, not original.** `crates/buzz-core/src/kind.rs` is the
authoritative kind registry; `launchpad/docs/corpus/templates/event-kind.md` (id
`corpus-template-event-kind`) is the template this node is a realized instance of and
states the required-section shape below; `launchpad/docs/corpus/AGENTS.md` is the
corpus create/update/retire procedure. This node adds nothing to any of those — it is
the lookup the template asks a real event-kind instance to be.

| For | Read |
|---|---|
| Which sections an event-kind node must contain, and why | `launchpad/docs/corpus/templates/event-kind.md` |
| Buzz's kind registry (numbers, doc comments, classification helpers) | `crates/buzz-core/src/kind.rs` |
| The base Nostr event envelope, kind ranges, tag definition, primary source | `https://github.com/nostr-protocol/nips/blob/dabfcb2aaecf4fa374eda8b1232ab303a03f60ba/01.md` |
| Channel scoping and `h`-tag conventions | `AGENTS.md` (repo root), and `crates/buzz-relay/src/handlers/ingest.rs`'s `requires_h_channel_scope`/`is_global_only_kind` |
| Where the AI-agent actor relationship (buzz-acp, the job protocol as a concept) already sits in the corpus | `launchpad/docs/corpus/architecture/context/ai-agent.md` |

If this node and any of those disagree, **they win** — this one has drifted.

## 1. Title and kind identity

**Job request.** `KIND_JOB_REQUEST`, integer **43001**, defined in
`crates/buzz-core/src/kind.rs` under the "Agent job protocol (43000-43999)" section
comment, alongside five sibling lifecycle kinds this node does not document:
`KIND_JOB_ACCEPTED` (43002), `KIND_JOB_PROGRESS` (43003), `KIND_JOB_RESULT` (43004),
`KIND_JOB_CANCEL` (43005), `KIND_JOB_ERROR` (43006). `kind.rs`'s own doc comment on
`KIND_JOB_REQUEST` is one line: "An agent job was requested." — it states no tag or
content shape.

This node's `type` is `interfaces-events`, per the event-kind template's own
instruction to state that explicitly rather than let an instance author guess.

**Implemented, not merely proposed — but not yet produced.** The constant exists,
is wired into ingest metrics labeling, the Home Feed activity query, and both
desktop and mobile consumer UI (see sections 6 and *Producers and consumers* below).
No producer currently emits it: `desktop/src/features/notifications/lib/sound.ts`
states plainly that "nothing emits the events yet — buzz-acp publishes plain stream
messages." Read every claim below as "the shape the codebase is wired to expect,"
not as "the shape a real emitted event has been observed to have."

## 2. Referenced NIP

**None.** Kind 43001 conforms to no numbered NIP in `nostr-protocol/nips`, and no
`docs/nips/NIP-*.md` file in this repository specifies it either (checked directly:
zero of the 16 Markdown files under `docs/nips/` mention "43001" or the job-request
concept). The only documentation of intent is `kind.rs`'s own section comment: "Not
using NIP-90 kinds (5000-6999) — Buzz requires auth chains (depth ≤ 3, breadth ≤
10)." NIP-90 ("Data Vending Machines") is the existing community convention for
"one party requests work, another performs it" over Nostr; Buzz deliberately does
not reuse its kind range, for a reason stated in one clause and not expanded on
anywhere this node's author found. Per the event-kind template's own guidance, a
kind with no governing NIP and no `docs/nips/` proposal is a signal that a custom-NIP
document may need writing — this node does not write one; it states the gap.

## 3. Kind range and delivery classification

**Regular (persistent, non-replaceable) — by omission, not by an explicit NIP-01
range match.** NIP-01 (pinned at commit `dabfcb2aaecf4fa374eda8b1232ab303a03f60ba`)
defines exactly four numeric kind categories, and none of their stated bounds reaches
as high as 43001: regular is `1000<=n<10000 || 4<=n<45 || n==1 || n==2`, replaceable
is `10000<=n<20000 || n==0 || n==3`, ephemeral is `20000<=n<30000`, addressable is
`30000<=n<40000`. NIP-01 states no default rule for anything above 39999; its own
closing line is "These are just conventions and relay implementations may differ."

`kind.rs`'s three classification helpers each evaluate false for 43001:
`is_ephemeral` (20000–29999), `is_replaceable` (`{0, 3, 41} ∪ 10000..=19999`), and
`is_parameterized_replaceable` (30000–39999). Since those three predicates are the
whole of Buzz's kind-classification model and none matches, Buzz's implementation
treats 43001 as an ordinary persistent, non-replaceable event by the absence of any
special case — the same conclusion `kind.rs` reaches for every other 4xxxx-range
custom kind in this file, none of which is ephemeral, replaceable, or
parameterized-replaceable either. This is this node's own inference from reading
those three functions directly, not a line `kind.rs` states in so many words.

No mismatch exists between `kind.rs`'s classification and any NIP-01 assertion,
because NIP-01 makes no assertion at all for a kind this high — there is nothing to
cross-check 43001 against beyond Buzz's own three predicates.

## 4. Tag shape

**No dedicated ingest-side tag validation for kind 43001 was found.** Unlike
`KIND_PUSH_LEASE` or the NIP-29 moderation kinds, no function in
`crates/buzz-relay/src/handlers/ingest.rs` names `KIND_JOB_REQUEST` to enforce a
specific tag shape, cardinality, or required field beyond generic Nostr event
validation (signature, id, size limits). What follows is what the surrounding
machinery implies rather than what ingest enforces:

- **`h` (channel scope) — optional, not required.** `KIND_JOB_REQUEST` is a member
  of neither `is_global_only_kind` nor `requires_h_channel_scope` in `ingest.rs`.
  For such a kind the pipeline's default path runs `channel_id =
  extract_channel_id(&event)`: an `h` tag naming a channel UUID is honored if
  present, and `channel_id` is `None` (global) if absent. A job request MAY be
  channel-scoped and MAY be global; nothing in ingest forces either.
- **`d` (addressing tag) — absent, and correctly so.** 43001 is not
  parameterized-replaceable (section 3), so it takes no `d` tag; NIP-33 addressing
  does not apply.
- **`p` (recipient) — expected by consumers, not enforced by ingest.** The only
  tag-filtered consumer code found for this kind, `mobile/lib/features/activity/
  activity_provider.dart`'s `ActivityNotifier`, queries kinds `[43001..43006]`
  filtered by `#p` equal to the viewer's own pubkey, commented "agent job
  lifecycle events addressed to me." This strongly implies a job request is meant
  to carry a `p` tag naming the target agent (or human), but no ingest-side rule
  in `ingest.rs` requires it for 43001 specifically — this is a consumer-side
  expectation, not a validated producer contract (INFERENCE, confidence 0.7 in the
  ledger above).
- **No other reference tags** (`e`, `a`) are named by any source this node's
  author opened. Whether a job request should reference a prior thread root, a
  repo, or a workflow definition via `e`/`a` tags is unanswered by the codebase
  today — a gap, not a stated "no."

## 5. Content field semantics

**Unspecified.** No source this node's author opened — not `kind.rs`, not
`ingest.rs`, not a `docs/nips/` file, not a desktop or mobile consumer — states
what `content` on a kind:43001 event actually contains: plaintext, a stringified
JSON object with a stated field shape, or ciphertext. Consumers (desktop's
`inbox.ts`/`FeedSection.tsx`, mobile's `feed_item.dart`) render a fixed headline
string ("Job requested") for the kind and do not appear to parse `content` for
kind-specific fields; `feed_item.dart`'s `displayContent` getter falls back to
"No additional details." for empty content, the same fallback it uses for any
other kind with no dedicated case, which is consistent with content not carrying
a kind-specific structured shape that any current consumer relies on. This is
read from the absence of any kind-43001-specific content handling, not from a
statement that content is unstructured.

## 6. Access control and storage model

**No special gate — the uncontroversial default applies.** 43001 is a member of
none of `kind.rs`'s four named access-control sets (`AUTHOR_ONLY_KINDS`,
`RESULT_GATED_KINDS`, `P_GATED_KINDS`, `SHARED_GATED_KINDS`), each read in full.
Read access is therefore whatever the ordinary community/channel visibility model
grants: a member of the community (and, if the event is channel-scoped via an `h`
tag, a member of that channel) can read it, exactly like a stream message or forum
post.

**Stored, not ephemeral** (section 3), so it persists in the `events` table and
participates in ordinary `REQ`/`COUNT` history queries subject to the visibility
above.

**Searchable.** `schema/schema.sql`'s `events.search_tsv` generated column NULLs
the tsvector only for `kind IN (1059, 30179, 30300, 30350, 30622, 44100, 44101,
44200)`. 43001 is not in that list, so a stored kind:43001 event's `content` is
indexed by the ordinary `to_tsvector('simple', content)` branch and is
discoverable through NIP-50 full-text search — consistent with
`desktop/src/features/search/ui/SearchResultItem.tsx` rendering a kind:43001
search hit with the label "Agent job."

**Fan-out is the generic path, not a special one.** `crates/buzz-relay/src/
handlers/event.rs`'s `dispatch_persistent_event` is the kind-agnostic post-commit
seam for every stored event (its own doc comment: "Schedule post-commit
delivery/side effects for a stored event"); nothing found singles out 43001 for
different live fan-out, Redis publish, or multi-node delivery behavior.

**Audited like any other stored event, not specially.** `dispatch_persistent_event`
unconditionally calls `enqueue_event_created_audit`, which logs a
`buzz_audit::AuditAction::EventCreated` entry recording the resolved actor pubkey,
the event id, and the numeric kind. No kind-specific audit branch exists for
43001 or its five sibling job kinds — it receives the same generic per-event audit
entry every other persistent kind receives.

**Metrics recognize it as a distinct group.** `bounded_kind_label` in the same
file assigns the whole range `43001..=43006` its own literal metrics label rather
than the catch-all `"other"` bucket, so Prometheus-style cardinality bounding
already treats the job protocol as one intentional group, independent of whether
anything emits events in that range yet.

## 7. Worked example

**Illustrative only — no producer exists to observe a real one from** (see
*Title and kind identity*). This example exercises the tag shape section 4
actually establishes (an optional `h` tag; no `d` tag) and marks `content` as
unspecified rather than inventing a schema section 5 found no source for:

```jsonc
{
  "id": "<64-hex event id>",
  "pubkey": "<64-hex requester pubkey>",
  "created_at": 1769990000,
  "kind": 43001,
  "tags": [
    ["p", "<64-hex target agent pubkey>"],
    ["h", "<channel-uuid>"]
  ],
  "content": "<unspecified — no source read while authoring this node states a required shape; treat as opaque/plaintext until a spec exists>",
  "sig": "<...>"
}
```

The `p` and `h` tags above are each drawn from a different, non-authoritative
source: `p` from `activity_provider.dart`'s consumer-side filter (section 4,
INFERENCE, confidence 0.7), `h` from `ingest.rs`'s default channel-scoping path
(section 4, FACT). A minimal event omitting both — `tags: []` — is equally valid
under everything this node's author found: nothing in `ingest.rs` rejects a
kind:43001 event with no tags at all.

## 8. Versioning and supersession

**None.** `kind.rs` records no prior kind number for `KIND_JOB_REQUEST` and no
comment describing a renumbering, unlike several other custom kinds in the same
file (e.g. `KIND_STREAM_MESSAGE_V2`'s "V1 used kind:10001 — wrong"). 43001 appears
to be the kind's only assigned number to date.

## 9. Relationships

This node declares two:

- **`implements` → `corpus-template-event-kind`.** This node is the realized
  instance the template's own text anticipates, per `relationships.schema.json`'s
  directionality for `implements` ("source is the concrete realization of
  target").
- **`references` → `architecture-context-ai-agent`.** That node names the
  43000-43999 range as "an agent job protocol... through which one agent (or a
  human) can request work from an agent as a distinct concept from an ordinary
  chat message" and explicitly defers the protocol's message shapes to "a future
  interfaces/events-level corpus node, not yet authored." This node cites it as
  supporting context for the actor-level relationship the protocol sits inside;
  `references` carries no ownership or currency dependency in either direction,
  per `relationships.schema.json`.

No `depends-on` edge is declared to any of the five sibling job kinds (43002-43006):
none of them has a corpus node yet to target, and `relationships[].target` naming
an id no loaded node carries is a hard validation error.

## Scope and omissions

**This document covers** kind 43001's identity, classification, tag and content
shape as currently implemented (and, where unspecified, says so), access control,
storage, fan-out, search, and audit treatment, and its current producer/consumer
surface.

**Producers and consumers, stated plainly because the DoD asks for it directly:**

| Role | Who, today |
|---|---|
| Producer | **None.** `sound.ts`'s own comment states nothing emits kind 43001-43006 events yet; `buzz-acp` (the AI-agent bridge named in `architecture-context-ai-agent`) is the architecturally implied future producer but currently publishes plain stream messages instead. |
| Consumer (query/storage) | `crates/buzz-db/src/store/feed.rs`'s `build_activity_query` (Home Feed activity) |
| Consumer (relay-side) | `crates/buzz-relay/src/handlers/event.rs`'s generic `dispatch_persistent_event`/`bounded_kind_label` paths (no kind-specific relay logic) |
| Consumer (desktop) | `desktop/src/shared/constants/kinds.ts`, `inbox.ts`, `FeedSection.tsx`, `SearchResultItem.tsx`, `sound.ts` (notification slot wired, disabled) |
| Consumer (mobile) | `mobile/lib/shared/relay/nostr_models.dart`, `activity_provider.dart`, `feed_item.dart` |

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `KIND_JOB_ACCEPTED` (43002), `KIND_JOB_PROGRESS` (43003), `KIND_JOB_RESULT` (43004), `KIND_JOB_CANCEL` (43005), `KIND_JOB_ERROR` (43006) as their own event-kind nodes | Not yet filed as separate tasks at the recorded revision — documenting them here would fold five more independently maintainable ideas into one node, which `corpus-standard-atomicity` (requirement A3) forbids. |
| The full auth-chain rule Buzz uses instead of NIP-90 (depth ≤ 3, breadth ≤ 10) — what it means, where it is enforced, and by what code | Not found by this node's author in the sources opened; `kind.rs`'s section comment states the rule's headline numbers but no implementation was located. A gap, not asserted as absent. |
| `buzz-acp`'s and `buzz-agent`'s internal request/response loop, and how a future producer would actually construct and sign a kind:43001 event | `architecture-context-ai-agent`'s own gap table already defers `buzz-acp`'s internal modules to "a future container-level corpus node, not yet authored" |
| Whether a `docs/nips/NIP-JR.md`-style proposal document should exist for this protocol before or alongside a corpus node | Not decided by any source this node's author opened; the event-kind template treats a `docs/nips/` file as optional per-kind, not mandatory |
| What `content` should contain once a producer exists | Section 5 states this is unspecified today; whoever implements the first producer settles it, and this node will need updating once they do (per `AGENTS.md`'s *Updating a node* re-verification rule) |

**Expected but not verified when this node was written:**

- **No real kind:43001 event has ever been observed on the wire.** Every tag and
  content claim above is read from consumer expectations and ingest defaults, not
  from a producer's actual output, because no producer exists yet. The worked
  example in section 7 is explicitly illustrative for this reason.
- **Whether any conformance test or fixture exercises kind 43001 specifically**
  was not established. A repository-wide search for `43001`/`JOB_REQUEST` across
  `.rs`, `.ts`, `.tsx`, and `.dart` files surfaced the consumer and registry sites
  cited above; no dedicated ingest or conformance test naming the kind was found
  among them, so this node makes no conformance/test-linking claim beyond what is
  cited.
- **Whether the `p`-tag addressing pattern inferred in section 4 is the intended
  contract or merely what one consumer happens to assume** was not resolved —
  only one consumer's filter logic was found to reason from, and no producer
  exists to confirm it against.
