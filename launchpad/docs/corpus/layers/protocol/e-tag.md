---
id: layers-protocol-e-tag
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision 29ca9b189bd3f639ba09c972b57c70538c0860c6."
    entry_class: FACT
    evidence:
      - "commit 29ca9b189bd3f639ba09c972b57c70538c0860c6"
  - statement: "Buzz parses NIP-10 positional markers on `e` tags in one shared module, crates/buzz-core/src/nip10.rs, which exposes a ThreadMarkers struct carrying only `root` and `reply`, the parse_thread_markers and parse_thread_markers_from_parts entry points, and ThreadMarkers::resolve()."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/nip10.rs"
  - statement: "The parser considers an `e` tag only when it has at least four parts and its second part is exactly 64 ASCII-hex characters, reads the marker from the fourth part, and matches only the literals \"root\" and \"reply\" — every other marker value, including NIP-10's third marker `mention`, falls through the wildcard arm and is discarded."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/nip10.rs"
  - statement: "A bare, unmarked `[\"e\", <id>]` tag produces no thread markers at all, asserted by the module's own bare_e_tag_without_marker_is_ignored test, and a marker whose event id is malformed is ignored rather than treated as a thread link, asserted by malformed_id_is_ignored_for_both_markers."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/nip10.rs"
  - statement: "ThreadMarkers::resolve() collapses the two markers into a reply's (root, parent) pair by three rules — root plus reply yields (root, reply), a lone reply yields (reply, reply) because a direct reply's target is itself the thread root, and a lone root or neither marker yields None because the event is top-level."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/nip10.rs"
  - statement: "Five crates call the shared parser rather than re-deriving marker semantics: the relay ingest resolver, the workflow reply predicate, the ACP queue, the CLI's thread-reference builder, and the SDK broker's action outcomes."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-workflow/src/lib.rs"
      - "crates/buzz-acp/src/queue.rs"
      - "crates/buzz-cli/src/commands/messages.rs"
      - "crates/buzz-sdk/src/broker/actions/outcomes.rs"
  - statement: "The workflow engine's event_is_reply predicate delegates to the same shared parser so it stays in lockstep with ingest, and its own tests assert that a lone `root` marker is top-level and that a bare unmarked `e` tag — described there as a plain mention or quote — is not a thread reply."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs"
  - statement: "The relay's resolve_nip10_thread_meta rejects a client-supplied reply on three distinct grounds — a parent event in a different channel, a `root` marker that disagrees with the parent's recorded or derived ancestry, and a resulting depth greater than 100."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "Threading is not the `e` tag's only job in Buzz: reactions take their target from the last `e` tag and are rejected outright when none is present, standard deletions and NIP-29 delete-event commands must reference exactly one target across their `e` and `a` tags combined, and a stream-message edit's ownership check requires an `e` tag naming the edit target."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "Because kind:7 reactions and kind:5 deletions carry an `e` tag and no `h` tag, the relay derives their channel from the target event the `e` tag names, and buzz-core's filter matcher carries a matching #h fallback that consults the stored channel_id only when an event has no `h` tags at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-core/src/filter.rs"
  - statement: "CLAUDE.md states that channels use `h` tags, the NIP-29 group tag, not `e` tags, and that filters and queries must scope to `h` tags when operating within a channel."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "NIP-CW, one of Buzz's own NIPs, defines an event as a reply if and only if it carries a NIP-10 marked `e` tag with the `reply` marker, explicitly excluding an event carrying only a root-marked tag, unmarked positional e-tags, or no e-tags at all, and specifies a two-hop auxiliary closure of reactions, deletions and edits that reference window rows by `e` tag."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-CW.md"
  - statement: "NIP-IA places a Buzz-specific `proof` value in the `e` tag's marker slot, deliberately kept distinct from the unmarked request `e` tag in the same event, so a Buzz event may carry marker values that are not NIP-10 thread markers."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-IA.md"
  - statement: "The relay pushes a `#e` filter down into SQL as a JSONB containment predicate, and migration 0004 creates idx_events_tags_gin over the events table's tags column using jsonb_path_ops specifically to support the `tags @> [[\"e\", <hex>]]` shape that every #e fan-out uses."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs"
      - "migrations/0004_events_tags_gin.sql"
  - statement: "The relay's integration suite exercises the marked `e` tag end to end in four tests — test_nip10_thread_reply_creates_metadata, test_nip10_unknown_parent_rejected, test_nip10_root_mismatch_rejected and test_nip10_thread_reply_not_in_top_level — each constructing its tags with Tag::parse([\"e\", <id>, \"\", <marker>])."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_nostr_interop.rs"
  - statement: "Storing a reply increments reply_count on the parent event and descendant_count on the thread root inside a single database transaction, which is the thread-counter capability's subject rather than this node's."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/thread.rs"
  - statement: "The upstream Nostr specifications are not present in this repository — docs/nips/ contains only Buzz's own two-letter NIPs — so no claim about what NIP-01 or NIP-10 themselves require can be verified against a file here, and the marker vocabulary described in this node is Buzz's implementation of that convention rather than a reading of the standard's text."
    entry_class: INFERENCE
    evidence:
      - "docs/nips/NIP-CW.md"
      - "crates/buzz-core/src/nip10.rs"
    confidence: 0.9
  - statement: "Because the shared parser discards any marker value other than root and reply, a client that emits NIP-10's `mention` marker gets that tag treated by Buzz exactly as an unmarked `e` tag would be — present on the wire and inert for threading — but no source in this repository states that ignoring `mention` was a deliberate decision rather than an unimplemented case."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/nip10.rs"
      - "docs/nips/NIP-CW.md"
    confidence: 0.75
