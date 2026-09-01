---
id: interfaces-nostr-buzz-nips-nip-mp
type: interfaces-events
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 650354eab8d41ab6ce1a71de079a6c6d95c69052 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 650354eab8d41ab6ce1a71de079a6c6d95c69052"
  - statement: "docs/nips/NIP-MP.md is Buzz's own custom NIP, 'Multi-Repository Projects', marked draft/optional/relay, defining kind:30621 as an addressable event grouping kind:30617 (NIP-34) repository announcements into a named project container."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-MP.md"
  - statement: "docs/nips/NIP-MP.fixtures.json (ingest conformance: 11 accepted / 20 rejected cases) and docs/nips/NIP-MP.fold-fixtures.json (12 client-fold cases) exist alongside the spec as its machine-checkable oracle."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-MP.fixtures.json"
      - "docs/nips/NIP-MP.fold-fixtures.json"
  - statement: "KIND_PROJECT is defined as the u32 constant 30621 in buzz-core's kind registry, with a compile-time assertion that it falls in the addressable-event range 30000-39999."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:632"
      - "crates/buzz-core/src/kind.rs:864"
  - statement: "The relay's ingest handler implements fn validate_project_envelope(event: &Event), which parses d, a (member), name, description, buzz-channel and buzz-visibility tags and enforces the spec's eight envelope rules (d-cardinality, d-empty, member-cap, member-tag-arity, member-coordinate-malformed, member-duplicate, metadata-cardinality, metadata-length) before an event of kind 30621 is accepted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1609"
  - statement: "The relay's own unit tests load the shared fixture file directly -- include_str!(\"../../../../docs/nips/NIP-MP.fixtures.json\") -- and run every case through validate_project_envelope, asserting each fixture's expected accept/reject outcome; the spec file is therefore a live test oracle, not descriptive-only documentation."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:5332"
      - "crates/buzz-relay/src/handlers/ingest.rs:1566"
  - statement: "buzz-sdk exposes its own validate_project_envelope(tags, content) and build_project(...) / build_project_with_tags(...) builders, plus a ProjectMemberCoord type whose parse_full parses and validates a member a-tag coordinate (30617:<owner-hex>:<repo-d>); buzz-sdk's unit tests build events with these and assert the resulting tag shape."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:2001"
      - "crates/buzz-sdk/src/builders.rs:2097"
      - "crates/buzz-sdk/src/builders.rs:2223"
      - "crates/buzz-sdk/src/builders.rs:2239"
  - statement: "crates/buzz-test-client/tests/e2e_project.rs contains end-to-end tests exercising kind:30621 over a live relay connection, including test_project_publish_and_query_returns_cross_owner_members, test_project_replacement_keeps_only_newest_for_same_author_and_d, test_project_same_d_under_two_authors_are_independent, and test_project_tombstone_deletes_coordinate_and_spares_members -- confirming cross-owner membership, NIP-01 replacement semantics, and NIP-09 tombstone-without-cascade are exercised against a running relay, not only unit-tested."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_project.rs:153"
      - "crates/buzz-test-client/tests/e2e_project.rs:198"
      - "crates/buzz-test-client/tests/e2e_project.rs:248"
      - "crates/buzz-test-client/tests/e2e_project.rs:307"
  - statement: "The relay-side deletion authority extension the spec describes -- a kind:5 naming a project's coordinate is honored when signed by the project's own signer OR by that signer's registered NIP-OA owner -- is implemented in validate_standard_deletion_event, which resolves the deletion's effective author and, for an a-tag (addressable-event) deletion, verifies that author against the target's ownership."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs:229"
  - statement: "The inclusive created_at <= <deletion> tombstone comparison the spec's Relay Processing Algorithm section requires (so a deletion never removes a version newer than itself) is implemented in soft_delete_by_coordinate, an UPDATE ... WHERE ... created_at <= $5 query."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs:866"
  - statement: "docs/nips/NIP-MP.md's own prose cites this function's path as crates/buzz-db/src/event.rs, but no file exists at that path in this checkout; the function is actually defined in crates/buzz-db/src/store/event.rs. The spec's implementation path is stale relative to the current module layout; this node cites the verified path instead of repeating the spec's citation."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-db/src/store/event.rs:866"
      - "docs/nips/NIP-MP.md"
    confidence: 0.9
  - statement: "buzz-cli's crates/buzz-cli/src/commands/projects.rs implements agent-facing project commands (cmd_create, cmd_get, cmd_list, cmd_add_repo, cmd_remove_repo, cmd_update, cmd_delete) built on the same builders and validation, confirming kind:30621 is reachable from the CLI surface as well as the relay's raw event endpoints."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/projects.rs:360"
      - "crates/buzz-cli/src/commands/projects.rs:462"
      - "crates/buzz-cli/src/commands/projects.rs:485"
      - "crates/buzz-cli/src/commands/projects.rs:510"
      - "crates/buzz-cli/src/commands/projects.rs:522"
      - "crates/buzz-cli/src/commands/projects.rs:588"
      - "crates/buzz-cli/src/commands/projects.rs:692"
  - statement: "The spec states that a project's authority begins and ends at the container: the signer gains no edit, delete, push or administration right over any member repository, and that push policy reads a member repository's own kind:30617 buzz-channel binding rather than any binding a project supplies, citing crates/buzz-relay/src/api/git/policy.rs as the enforcement point."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-MP.md"
      - "crates/buzz-relay/src/api/git/policy.rs"
  - statement: "No node exists yet under launchpad/docs/corpus/interfaces/ for any other Buzz-custom NIP or Nostr interface, so this node declares no relationships -- there is no merged sibling id to target, and the corpus's own AGENTS.md treats an invented target as a hard validation error."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
