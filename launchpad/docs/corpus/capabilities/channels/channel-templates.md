---
id: capabilities-channels-channel-templates
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Channel templates let a user (via Buzz Desktop) or an agent (via the `buzz` CLI) create a new channel pre-populated with a channel type, visibility, description, canvas content and agent roster from a saved template, instead of specifying each of those individually."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/types.ts:849-863"
      - "crates/buzz-cli/src/lib.rs:589-591"
  - statement: "Buzz Desktop introduced channel templates in PR #538 ('feat(desktop): channel templates -- reusable project settings'), and the `buzz` CLI gained `channels create --template` in PR #1990 ('feat(cli): add channels create --template for desktop channel templates')."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/templates/types.rs"
      - "crates/buzz-cli/src/commands/channel_templates.rs"
      - "commit 1b9f6169e (feat(desktop): channel templates — reusable project settings (#538))"
      - "commit 1a9414618 (feat(cli): add channels create --template for desktop channel templates (#1990))"
  - statement: "A channel template is stored as a record with `id`, `name`, `description`, `channel_type` (defaulting to `stream`), `visibility` (defaulting to `open`), `canvas_template`, an `agents` roster of `personas` and `teams`, an `is_builtin` flag, and `created_at`/`updated_at` timestamps."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/templates/types.rs:3-30"
      - "desktop/src/shared/api/types.ts:849-863"
  - statement: "Templates are persisted desktop-locally as a JSON file at the app's `templates/channel-templates.json` path under its app-data directory, read and written through five Tauri commands (`list_channel_templates`, `create_channel_template`, `update_channel_template`, `delete_channel_template`, `duplicate_channel_template`) -- not as a Nostr event synced through the relay."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/templates/storage.rs:8-20"
      - "desktop/src-tauri/src/commands/channel_templates.rs:46-200"
  - statement: "A built-in template (`is_builtin: true`) can be duplicated but cannot be deleted -- `validate_channel_template_deletion` rejects deletion of a built-in template with the message 'Built-in templates cannot be deleted.'"
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/templates/storage.rs:63-68"
      - "desktop/src-tauri/src/templates/storage.rs:212-219"
  - statement: "No code path that seeds or ships a default built-in template was found: `templates/mod.rs` only re-exports `storage` and `types`, and the only occurrence of a named template like 'Buzz Team' in the repository is inside CLI unit-test fixtures, not production seed data."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/templates/mod.rs"
      - "crates/buzz-cli/src/commands/channel_templates.rs:151-186"
  - statement: "Buzz Desktop manages templates through a dedicated Settings panel ('Channel templates'), reachable via `SettingsPanels.tsx`'s `channel-templates` section and rendered by `ChannelTemplatesSettingsCard`, which supports create, edit, duplicate and delete."
    entry_class: FACT
    evidence:
      - "desktop/src/features/settings/ui/SettingsPanels.tsx:88-187"
      - "desktop/src/features/settings/ui/ChannelTemplatesSettingsCard.tsx:62-135"
  - statement: "On desktop, creating a channel from a template first creates the channel, then best-effort applies the template's canvas content (substituting `{channel.name}` and `{template.name}` placeholders) via `applyCanvas`, then fires-and-forgets `applyAgents` to add the template's persona/team roster as managed agents; a canvas-apply failure does not block navigation to the new channel."
    entry_class: FACT
    evidence:
      - "desktop/src/features/channel-templates/useApplyTemplate.ts:37-55"
      - "desktop/src/app/AppShell.tsx:512-543"
  - statement: "On the CLI, `buzz channels create --template <name>` resolves the named template (case-insensitively) from the desktop's `channel-templates.json`, or from a path given via `--templates-file`; it applies the template's `channel_type`, `visibility` and `description` as defaults that explicit `--type`/`--visibility`/`--description` flags override, and reports a final status of `ok` or `partial` depending on whether every resolved agent could be added as a member."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/channels.rs:645-786"
      - "crates/buzz-cli/src/lib.rs:568-598"
  - statement: "Both the CLI and the desktop Tauri commands validate a template's `channel_type` against exactly `{stream, forum}` and `visibility` against exactly `{open, private}`, rejecting any other value rather than passing it through."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/channels.rs:671-686"
      - "desktop/src-tauri/src/commands/channel_templates.rs:28-44"
  - statement: "The CLI resolves a template's agent roster against live relay state -- team entries are expanded into persona slugs via kind:30176, and live managed-agent instances are scanned via kind:30177 -- then applies a per-persona-slug cardinality rule: zero live instances is skipped, exactly one live instance is added, and more than one live instance for the same persona is a hard error naming the candidate pubkeys rather than an arbitrary pick."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/channels.rs:473-501"
      - "crates/buzz-cli/src/commands/channels.rs:602-643"
  - statement: "Applying a template's canvas is best-effort on both surfaces: the CLI's own comment states its canvas-apply step 'matches desktop's useApplyTemplate.ts behavior' by treating a canvas-submission failure as non-fatal to the surrounding command."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/channels.rs:723-738"
      - "desktop/src/features/channel-templates/useApplyTemplate.ts:50-55"