relationships:
  - type: implements
    target: corpus-template-concept
  - type: references
    target: capabilities-messaging-reply
  - type: references
    target: capabilities-messaging-thread
  - type: references
    target: capabilities-messaging-thread-counters
  - type: references
    target: capabilities-messaging-reaction
  - type: references
    target: implementation-crates-buzz-core
  - type: references
    target: implementation-crates-buzz-relay
  - type: references
    target: layers-data-deletion
  - type: references
    target: layers-data-postgres-indexes
  - type: references
    target: architecture-flows-event-ingestion
  - type: references
    target: verification-contracts-nostr
---

# The `e` tag

The `e` tag is Buzz's **event-to-event reference**: a tag on one Nostr event whose
value is the id of *another* event, declaring that this event is about that one.
It is the single primitive underneath replies, threads, reactions,
deletions and edits — five features that would otherwise each need their own way
of saying "the event I mean is this one."

This node explains what the tag is and how Buzz reads it. It is a protocol-layer
node: the *capabilities* built on top of it have their own canonical nodes, named
in **Relationships** below, and this document links to them rather than repeating
what they say.

## Definition

**An `e` tag is a tag array whose first element is the literal string `e` and
whose second element is a hex-encoded Nostr event id.** Optional third and
fourth elements carry a relay hint and a *marker* — a short keyword saying what
kind of reference this is. In Buzz the shape that carries meaning is the
four-element, marked form:

```
["e", "<64-hex event id>", "<relay hint, often empty>", "<marker>"]
```

### What the `e` tag is not

The corpus and the codebase both distinguish `e` from three neighbouring things
it is easy to conflate. All three are the subject of their own sibling nodes;
what follows is the boundary, not their content.

| Not this | Because |
|---|---|
| **The `h` tag** | `h` names the *channel* an event belongs to — the NIP-29 group tag. `CLAUDE.md` states this plainly: channels use `h` tags, not `e` tags, and filters operating inside a channel must scope on `h`. An `e` tag names an *event*, never a container. |
| **The `p` tag** | `p` names a *pubkey* — a person or agent. `e` names an event. An event referencing both is saying "about that message, involving that person." |
| **The event id itself** | The id is the event's own identity, computed over its content. The `e` tag is a *pointer to* another event's id, carried in the tag list. |

The `h`/`e` split is not merely conventional — the relay leans on it. Reactions
(kind:7) and deletions (kind:5) carry an `e` tag and **no** `h` tag at all, so the
relay derives their channel by looking up the event the `e` tag names. `buzz-core`'s
filter matcher carries the mirror of that rule: a `#h` filter falls back to the
event's stored `channel_id` only when the event has no `h` tags whatsoever, and an
event that *does* carry `h` tags is matched strictly against them.

