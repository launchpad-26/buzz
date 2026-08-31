---
id: capabilities-archive-identity-archive
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "`crates/buzz-core/src/kind.rs` defines the five NIP-IA event kinds used by this capability: `KIND_IA_ARCHIVE_REQUEST = 9035`, `KIND_IA_UNARCHIVE_REQUEST = 9036`, `KIND_IA_ARCHIVED = 8002`, `KIND_IA_UNARCHIVED = 8003`, `KIND_IA_ARCHIVED_LIST = 13535`."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:408"
      - "crates/buzz-core/src/kind.rs:410"
      - "crates/buzz-core/src/kind.rs:414"
      - "crates/buzz-core/src/kind.rs:416"
      - "crates/buzz-core/src/kind.rs:418"
  - statement: "`crates/buzz-relay/src/handlers/identity_archive.rs` defines a `ConsentPath` enum with exactly three variants -- `SelfSigned`, `Owner`, `Admin` -- and its `determine_consent_path` function resolves one of them for every archive/unarchive request before `handle_identity_archive_event` persists anything."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/identity_archive.rs"
  - statement: "`crates/buzz-relay/src/handlers/ingest.rs` routes both `KIND_IA_ARCHIVE_REQUEST` and `KIND_IA_UNARCHIVE_REQUEST` to `Scope::UsersWrite`, not an admin-only scope, meaning the relay's coarse ingest gate admits the request from any authenticated user and leaves consent-path authorization entirely to the handler in `identity_archive.rs`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:505"
  - statement: "`migrations/0001_initial_schema.sql` creates `archived_identities` with a composite primary key `(community_id, pubkey)`, a `consent_path` column constrained by `CHECK (consent_path IN ('self', 'owner', 'admin'))`, and `actor`, `reason`, `replaced_by`, `request_event_id`, `archived_at` columns, preceded by the comment \"Conformance: archive cannot hide a key in another community. PK scoped.\" -- so archive state is per-community, not global."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:589"
  - statement: "`crates/buzz-db/src/store/archived_identities.rs`'s module doc states the table \"stores a community-local UI visibility hint for identity pubkeys\" and that \"Archiving is not a ban: it does not affect membership, relay access, or repository permissions\"; its `archive()` function inserts with `ON CONFLICT (community_id, pubkey) DO NOTHING`, so re-archiving an already-archived identity is idempotent and never mutates the existing row's consent path, actor, or reason."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/archived_identities.rs"
  - statement: "`crates/buzz-db/src/store/deletion.rs` lists `\"archived_identities\"` among the tables purged when a community is deleted, and `migrations/0029_community_deletion.sql` calls `attach_community_write_fence('archived_identities')` -- archive state is ordinary per-community tenant data, with no special-cased retention across community deletion."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/deletion.rs:59"
      - "migrations/0029_community_deletion.sql:547"
  - statement: "`desktop/src-tauri/src/commands/identity_archive.rs` exposes Tauri commands `archive_identity`, `unarchive_identity`, `resolve_oa_owner`, and `list_archived_identities`; its doc comments state the desktop \"submit[s] kind:9035 and kind:9036 archive/unarchive requests\" where \"consent path is selected by the relay; we just build the wire form,\" and that `list_archived_identities` reads the relay's `kind:13535` snapshot \"to drive UI flair\" while noting \"the relay performs full authorization.\""
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/identity_archive.rs"
  - statement: "`desktop/src/features/identity-archive/hooks.ts`'s `useIsArchivedPredicate` is documented as \"Self-exempt by construction: the current user is never folded from their own client, even when archived on the relay,\" citing NIP-IA's Self Requests section for the reasoning that folding self would recreate the shadowban the protocol's self-unarchive path exists to prevent; the same file's `useIsIdentityArchived` returns `undefined` while the relay snapshot is loading so callers can defer showing archive-dependent UI rather than flashing a false negative."
    entry_class: FACT
    evidence:
      - "desktop/src/features/identity-archive/hooks.ts"
  - statement: "`desktop/src/features/channels/lib/useClassifiedMembers.ts` uses `useIsArchivedPredicate` to peel archived members out of a channel's member list before splitting the remainder into people and bots, with the inline comment \"Archived wins over bot: a zombie agent should fold into 'Archived', not appear as an active 'Bot'.\""
    entry_class: FACT
    evidence:
      - "desktop/src/features/channels/lib/useClassifiedMembers.ts:52"
  - statement: "`crates/buzz-cli/src/commands/agents.rs` implements `buzz agents archive <target-pubkey>`, `buzz agents unarchive <target-pubkey>`, and `buzz agents archived` (with `dispatch` routing `AgentsCmd::Archive`/`AgentsCmd::Unarchive`/`AgentsCmd::Archived`), each accepting an `--admin` flag parsed by `clap` and asserted by `tests::archive_admin_flag_is_parsed`/`tests::unarchive_admin_flag_is_parsed`; `cmd_archived` fetches and client-side-verifies the relay's `kind:13535` snapshot via `verify_archived_event`, which rejects a wrong kind, a mismatched relay-self author, a missing or duplicated NIP-70 `-` tag, and a failed signature check before returning the archived pubkey list."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/agents.rs:88"
      - "crates/buzz-cli/src/commands/agents.rs:128"
      - "crates/buzz-cli/src/commands/agents.rs:166"
      - "crates/buzz-cli/src/commands/agents.rs:467"
  - statement: "`desktop/tests/e2e/identity-archive.spec.ts` exercises five cases against a mocked bridge -- self-viewer/self-target (Archive visible, no flair), relay-admin viewing another user (Archive visible), verified NIP-OA owner viewing their agent (Archive visible), no-authority viewer (Archive hidden), and an already-archived target (flair visible plus an Unarchive button gated to admin/self) -- and a sibling spec `identity-archive-hide.spec.ts` covers UI-visibility hiding behavior; neither spec drives a live relay round-trip."
    entry_class: FACT
    evidence:
      - "desktop/tests/e2e/identity-archive.spec.ts:46"
      - "desktop/tests/e2e/identity-archive.spec.ts:70"
      - "desktop/tests/e2e/identity-archive.spec.ts:85"
      - "desktop/tests/e2e/identity-archive.spec.ts:99"
      - "desktop/tests/e2e/identity-archive.spec.ts:122"
  - statement: "NIP-IA's own Self Requests section documents self-unarchive as a relay-enforced protocol guarantee -- an archived party retains a path to reverse their own archive as long as they hold the retired key -- which is the source `useIsArchivedPredicate`'s doc comment cites for why self-exemption is mandatory rather than a UI nicety."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-IA.md"
  - statement: "No automated test was found in this session that exercises the full request -> relay-verified consent -> persisted state -> delta -> snapshot pipeline end-to-end against a live, non-mocked relay; the coverage inspected is a Postgres-gated relay-handler test plus the two mocked-bridge Playwright specs above, which is narrower than full pipeline verification."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/identity_archive.rs"
      - "desktop/tests/e2e/identity-archive.spec.ts"
      - "desktop/tests/e2e/identity-archive-hide.spec.ts"
    confidence: 0.6
  - statement: "A sibling, protocol-level concept node for the same subject exists at `launchpad/docs/corpus/layers/identity/identity-archive.md` (`type: layers`, id `layers-identity-identity-archive`), authored for issue #1107 under an open, unmerged pull request, and that node's own front matter names issue #718 (this task) as a distinct, capability-shaped node at a distinct path with a distinct definition of done."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1107 / PR #1812 (layers-identity-identity-archive node, unmerged at the time this node was authored)"
  - statement: "Issue #718's definition of done requires this node to state the capability and primary actors/outcomes, define behavioral rules/constraints/variants, link major flows/interfaces/data/platform implementation, and link verification demonstrating the capability -- distinct from #1107's protocol-definition-shaped DoD for the sibling node above."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#718 definition of done"