---

# Interface: NIP-MP — Multi-Repository Projects (`kind:30621`)

Buzz's own custom Nostr interface for grouping repositories into a named,
addressable project container. This node documents the wire contract: what a
`kind:30621` event carries, how a relay accepts or rejects one, and how
authority, versioning and ordering work. It does not restate the client-side
rendering algorithm (the fold) in full — that is cited, not duplicated, since
the authoritative text already lives in the spec.

**Authoritative spec**: [`docs/nips/NIP-MP.md`](../../../../../../docs/nips/NIP-MP.md).
**Machine conformance oracle**: [`docs/nips/NIP-MP.fixtures.json`](../../../../../../docs/nips/NIP-MP.fixtures.json)
(ingest accept/reject cases) and
[`docs/nips/NIP-MP.fold-fixtures.json`](../../../../../../docs/nips/NIP-MP.fold-fixtures.json)
(client-fold placement cases).

## Kind

| Kind | Name | Signer | Class | Purpose |
|------|------|--------|-------|---------|
| `30621` | Project | user | addressable (NIP-01) | A named grouping of `kind:30617` repository announcements |

`KIND_PROJECT` is registered as `30621` in Buzz's kind constant table, in the
NIP-34 git block between `30617` (repository) and `30618` (repository state).

## Inputs / Messages — event format

```jsonc
{
  "kind": 30621,
  "pubkey": "<project-signer-pubkey-hex>",
  "content": "",
  "tags": [
    ["d", "platform"],
    ["name", "Platform"],
    ["description", "Relay, desktop, and mobile for the platform team."],
    ["a", "30617:<owner-a-pubkey-hex>:buzz"],
    ["a", "30617:<owner-b-pubkey-hex>:buzz-infra"],
    ["buzz-channel", "<channel-uuid>"],
    ["buzz-visibility", "listed"]
  ]
}
```

| Tag | Cardinality | Meaning |
|-----|-------------|---------|
| `d` | exactly 1, non-empty | Project slug; the NIP-01 addressable identifier |
| `name` | 0 or 1 | Display name; clients fall back to `d` when absent |
| `description` | 0 or 1 | Free text |
| `a` | 0 to 64 | One member repository coordinate each, `30617:<owner-hex>:<repo-d>` |
| `buzz-channel` | 0 or 1 | Channel UUID; metadata only, at most 256 bytes |
| `buzz-visibility` | 0 or 1 | `listed` (default) or `unlisted`, at most 256 bytes |