## Markers: what Buzz actually reads

All NIP-10 marker parsing in Buzz lives in **one** module,
`crates/buzz-core/src/nip10.rs`, so that no consumer can invent its own reading of
ancestry. Its own doc comment says a second hand-rolled copy is exactly how two
consumers previously drifted apart on marker semantics.

The parser recognises a tag only when it has **at least four elements** and its
event id is **exactly 64 ASCII-hex characters**. It then matches the fourth
element against two literals:

- `root` — the first event in the thread.
- `reply` — the immediate parent this event answers.

**Every other marker value is discarded by a wildcard arm.** That includes
NIP-10's third marker, `mention`: a search of the whole Rust tree finds no
handling of it anywhere. So far as threading is concerned a `mention`-marked
`e` tag is inert — indistinguishable in effect from an unmarked one. No
ingest path was found that rejects an unrecognised marker, but that is an
absence of evidence rather than a verified acceptance rule; see *Scope and
omissions*.

Two shapes are likewise inert:

- **An unmarked `["e", <id>]` tag** yields no markers. The module's own
  `bare_e_tag_without_marker_is_ignored` test asserts this, and Buzz's `NIP-CW`
  states the same rule normatively: an event carrying only unmarked positional
  `e` tags is **not** a reply. The workflow engine reaches the same conclusion
  through the same parser, and names the case in its own test comment: a bare
  `e` tag with no marker is *a plain mention or quote*, not a thread link.
- **A marker with a malformed id** is ignored rather than treated as a broken
  thread link, asserted by `malformed_id_is_ignored_for_both_markers`.

### The three states a reader must distinguish

`ThreadMarkers::resolve()` is the one place those markers become a `(root, parent)`
pair. Its three outcomes are the whole comparison:

| Markers present | Resolves to | Meaning |
|---|---|---|
| `root` **and** `reply` | `(root, reply)` | A nested reply; it names both its thread and its immediate parent. |
| `reply` only | `(reply, reply)` | A direct reply to a thread root — the target *is* the root. |
| `root` only, or neither | `None` | Top-level. A lone `root` tag never anchors a reply. |

The third row is the counter-intuitive one and the one worth carrying: **a `root`
marker on its own does not make an event a reply.** Buzz's own `NIP-CW` states the
same predicate from the wire side, and the relay's ingest path implements it.

Buzz also uses the marker slot for values that are not NIP-10 markers at all:
`NIP-IA` specifies a `proof` marker on an `e` tag, deliberately kept distinct from
the unmarked request `e` tag in the same event. The marker slot is a Buzz
extension point, not a closed NIP-10 vocabulary.

## What the relay does with a marked `e` tag

When a client submits an event whose markers resolve, the relay's ingest resolver
validates the claimed ancestry rather than trusting it. It rejects on three
grounds:

- the parent event lives in **a different channel** than the incoming event;
- the `root` marker **disagrees** with the parent's recorded (or, for un-indexed
  parents, derived) ancestry;
- the resulting **depth exceeds 100**.

That last rule matters for anyone reasoning about `e`-tag chains: ancestry in Buzz
is bounded, not arbitrary.

Storing an accepted reply then updates `reply_count` on the parent and
`descendant_count` on the root in one transaction — see
`capabilities-messaging-thread-counters`, which owns that behaviour.

## Use cases

Understanding the `e` tag is what lets you:

- **Tell a reply from a top-level message without asking the database.** The
  predicate is entirely in the tags, which is why `NIP-CW` can define channel
  windows reproducibly from wire data alone.
- **Debug a reply that "didn't thread."** The usual causes are all `e`-tag shape
  problems: an unmarked tag, a `root`-only tag, a marker Buzz does not read, or an
  id that is not 64 hex characters. None of these produce an error — they produce
  a message that silently lands at top level.
- **Query for everything referring to an event.** A `#e` filter is pushed down
  into SQL as a JSONB containment predicate, and migration
  `0004_events_tags_gin.sql` exists specifically to make that shape fast; see
  `layers-data-postgres-indexes`.