---

# Identity archive: capability

Buzz lets a relay retire a stale pubkey — a rotated human key, a departed
contractor's account, or a dormant agent whose owner is still active — from
the surfaces where people look for who's currently around: member lists,
autocomplete, and DM/channel-adder pickers. The retired identity's past
messages keep rendering exactly as before, attributed to the same key; no
event is deleted, and no claim is made about that pubkey on any other relay.
An identity's owner (self), the agent-owner of a dormant agent identity, or a
community admin can request the archive; the archived party always retains a
protocol-guaranteed path to reverse it themselves.

## Primary actors and outcomes

- **A human or agent whose own key is stale** requests their own archive
  (self path) — commonly after rotating to a new key — so their old identity
  stops cluttering member pickers while their history stays intact.
- **An agent's owner** archives a dormant agent identity they own, proving the
  ownership relationship via a NIP-OA attestation, so a "zombie agent" folds
  into an "Archived" bucket instead of appearing as a live bot.
- **A community admin or owner** archives any identity directly, independent
  of self- or owner-consent, typically alongside (not instead of) a separate
  membership-removal decision.
- **Every other member of the community** experiences the outcome passively:
  archived identities disappear from active-member and autocomplete surfaces,
  while any message history involving them is unaffected.

## Behavioral rules, constraints and variants