`content` carries no meaning; writers emit the empty string and readers
ignore it. Unrecognized tags are ignored, not rejected. The relay validator
implementing this shape parses exactly these tag names and applies the
envelope rules below.

## Outputs / Responses

A `kind:30621` event is retrieved like any other Nostr event: NIP-01 `REQ`
filters over WebSocket, or the equivalent `POST /query` / `POST /count` HTTP
bridge (see the repo-wide "Nostr-first HTTP surface" convention). Ingest is
`POST /events` or the WebSocket `EVENT` message; a rejected envelope returns a
Nostr `OK` message with `false` and the specific rejection reason. There is
no project-specific read endpoint — resolution (querying by `d` tag,
resolving `a`-tag member coordinates, applying the client-side fold) is a
client responsibility described in the spec's Client Behavior section.

## Error / Rejection Behavior

The relay validator enforces eight envelope rules, in this order, before
storing an event:

1. `d-cardinality` — exactly one `d` tag.
2. `d-empty` — the `d` value is non-empty (bounded by the relay's generic
   1024-byte `d`-tag limit).
3. `member-cap` — at most 64 `a` tags, counting every tag rather than
   distinct coordinates.
4. `member-tag-arity` — every `a` tag has exactly two or three elements.
5. `member-coordinate-malformed` — every `a` tag's coordinate parses as
   `30617:<64-lowercase-hex-owner>:<repo-d>`.
6. `member-duplicate` — no two `a` tags name the same coordinate.
7. `metadata-cardinality` — at most one each of `name`, `description`,
   `buzz-channel`, `buzz-visibility`.
8. `metadata-length` — `name` ≤ 256 bytes, `description` ≤ 2048 bytes,
   `buzz-channel` ≤ 256 bytes, `buzz-visibility` ≤ 256 bytes.

Rules 3–6 run in that order so an oversized tag list is refused on count
before any per-tag parse is attempted. Duplicates are rejected, never
normalized — a relay cannot dedupe tags inside a signed event without
invalidating its signature. The relay's ingest validator implements and unit
tests all eight rules against the shared fixture file.

The relay never checks whether the signer owns, maintains, or otherwise
relates to a referenced member repository — referencing another owner's
repository is legal, and rejected only for the shape/cardinality reasons
above, never for lack of a relationship to the member.

## Authentication / Authorization

Writing a `kind:30621` event requires the `repos:write` scope, the same scope
required for `kind:30617` and `kind:30618` — a client authorized to announce
repositories is authorized to group them. The relay performs no membership
authorization: publishing a project naming someone else's repository is
legal at ingest, because membership by itself grants nothing over the member
repository (no edit, delete, push, or administration right). Push policy for
a repository's own git operations reads only that repository's own
`kind:30617` `buzz-channel` binding; a project's own `buzz-channel` tag is
metadata and is never consulted by push policy.

Deletion authorization is wider than replacement: replacing a project's
coordinate is signer-only on every relay (NIP-01 keys the coordinate on the
pubkey). Deleting it (NIP-09 `kind:5` naming the coordinate) is accepted from
the signer, or — as a Buzz-wide relay extension applied uniformly to every
kind, not specially to projects — from that signer's registered NIP-OA
owner. Deleting a project deletes only the `kind:30621` container; member
repositories, their refs, channels and protections are untouched.

## Versioning / Compatibility

