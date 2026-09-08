---
id: capabilities-archive-export
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "The desktop app registers four Tauri commands for exporting managed-agent state to a portable file: `export_agent_snapshot`, `encode_agent_snapshot_for_send`, `export_team_snapshot`, and `encode_team_snapshot_for_send`, all listed in the app's `generate_handler!` invocation."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/lib.rs:750-761"
      - "desktop/src-tauri/src/commands/personas/snapshot.rs"
      - "desktop/src-tauri/src/commands/team_snapshot.rs"
  - statement: "`export_agent_snapshot` produces a `buzz-agent-snapshot v1` file in one of two formats -- `.agent.json` (canonical manifest) or `.agent.png` (the same manifest embedded in a `buzz_agent_snapshot` tEXt chunk of an avatar image) -- and the user picks the save destination through an OS save-file dialog; the command returns `false` without writing anything if that dialog is cancelled."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/personas/snapshot.rs"
      - "desktop/src-tauri/src/managed_agents/agent_snapshot.rs:1-17"
  - statement: "A snapshot export includes zero, one, or three levels of agent memory -- `none` (definition + profile only, the default), `core` (adds the core memory entry), or `everything` (adds every `mem/*` entry) -- selected by the caller via a `memory_level` parameter, and memory is fetched and included only when a `memory_source_pubkey` naming a linked keyed agent instance is supplied and server-side validated against the exported definition."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/agent_snapshot.rs:78-88"
      - "desktop/src-tauri/src/commands/personas/snapshot.rs:67-105"
      - "desktop/src-tauri/src/commands/personas/snapshot.rs:144-154"
  - statement: "The export path never serializes secret or machine-local fields into the snapshot: private key material, the NIP-OA `auth_tag`, `env_vars`, `relay_url`, local harness command paths, runtime process state, and internal lineage/bookkeeping ids are all excluded by construction (only explicit fields are placed into the manifest type), not by a post-hoc redaction step."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/managed_agents/agent_snapshot.rs:19-41"
  - statement: "The desktop UI's export dialog lets the user choose the memory level (\"Agent only\" / \"Agent + core memory\" / \"Agent + all memories\") and the file format (JSON or PNG) before exporting, and shows a plaintext-memory warning banner whenever a non-`none` memory level is selected."
    entry_class: FACT
    evidence:
      - "desktop/src/features/agents/ui/AgentSnapshotExportDialog.tsx"
  - statement: "`export_team_snapshot` produces a `buzz-team-snapshot v1` file (`.team.json` or `.team.png`) bundling every team member's definition, profile, and optional memory into one file, with a combined size ceiling of 25 MiB for JSON and 50 MiB for PNG; re-importing it mints a fresh keypair and `ManagedAgentRecord` per member plus one `TeamRecord`, rather than reusing the exporter's identities."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/team_snapshot.rs:1-30"
  - statement: "The agent-snapshot-export feature (definition/profile/memory manifest, `.agent.json`/`.agent.png` codec, export/import Tauri commands, sender-native send, and recipient card/import) shipped in PR #1753 (`1580046b3 feat(desktop): add buzz-agent-snapshot v1 export, import, sender-native send, and recipient card/import (#1753)`); team-level snapshot export shipped afterward in PR #1784 (`aceb5e045 feat(managed_agents): add buzz-team-snapshot v1 codec (#1784)`) and was extended for PNG memory parity in PR #1846 (`448baeef7 feat(teams): unify team model, snapshot sharing, and PNG memory parity (#1846)`)."
    entry_class: FACT
    evidence:
      - "commit 1580046b3"
      - "commit aceb5e045"
      - "commit 448baeef7"
  - statement: "No `buzz-cli` subcommand exposes agent- or team-snapshot export: every occurrence of the string `snapshot` across `crates/buzz-cli/src` names an unrelated concept -- the NIP-IA archived-identities snapshot (`kind:13535`), a NIP-40902 presence snapshot, or a `kind:30023` note snapshot -- none of them a portable agent/team file export."
    entry_class: FACT
    evidence:
      - "grep_recursive('snapshot', path='crates/buzz-cli/src') -> hits only in agents.rs (NIP-IA archived-identities snapshot), channels.rs (NIP-IA + presence snapshot), users.rs (presence snapshot), messages.rs (membership snapshot), notes.rs (kind:30023 note snapshot); zero hits naming agent- or team-snapshot export, run at commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "NIP-IA (Identity Archival), the protocol governing relay-scoped hiding of retired pubkeys via `kind:9035`/`9036`/`8002`/`8003`/`13535` events, defines no export or file-download concept anywhere in its text; it is a distinct capability from agent/team snapshot export despite both using the word \"archive\"/\"archival\"."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-IA.md"
  - statement: "The import/restore counterpart of this capability -- `preview_agent_snapshot_import` and `confirm_agent_snapshot_import` (agent-level) and their team-level equivalents -- is implemented in a sibling module explicitly split out to keep the export module under the repository's file-size gate, and is registered through the same `personas::`/`team_snapshot::` command paths as the export commands documented here."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/personas/snapshot/import.rs:1-7"
      - "desktop/src-tauri/src/commands/personas/snapshot.rs:25-28"
  - statement: "Desktop Playwright E2E specs exist that exercise the agent- and team-snapshot recipient/import UI against the exported file formats this node documents: `desktop/tests/e2e/agent-snapshot-recipient.spec.ts` (its header states it exercises the `AgentSnapshotCard` rendered from an `.agent.json`/`.agent.png` attachment and the add-agent preview/confirm flow) and `desktop/tests/e2e/team-snapshot.spec.ts`. Only their header/purpose comments were read for this node, not their full bodies, so the extent to which they exercise the export side specifically (versus only the import side their names emphasize) was not confirmed."
    entry_class: FACT
    evidence:
      - "desktop/tests/e2e/agent-snapshot-recipient.spec.ts:1-6"
      - "desktop/tests/e2e/team-snapshot.spec.ts"