- **Three consent paths, one relay-side check.** Every archive/unarchive
  request is admitted at the relay's coarse ingest gate under a general
  write scope, then routed to exactly one of `SelfSigned` (actor is the
  target), `Owner` (actor proves NIP-OA ownership of the target, re-checked
  against the target's *live* profile, not just the request's own attached
  credential), or `Admin` (actor holds an admin/owner community role). A
  request that resolves to none of the three is rejected.
- **Idempotent, not cumulative.** Archiving an already-archived identity does
  not overwrite its recorded consent path, actor, or reason — the underlying
  insert is a no-op on conflict. There is one current archive state per
  `(community, pubkey)`, not a history of archive events.
- **Composable with, not a substitute for, membership removal.** An admin may
  archive an identity (hiding it from UI) and separately remove it from
  community membership (denying access) as two independent, independently
  auditable decisions. A pubkey can be archived without being removed,
  removed without being archived, or both.
- **Self-unarchive is a guaranteed escape hatch, not a UI nicety.** An
  archived identity can always self-unarchive while it still holds the key —
  this is what stops the mechanism from being a silent shadowban, and it is
  why client code exempts the current user's own pubkey from being folded by
  the archived-filter predicate even when the relay's snapshot says they are
  archived.
- **Per-community, not global.** Archive state is scoped to `(community_id,
  pubkey)`; it says nothing about the same pubkey on a different relay or
  community, and it is purged like other tenant data when a community is
  deleted.
- **Client-visible state is a signed, verifiable snapshot.** Consumers of the
  archived-identities list — the desktop app and the CLI alike — verify the
  snapshot's kind, its authoring pubkey against the relay's own advertised
  identity, and its signature before trusting it, rather than trusting an
  unauthenticated read.

## Maturity

Shipped. The relay enforces the three consent paths and persists state
(`crates/buzz-relay/src/handlers/identity_archive.rs`,
`crates/buzz-db/src/store/archived_identities.rs`, `archived_identities` table
in `migrations/0001_initial_schema.sql`); the desktop app exposes archive,
unarchive, owner-resolution, and snapshot-read Tauri commands
(`desktop/src-tauri/src/commands/identity_archive.rs`) and consumes them in the
member-classification and profile UI
(`desktop/src/features/identity-archive/hooks.ts`,
`desktop/src/features/channels/lib/useClassifiedMembers.ts`); the CLI exposes
`buzz agents archive`/`unarchive`/`archived`
(`crates/buzz-cli/src/commands/agents.rs`); and mocked-bridge Playwright specs
cover five distinct viewer/target permission combinations
(`desktop/tests/e2e/identity-archive.spec.ts`,
`identity-archive-hide.spec.ts`). No end-to-end test exercising the full
pipeline against a live, non-mocked relay was found in this session — see
*Scope and omissions*.

## Boundary