`kind:30621` is an addressable event per NIP-01 (`30000 ≤ n < 40000`),
addressed by `(pubkey, 30621, d)`; two signers may reuse the same `d` value
as two distinct projects. `30621` was placed in the NIP-34 git block
(`30617`, `30618`) as the one free kind number between `30617`/`30618` and
`30622` (`KIND_DM_VISIBILITY`, NIP-DV) in Buzz's own kind registry, and the
spec records that it checked — as of authoring — that neither the upstream
`nostr-protocol/nips` kind table nor nostrbook.dev's kind registry had
assigned `30621`; both checks are advisory rather than authoritative
allocation, so a future upstream assignment would be a collision Buzz
absorbs the same way it already does for its other custom kinds. Unrecognized
tags on the event MUST be ignored by readers rather than treated as a
rejection cause, which is what lets a future writer add metadata without
invalidating events for older readers. A third-party NIP-34 client that does
not know `kind:30621` still discovers and renders each member `kind:30617`
individually — nothing about the standard NIP-34 repository events degrades
in that client.

## Ordering / Idempotency

Replacement follows NIP-01 with no special case: for a given `(pubkey,
30621, d)`, the event with the newest `created_at` wins, and one pubkey can
never overwrite another's coordinate. Deletion follows NIP-09 with the
inclusive-bound rule verified above: a tombstone removes only versions whose
`created_at` is at or before the deletion's own `created_at`, so a delayed or
replayed tombstone signed before the current head does not remove it. The
end-to-end test suite exercises both properties against a running relay:
replacement keeps only the newest event for one `(author, d)`, and two
authors reusing the same `d` are independent addressable coordinates.

## Example — valid event

```jsonc
{
  "kind": 30621,
  "pubkey": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "content": "",
  "tags": [
    ["d", "platform"],
    ["name", "Platform"],
    ["a", "30617:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb:buzz"],
    ["buzz-visibility", "listed"]
  ]
}
```

One `d` tag, a well-formed 64-hex-char member coordinate naming kind `30617`,
and no duplicate metadata tags — this satisfies all eight envelope rules and
is accepted.

## Example — failure

```jsonc
{
  "kind": 30621,
  "pubkey": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "content": "",
  "tags": [
    ["d", "platform"],
    ["a", "30618:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb:buzz"]
  ]
}
```

Rejected under `member-coordinate-malformed`: the coordinate's kind segment
is `30618` (repository *state*), not the required literal `30617`
(repository *announcement*) — a project groups announcements, and a
coordinate naming any other kind is malformed regardless of otherwise
correct shape.

## Relation to other NIPs

Depends on NIP-01 (addressable events, `a`-tag grammar, replacement), NIP-34
(the `kind:30617` repositories a project groups), and NIP-09 (deletion, with
Buzz's owner-deletion and inclusive-timestamp extensions above). Interacts
with NIP-29 (the channel a project's `buzz-channel` names) and NIP-OA (owner
attestation, consulted only for who besides the signer may delete a
project). None of these are separately covered here; each is its own
corpus surface once documented.

## Scope and omissions

**This node covers** the `kind:30621` event shape, the relay's eight ingest
validation rules, authorization (write scope, membership non-authorization,
deletion authority), versioning/kind-allocation, and replacement/deletion
ordering — the wire-level interface contract.

**This node does not cover, by design:**

- The client-side rendering fold (listing eligibility, claim authority,
  pagination modes) in full — that algorithm is the spec's own Client
  Behavior section and `NIP-MP.fold-fixtures.json`; restating it here would
  duplicate rather than link to canonical content.
- The `buzz-cli` `projects` subcommand surface as its own ergonomics
  contract — it is a separate, independently maintainable concern from the
  wire format this node documents.
- Whether `30621` should ever be proposed for upstream `nostr-protocol/nips`
  standardization — the spec states this kind is Buzz-specific by design and
  this node does not evaluate that decision.

**Expected but not independently re-verified at authoring time:** the spec's
claim that, at the time it was written, upstream `nostr-protocol/nips` and
nostrbook.dev had not assigned `30621` (checked at a specific pinned upstream
commit and against a live HTTP registry) was not re-checked by this node —
it is reported here as what the spec itself asserts, not as independently
confirmed present-tense fact about either external registry.