---

# Channel templates: capability

Channel templates let a user in Buzz Desktop, or an agent through the `buzz`
CLI, create a new channel pre-populated with a saved configuration -- a
channel type, a visibility, a description, canvas starter content, and a
roster of persona/team agents to add as members -- instead of specifying each
of those individually every time a similarly-shaped channel is created.
Buzz Desktop additionally lets a user manage the saved templates themselves
(create, edit, duplicate, delete) from a dedicated Settings panel.

## Maturity

**Shipped.** Buzz Desktop's template management (the `ChannelTemplateRecord`
data model, the five Tauri CRUD commands, the Settings UI, and applying a
template's canvas/agents when creating a channel) shipped in PR #538. The
`buzz` CLI's `channels create --template` -- reading the same desktop-local
template store, resolving its agent roster against live relay state, and
applying its defaults -- shipped later in PR #1990. Both surfaces carry unit
test coverage in their respective crates/modules (for example
`desktop/src-tauri/src/templates/storage.rs`'s serialization and
deletion-guard tests, and `crates/buzz-cli/src/commands/channel_templates.rs`
and `channels.rs`'s template-resolution and cardinality-rule tests).

## Boundary

This node does not describe:
- **How Buzz Desktop or the `buzz` CLI are built.** The container-level
  architecture of those two surfaces is `architecture-containers-desktop`
  and `architecture-containers-cli` (see *Relationships*); this node covers
  only the channel-templates feature within them.
- **The interface contract each surface exposes.** No interface-type corpus
  node exists yet for the desktop Tauri command surface or the `buzz` CLI's
  subcommand surface, so this node cannot reference one. `list_channel_templates`,
  `create_channel_template`, `update_channel_template`, `delete_channel_template`
  and `duplicate_channel_template` (Tauri commands) and `channels create
  --template`/`--templates-file` (CLI flags) are named here as the surface
  this capability exposes, not as a full interface specification.
- **The step-by-step flow of one interaction through it.** No flow-type
  corpus node exists yet for "create a channel from a template" on either
  surface.
- **The event kinds a created channel, its canvas, or its membership are
  built from** (kind:39000-family channel metadata, canvas events, kind:9000
  membership events). Those are the underlying primitives a template's
  effects are expressed through, not something this capability defines.
- **How the running relay or desktop app is operated.** This is a
  user/agent-facing product capability, not an operations concern.

## Relationships

- references: architecture-containers-desktop
- references: architecture-containers-cli

## Scope and omissions

**This node covers** what a channel template is, where it is stored, how it
is applied on Buzz Desktop and through the `buzz` CLI, the validation rules
both surfaces enforce on a template's `channel_type` and `visibility`, the
best-effort semantics of applying a template's canvas, and the CLI's
cardinality rule for resolving a template's agent roster against live relay
state.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How Buzz Desktop and the `buzz` CLI are built | `architecture-containers-desktop`, `architecture-containers-cli` |
| The Tauri command / CLI subcommand surface as a formal interface contract | not yet drafted (no interface-type corpus node exists) |
| The step-by-step flow of creating a channel from a template | not yet drafted (no flow-type corpus node exists) |
| The event kinds behind channel creation, canvas, and membership | not yet drafted |
| How the running system is operated | the `operations` corpus surface |

**Expected but not verified when this node was written:**
- **Whether any built-in template ships by default was not found.** The
  data model supports `is_builtin: true` and the deletion path guards
  against removing one, but no seeding code populates a built-in template on
  first run; the only place a named template like "Buzz Team" appears in
  the repository is CLI unit-test fixtures. This node does not claim any
  built-in template is actually shipped to users today.
- **Cross-device sync of a user's templates was not verified either way.**
  Storage is a JSON file under the desktop app's own app-data directory, per
  installation, which strongly suggests templates do not sync across a
  user's devices, but no explicit sync (or anti-sync) code path was searched
  for beyond the storage module itself.
- **The desktop channel-creation UI's own template-selection flow**
  (`desktop/src/features/sidebar/ui/CreateChannelFormFields.tsx` and
  `useCreateChannelForm.ts`) was located but not read in full; this node's
  claims about desktop application of a template rest on `AppShell.tsx`'s
  `handleCreateChannel` and `useApplyTemplate.ts` rather than the form
  component itself.