This node does not describe:
- **The NIP-IA protocol itself as a concept** — its event-kind definitions,
  wire formats, and its distinction from NIP-09 deletion, NIP-51 mute lists,
  NIP-43 membership removal, and NIP-AB device pairing. That is
  `layers-identity-identity-archive` (issue #1107, open PR #1812 at the time
  this node was written — see *Scope and omissions* for why no
  `relationships` edge targets it yet).
- **How the relay, database, and desktop containers are built** — technology
  choices, deployment topology. That is the architecture family's territory
  (`launchpad/docs/corpus/architecture/containers/relay.md`,
  `architecture/containers/desktop.md`, `architecture/containers/postgres.md`),
  none of which are cited here as `relationships` because none of them
  discusses identity archival as their own subject matter.
- **The CLI's or desktop's full command/route surface as an interface
  contract** — this node names the specific commands that expose the
  capability as evidence of its maturity, not as a catalogued interface
  boundary; no `interfaces-events`-typed node for identity archival exists yet
  to `references`.
- **The step-by-step sequence of one archive request landing** (request ->
  consent check -> persist -> delta -> snapshot -> client re-render) as a
  flow. No `type: capabilities`-adjacent flow node for identity archival
  exists yet.
- **How the running relay is operated** (monitoring, incident response) with
  respect to archived-identity state.

## Relationships

Declared: none. Checked before deciding that rather than assuming it — at
the recorded revision, `origin/launchpad`'s corpus tree has no
`capabilities/`, `interfaces-events/`, or identity-archival-specific flow node
for this subject to `references` or sit `part-of`. The one node that already
covers closely related subject matter,
`launchpad/docs/corpus/layers/identity/identity-archive.md`, is not a valid
target: it exists only on an open, unmerged pull request (#1812) at the time
this node was authored, and `AGENTS.md`'s own rule is that a `relationships`
target must resolve against the branch being merged into, never against a
worktree or an unmerged sibling. Once #1812 merges, this node should gain a
`references` edge to `layers-identity-identity-archive` — that is the natural
first edge for this node, deliberately left for a follow-up rather than
declared speculatively now.

## Scope and omissions

**This node covers** the identity-archive capability at the product level:
who can request it and why, the behavioral rules and constraints that govern
every request regardless of implementation detail, its current shipped
maturity with citations to the relay, database, desktop, and CLI code and
tests that realize it, and its boundary against the protocol-concept,
architecture, interface, and flow documents that are each a distinct node.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| NIP-IA as a protocol concept — event kinds, wire formats, distinction from NIP-09/NIP-51/NIP-43/NIP-AB | #1107, `layers/identity/identity-archive.md` (open, unmerged PR #1812 at time of writing) |
| How the relay/database/desktop containers realize this and other capabilities | the `architecture` corpus surface (`architecture/containers/*.md`) |
| The CLI's and desktop's command/route surface as a catalogued interface contract | not yet a filed corpus node for this subject |
| The step-by-step sequence of one archive request through the system | not yet a filed corpus node for this subject |
| Human and agent identity representation more broadly (of which an archivable identity is one state) | #1106/#1103 (`layers/identity/human-identity.md`, `agent-identity.md`), not yet drafted |
| NIP-OA owner-attestation mechanics in full (the cryptographic construction the owner consent path relies on) | not yet a filed corpus node; see `docs/nips/NIP-OA.md` directly |

**Expected but not verified when this node was written:**
- **No end-to-end test exercising the full request-to-snapshot pipeline
  against a live, non-mocked relay was found.** Coverage inspected in this
  session is narrower: relay-handler tests in
  `crates/buzz-relay/src/handlers/identity_archive.rs`, unit tests on the
  `buzz-db` and `buzz-cli` sides, and two Playwright specs that verify
  UI-visible behavior against a mocked Tauri bridge. This is recorded as an
  `INFERENCE` in the evidence ledger, not asserted as a proven absence.
- **This node's `relationships` are declared empty by design, not by
  oversight** — the one closely related node
  (`layers-identity-identity-archive`) is not yet merged and therefore not a
  valid target; see *Relationships* above for the check performed and the
  edge this node should gain once that changes.