- **Read reaction, deletion and edit handling correctly.** Each locates its target
  through an `e` tag, with its own rule: a reaction takes the **last** `e` tag and
  is rejected without one; a deletion must reference **exactly one** target across
  its `e` and `a` tags combined; an edit's ownership check requires an `e` tag
  naming the target.

## Verification

The relay's Nostr-interop suite exercises the marked `e` tag end to end in four
tests — a reply creating thread metadata, an unknown parent being rejected, a
`root`/parent mismatch being rejected, and a threaded reply staying out of the
top-level window. The shared parser carries its own unit tests for marker
selection, id validity and each `resolve()` branch. `verification-contracts-nostr`
owns the broader Nostr contract picture.

## Relationships

- `implements` `corpus-template-concept` — this node follows that template's
  required sections.
- `references` `capabilities-messaging-reply`, `capabilities-messaging-thread`,
  `capabilities-messaging-thread-counters` and `capabilities-messaging-reaction` —
  the capabilities built on this primitive. They own how a reply is composed and
  sent, what a thread is as a user-facing feature, how counters are maintained,
  and how reactions behave. This node owns only the tag.
- `references` `implementation-crates-buzz-core` and
  `implementation-crates-buzz-relay` — the crates holding the parser and the
  ingest validation respectively.
- `references` `layers-data-deletion` — deletion semantics, which consume the tag.
- `references` `layers-data-postgres-indexes` — the index supporting `#e` lookups.
- `references` `architecture-flows-event-ingestion` — the pipeline an `e`-tagged
  event travels.
- `references` `verification-contracts-nostr` — the Nostr contract this tag sits in.

## Scope and omissions

### What this node does not cover, and who owns it

- **How a reply is composed and submitted** by the CLI, desktop or mobile clients
  — `capabilities-messaging-reply`.
- **Threads as a user-facing capability**, including depth rendering and
  broadcast surfacing — `capabilities-messaging-thread`.
- **`reply_count` / `descendant_count` maintenance and the kind:39005 summary
  overlay** — `capabilities-messaging-thread-counters`.
- **Reaction semantics** beyond the fact that a reaction locates its target via
  `e` — `capabilities-messaging-reaction`.
- **Deletion semantics** beyond the target-cardinality rule — `layers-data-deletion`.
- **Event tags in general, the `h` tag, the `p` tag, and the event id.** Each is a
  separate protocol-layer subject. At the recorded revision none of those nodes is
  merged, so this node draws the boundary in prose above and declares no
  relationship edge to them; the edges belong in a later pass once they exist.

### What I expected to verify and could not

- **The text of upstream NIP-01 and NIP-10 is not in this repository.** `docs/nips/`
  holds only Buzz's own two-letter NIPs (`NIP-CW`, `NIP-IA`, and siblings). Every
  claim above about marker vocabulary is therefore a claim about **Buzz's
  implementation** of the NIP-10 convention, read from `crates/buzz-core/src/nip10.rs`
  and `docs/nips/NIP-CW.md`. Where this node says "NIP-10's third marker,
  `mention`", it is reporting the marker name the Buzz parser's own wildcard arm
  declines to handle, not quoting the standard.
- **Whether ignoring the `mention` marker is deliberate.** The parser discards it
  silently and no comment, decision record or issue found in this repository
  states why. That claim is recorded as an INFERENCE, not a FACT, and the
  behaviour is described rather than justified.
- **Whether an unrecognised marker value is accepted at ingest.** Reading
  `crates/buzz-relay/src/handlers/ingest.rs` turned up no validation that
  rejects an `e` tag on the basis of its marker, but proving acceptance needs a
  live relay submission this node did not make. The body states only what the
  parser does with such a tag, not what the relay does with the event carrying it.
- **Runtime behaviour was not executed.** Every claim here comes from reading
  source, tests and migrations at the recorded revision. The four interop tests
  named above require a running Postgres and Redis; they were read, not run, so
  this node asserts what they assert, not that they currently pass.
- **Client-side tag construction was surveyed only far enough to confirm the
  shared parser has five Rust consumers.** The desktop TypeScript and mobile Dart
  paths that build `e` tags were not read for this node; if their marker rules
  ever diverge from `nip10.rs`, nothing here would catch it.