---

# Agent and team snapshot export: capability

Buzz lets a user take a managed agent's (or an entire team's) definition,
profile, and optionally its memory, and export it as a single portable file --
`.agent.json`/`.agent.png` for one agent, `.team.json`/`.team.png` for a whole
team -- that can be saved to disk or sent natively as a channel/DM attachment.
The exported file is import-compatible: a recipient (or the same user, later)
can bring the agent or team back into their own Buzz instance from that one
file, with a fresh keypair minted on import rather than the original identity
being transplanted.

## Maturity

**Shipped.** Agent-level snapshot export (definition + profile + optional
memory, `.agent.json`/`.agent.png` codec, the export/import Tauri commands, and
sender-native send plus recipient card/import) landed in PR #1753. Team-level
snapshot export (`.team.json`/`.team.png`, bundling every member plus one
`TeamRecord`) landed afterward in PR #1784 and was extended for PNG memory
parity in PR #1846. Both command sets are registered in the running app's
`generate_handler!` list today, not merely present as unused code. Desktop E2E
specs exercising the recipient/import side of both file formats exist
(`agent-snapshot-recipient.spec.ts`, `team-snapshot.spec.ts`); see *Scope and
omissions* for what was and was not confirmed about their coverage of export
specifically.

## Boundary

This node does not describe:
- **How the feature is built** -- the manifest type, PNG tEXt-chunk codec, and
  envelope/encryption helpers live in `desktop/src-tauri/src/managed_agents/
  agent_snapshot.rs`, `team_snapshot.rs`, and `agent_snapshot_envelope.rs`. No
  architecture-family corpus node for this container's internals exists yet to
  `references`.
- **The interface contract itself** -- the exact Tauri command signatures,
  parameter shapes, and error cases for `export_agent_snapshot` /
  `encode_agent_snapshot_for_send` / `export_team_snapshot` /
  `encode_team_snapshot_for_send`. No interface-type corpus node exists yet to
  `references`.
- **The step-by-step flow** a user or agent takes through export -- opening the
  dialog, choosing memory level and format, confirming, and what happens next
  on the send-vs-save-to-disk branches. No flow-type corpus node exists yet.
- **Import/restore.** Bringing an exported file back into a Buzz instance --
  `preview_agent_snapshot_import`, `confirm_agent_snapshot_import`, and the
  team-level equivalents -- is the counterpart capability, implemented in a
  sibling module split out specifically to keep this one under the file-size
  gate. It is a distinct capability from export, not a variant of it: importing
  mints a fresh identity rather than reusing the exporter's, and has its own
  validation, size ceilings, and preview/confirm two-step flow.
- **NIP-IA identity archival.** `docs/nips/NIP-IA.md` defines a same-named-in-
  spirit but functionally unrelated capability: hiding a retired pubkey from a
  relay's active-member surfaces. It has no export or file concept at all and
  shares no code path with the snapshot-export feature this node documents.
- **Local message/event archiving to a local database** (the desktop
  "local archive" subscription feature that saves relay events to a local
  SQLite store) -- a different capability under the same `archive/` grouping,
  with no shared implementation.

## Relationships

None declared. The corpus tree merged to `origin/launchpad` at the recorded
revision contains no `capabilities/` subtree and no sibling node this capability
would `references`, `part-of`, or `implements` against -- only the `AGENTS.md`/
`README.md`/`templates/**`/`standards/**`/`architecture/**` nodes are merged.
The architecture, interface, flow, and restore/import nodes named in *Boundary*
above do not yet exist as corpus nodes; when any of them merge, this node's
`relationships` is where a `references` edge to them belongs.

## Scope and omissions

**This node covers** what the agent/team snapshot export capability lets a
user do, the file formats and memory-level choices it exposes, what is
deliberately excluded from an exported file (secrets, machine-local paths,
runtime state), that it is desktop-only with no CLI equivalent, its shipped
maturity and the PRs that shipped it, and its boundary against the visually
similar NIP-IA identity-archival capability and against its own import/restore
counterpart.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How the feature is built (manifest types, PNG codec, envelope/encryption) | a future architecture-family corpus node (none merged yet) |
| The Tauri command interface contract in full | a future interface-type corpus node (none merged yet) |
| The step-by-step export flow | a future flow-type corpus node (none merged yet) |
| Import/restore of an exported snapshot | the sibling "restore" capability node (task #720, not opened while drafting this node) |
| The desktop "local archive" (local SQLite event archiving) capability | the sibling "local-archive" capability node (task #719, not opened while drafting this node) |
| NIP-IA identity archival | the sibling "identity-archive" capability node (task #718, not opened while drafting this node) |

**Expected but not verified when this node was written:**
- **The full bodies of `agent-snapshot-recipient.spec.ts` and
  `team-snapshot.spec.ts`** (desktop E2E specs) were not read in full -- only
  their header comments, which describe recipient-native card rendering and
  the add-agent preview/confirm flow. Whether they exercise the *export* side
  (as opposed to only the import side they are named for) was not confirmed
  beyond the header comment's framing.
- **Unit test coverage for the secret-exclusion claim** (`agent_snapshot.rs`'s
  own doc comment states exclusions are "asserted by unit tests") was not
  independently opened; the exclusion claim above rests on the module's
  by-construction manifest-type shape, not on running or reading those tests.
- **Sibling issues #718, #719, #720** (identity-archive, local-archive, restore)
  were not opened while drafting this node; their scope above is inferred only
  from their issue titles in the parent Feature #613's child-issue list.
