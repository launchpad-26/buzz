---
id: implementation-mobile-feature-map
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "mobile/lib/features/ contains exactly ten feature directories -- activity, channels, forum, home, invites, pairing, profile, pulse, search, settings -- totaling 234 .dart files, with channels (149 files) an order of magnitude larger than every other feature and home (1 file) the smallest."
    entry_class: FACT
    evidence:
      - "find(path='mobile/lib/features/activity', name='*.dart') -> 13 files"
      - "find(path='mobile/lib/features/channels', name='*.dart') -> 149 files"
      - "find(path='mobile/lib/features/forum', name='*.dart') -> 5 files"
      - "find(path='mobile/lib/features/home', name='*.dart') -> 1 files"
      - "find(path='mobile/lib/features/invites', name='*.dart') -> 6 files"
      - "find(path='mobile/lib/features/pairing', name='*.dart') -> 10 files"
      - "find(path='mobile/lib/features/profile', name='*.dart') -> 31 files"
      - "find(path='mobile/lib/features/pulse', name='*.dart') -> 7 files"
      - "find(path='mobile/lib/features/search', name='*.dart') -> 3 files"
      - "find(path='mobile/lib/features/settings', name='*.dart') -> 9 files"
      - "find(path='mobile/lib/features', name='*.dart') -> 234 files total"
  - statement: "This repository's root CLAUDE.md states the feature-isolation contract this node checks against: 'Feature modules must not import from other feature modules -- only from shared/.'"
    entry_class: FACT
    evidence:
      - "CLAUDE.md:599-600"
  - statement: "The corpus already documents this same technology choice at the container level: architecture-containers-mobile's Technology section states feature modules 'import only from shared/, never from each other, keeping the feature boundary enforced by convention rather than by a build-time gate' -- naming explicitly that the rule has no automated enforcement, which this node verifies directly rather than re-asserting."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/mobile.md:129-131"
  - statement: "No lint rule enforces the feature-isolation contract: mobile/analysis_options.yaml enables only package:flutter_lints/flutter.yaml plus the custom_lint plugin, and the only package providing custom_lint rules in mobile/pubspec.yaml is riverpod_lint (Riverpod-specific rules), not an import-boundary or architecture linter."
    entry_class: FACT
    evidence:
      - "mobile/analysis_options.yaml:1-9"
      - "mobile/pubspec.yaml:53-58"
  - statement: "A full scan of every top-level `import` line under mobile/lib/features/**/*.dart, resolving both package:buzz/features/<feature>/... and relative ../<feature>/... forms against each importing file's own feature directory, found 62 import lines that cross a feature boundary, spread across 23 distinct files and 19 distinct (importing-feature, imported-feature) pairs -- the contract in CLAUDE.md:599-600 is violated today, not merely undocumented as unenforced."
    entry_class: FACT
    evidence:
      - "grep_and_resolve(root='mobile/lib/features', line_pattern=\"^import '...'\", resolve='relative and package:buzz/features/ forms against importing file's own feature') -> 62 violating lines, 23 files, 19 feature pairs"
  - statement: "The three heaviest cross-feature import pairs are channels -> profile (10 lines, across 5 files), search -> channels (10 lines, across 2 files) and activity -> channels (9 lines, across 2 files); these three pairs alone account for 29 of the 62 violating lines found."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/channels/channel_detail_page.dart:33-34"
      - "mobile/lib/features/channels/channel_detail_page.dart:75"
      - "mobile/lib/features/channels/channel_management_provider.dart:12"
      - "mobile/lib/features/channels/channels_page.dart:30-32"
      - "mobile/lib/features/channels/members_sheet.dart:12-13"
      - "mobile/lib/features/channels/thread_detail_page.dart:38"
      - "mobile/lib/features/search/search_page.dart:17-23"
      - "mobile/lib/features/search/search_provider.dart:7-9"
      - "mobile/lib/features/activity/activity_page.dart:23-28"
      - "mobile/lib/features/activity/activity_provider.dart:7-9"
  - statement: "home/home_page.dart's three cross-feature imports (activity, channels, search) are the app's tab-shell composing its three top-level tabs, which is a structurally different case from the other 18 pairs found: home/ is the composition root HomePage renders, not a lateral feature reaching into a sibling's internals, even though it still literally violates the 'only from shared/' wording."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/home/home_page.dart:13-15"
  - statement: "Two of the smaller pairs -- settings -> pairing (mobile/lib/features/settings/settings_page.dart importing pairing_provider.dart directly for shared pairing state) and invites -> pairing (invite_join_sheet.dart importing pairing_page.dart directly) -- are genuine lateral feature-to-feature imports, not composition-root wiring; by contrast, SettingsPage's own invite and identity-recovery entry points are injected as WidgetBuilder callbacks from mobile/lib/app.dart rather than imported directly, so that particular potential settings -> invites / settings -> pairing coupling was avoided rather than taken."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/settings/settings_page.dart:17"
      - "mobile/lib/features/invites/invite_join_sheet.dart:8"
      - "mobile/lib/features/settings/settings_page.dart:42-56"
      - "mobile/lib/app.dart:410-416"
  - statement: "Each feature directory has its own entry-point widget: ActivityPage (activity_page.dart:66), ChannelsPage (channels_page.dart:161), ForumPostsView (forum_posts_view.dart:23) and ForumThreadPage (forum_thread_page.dart:25), HomePage (home_page.dart:17), CommunityInvitePage (invite_create_page.dart:26) and InviteJoinSheet (invite_join_sheet.dart:36), PairingPage (pairing_page.dart:28), ProfileEditPage (profile_edit_page.dart:31), PulsePage (pulse_page.dart:20), SearchPage (search_page.dart:100), and SettingsPage (settings_page.dart:37)."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/activity/activity_page.dart:66"
      - "mobile/lib/features/channels/channels_page.dart:161"
      - "mobile/lib/features/forum/forum_posts_view.dart:23"
      - "mobile/lib/features/forum/forum_thread_page.dart:25"
      - "mobile/lib/features/home/home_page.dart:17"
      - "mobile/lib/features/invites/invite_create_page.dart:26"
      - "mobile/lib/features/invites/invite_join_sheet.dart:36"
      - "mobile/lib/features/pairing/pairing_page.dart:28"
      - "mobile/lib/features/profile/profile_edit_page.dart:31"
      - "mobile/lib/features/pulse/pulse_page.dart:20"
      - "mobile/lib/features/search/search_page.dart:100"
      - "mobile/lib/features/settings/settings_page.dart:37"
  - statement: "HomePage composes exactly three tabs -- ActivityPage, ChannelsPage and SearchPage -- via imports at home_page.dart:13-15, and mobile/lib/app.dart's authenticated App state renders HomePage with a settingsPageBuilder and hasUnreadInbox, while its unauthenticated/error state renders PairingPage directly; Forum, Invites, Profile and Pulse have no top-level tab slot and are reached only by navigation from within another feature or from the composition root."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/home/home_page.dart:13-15"
      - "mobile/lib/app.dart:379-394"
  - statement: "ChannelsPage pushes SettingsPage via a settingsPageBuilder WidgetBuilder parameter (_SettingsPageRoute at channels_page.dart:387-397) rather than importing settings_page.dart directly, and that builder is supplied from mobile/lib/app.dart's composition root -- a callback-injection pattern that avoids a channels -> settings import the feature otherwise would have needed for this navigation."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/channels/channels_page.dart:163"
      - "mobile/lib/features/channels/channels_page.dart:169"
      - "mobile/lib/features/channels/channels_page.dart:354-355"
      - "mobile/lib/features/channels/channels_page.dart:387-397"
      - "mobile/lib/app.dart:399-409"
  - statement: "A grep across mobile/lib for `PulsePage(` construction found no call site outside pulse/pulse_page.dart itself -- pulse/ is not composed into HomePage's tabs, mobile/lib/app.dart, or any other navigation surface this scan reached -- but pulse/ still carries its own widget tests (mobile/test/features/pulse/note_card_test.dart, compose_note_page_test.dart), so this is reported as an unresolved observation about reachability, not a confirmed dead-code finding; a grep for one literal construction pattern across two directories does not rule out a route table, deep link, or dynamic dispatch this scan did not check."
    entry_class: INFERENCE
    evidence:
      - "grep(pattern=\"PulsePage(\", scope='mobile/lib and mobile/test') -> only mobile/lib/features/pulse/pulse_page.dart itself"
      - "mobile/test/features/pulse/note_card_test.dart"
      - "mobile/test/features/pulse/compose_note_page_test.dart"
    confidence: 0.55
  - statement: "mobile/test/features/ contains one test subdirectory per lib/features/ feature (activity, channels, forum, home, invites, pairing, profile, pulse, search, settings -- all ten present, no extras), which is the mobile app's existing per-feature test organization; this node's Verification section reports against that structure rather than inventing a new one."
    entry_class: FACT
    evidence:
      - "find(path='mobile/test/features', type='dir') -> activity, channels, forum, home, invites, pairing, profile, pulse, search, settings (10 directories, one per mobile/lib/features/* entry)"
  - statement: "This container's quality gates are `dart format --output=none --set-exit-if-changed .`, `flutter analyze` and `flutter test` (or the `just mobile-fmt` / `just mobile-check` / `just mobile-test` wrappers), none of which check import direction between feature directories -- `flutter analyze` runs the lint rules confirmed in the analysis_options.yaml/pubspec.yaml evidence above, and `flutter test` exercises per-feature behavior, not the module-boundary convention."
    entry_class: FACT
    evidence:
      - "CLAUDE.md:605-609"
---

# Mobile feature map: implementation reference

This node maps `mobile/lib/features/`'s ten feature directories -- what each one is
for, its entry point, and how it is reached from the app's composition root -- against
the feature-isolation contract this repository's `CLAUDE.md` states for the mobile
container: *"Feature modules must not import from other feature modules -- only from
`shared/`."* It is a breadth-first map, not a per-feature deep-dive: internal routing,
provider implementation, and widget-tree detail inside any one feature are out of
scope here and belong to `#950` (Flutter app internals, drafted in parallel in this
same batch). See *Scope and omissions* below for the full boundary.

## Target

The target this node checks the code against is `CLAUDE.md:599-600` (this
repository's root contributor guide, under "Mobile App (Flutter) > Rules"):
*"Feature modules must not import from other feature modules -- only from `shared/`."*
`CLAUDE.md` is not itself a corpus node at this revision, so no `implements` edge is
declared toward it -- per `AGENTS.md`'s rule against declaring an edge to an id that
does not exist, it is named here by path instead.

The same technology choice is already elaborated, at the container level, by
`architecture-containers-mobile` (a merged corpus node), whose own Technology section
states the identical rule and additionally names that it is *"enforced by convention
rather than by a build-time gate."* This node declares `part-of` toward that container
node rather than `implements` toward `CLAUDE.md`, because this document is the
feature-level breakdown that node's own *Scope and omissions* names as future,
separate work ("per-feature detail inside `lib/features/*` ... is a separate task
rather than folded in here").

## Implementation surface

| Feature directory | Realizes | Note |
|---|---|---|
| `activity/` (13 files) | The Activity tab slot named in `architecture-containers-mobile`'s feature list | Cross-channel inbox/activity feed (DMs, mentions, reminders). Entry point `ActivityPage` (`activity_page.dart:66`), one of `HomePage`'s three tabs. Imports `channels/` directly (9 lines, `activity_page.dart:23-28`, `activity_provider.dart:7-9`) to render inbox items that are themselves channel messages -- a boundary violation, not a convention exception. |
| `channels/` (149 files, 11 sub-directories) | The core messaging surface named in `architecture-containers-mobile` | The channel/thread messaging surface itself: channel list, channel detail/thread views, composer, message rendering, reactions, mentions, huddle actions, unread badges, channel management, emoji picker, media viewer. By far the largest feature. Entry points `ChannelsPage` (`channels_page.dart:161`, a `HomePage` tab) and the pushed `ChannelDetailPage`/`ThreadDetailPage`. Imports `profile/` (10 lines across 5 files), `invites/` (2 lines), `pairing/` (2 lines), `activity/` (1 line) and `forum/` (1 line) -- the most heavily cross-importing feature in absolute line count. |
| `forum/` (5 files) | Not named as its own tab in `architecture-containers-mobile`; a nested content surface within Channels | A per-channel "forum" thread view, rendered inside a channel's detail page and reachable from search results. Entry points `ForumPostsView` (`forum_posts_view.dart:23`) and `ForumThreadPage` (`forum_thread_page.dart:25`). Imports `channels/` (6 lines) and `profile/` (2 lines). |
| `home/` (1 file) | The tab-shell composition root | `HomePage` (`home_page.dart:17`) composes `ActivityPage`, `ChannelsPage` and `SearchPage` into a floating tab bar; it is the widget `App` (`mobile/lib/app.dart`) renders once authenticated. Its 3 cross-feature imports (`home_page.dart:13-15`) are composition-root wiring for its own tabs, not lateral feature coupling -- see *Divergences* for why this pair is reported separately from the others. |
| `invites/` (6 files) | Not a named tab; reached via composition-root callback and deep link | Community invite creation and joining. Entry points `CommunityInvitePage` (`invite_create_page.dart:26`, injected into `SettingsPage` as a builder from `app.dart`) and `InviteJoinSheet` (`invite_join_sheet.dart:36`, reached from deep-link dispatch). Imports `pairing/` directly (1 line, `invite_join_sheet.dart:8`) -- a genuine lateral import, not builder-injected. |
| `pairing/` (10 files) | The NIP-AB device-pairing surface named in `architecture-containers-mobile` | QR scan, pairing socket/provider/crypto. Entry point `PairingPage` (`pairing_page.dart:28`), shown pre-auth (`app.dart`'s unauthenticated/error state) and from Settings' identity-recovery flow via a builder callback. `pairing/` has zero outbound cross-feature imports found in this scan -- the only feature of the ten with none. |
| `profile/` (31 files) | Not a named tab; reached from within other features and Settings | User profile viewing/editing: avatar capture/crop/editor (its own 3 sub-directories), presence, status, text editing. Entry point `ProfileEditPage` (`profile_edit_page.dart:31`), reached from Settings and from Channels/Forum member/author surfaces. Imports `channels/` (5 lines across 2 files, `set_status_sheet.dart:17`, `user_profile_sheet.dart:17-20`). |
| `pulse/` (7 files) | A note/timeline feed feature with no confirmed reachability from this app's own navigation | `PulsePage` (`pulse_page.dart:20`), `note_card`, `compose_note_page`, `agent_activity_card`. Imports `channels/` (5 lines) and `profile/` (2 lines). See the INFERENCE evidence entry above and *Scope and omissions*: no call site for `PulsePage(` was found outside its own file in this scan, despite `pulse/` carrying its own widget tests. |
| `search/` (3 files) | The Search tab slot named in `architecture-containers-mobile` | Search across channels, people and messages. Entry point `SearchPage` (`search_page.dart:100`), one of `HomePage`'s three tabs. The single heaviest cross-feature importer by pair count: `channels/` (10 lines across 2 files), plus `forum/` and `profile/` (1 line each). |
| `settings/` (9 files) | Not a named tab; reached via composition-root callback and a pushed route from Channels | App settings, theme/accent pickers. Entry point `SettingsPage` (`settings_page.dart:37`), reached from `ChannelsPage` via a pushed `_SettingsPageRoute` and wired as `app.dart`'s `_buildSettingsPage`. Imports `pairing/` directly (1 line, `settings_page.dart:17`) for shared pairing state, even though its own invite/identity-recovery entry points use builder injection instead -- see *Divergences*. |

## Divergences

The target states an absolute rule ("must not import from other feature modules --
only from `shared/`"), and the code does not hold to it: **62 import lines cross a
feature boundary, across 23 distinct files and 19 distinct feature-pair directions**
(full scan method and count in the evidence ledger above). This is drift, not a
documented exception -- no comment, ADR, or corpus node accepts these imports as
intentional deviations, and `architecture-containers-mobile` itself, which already
describes the rule, does not mention that it is violated.

Two shapes of divergence are worth distinguishing, because they carry different
weight:

- **Composition-root wiring** (`home -> activity`, `home -> channels`, `home ->
  search`, 3 lines): `HomePage` importing its own three tabs is what a tab shell is
  *for*. It still literally violates the "only from `shared/`" wording, but treating it
  identically to the next category would flatten a real distinction the rule's own
  intent (avoid lateral feature coupling) does not seem to be aimed at.
- **Lateral feature coupling** (the remaining 59 lines, 18 pairs): `channels/`
  reaching into `profile/` to render member/author info, `search/` reaching into
  `channels/`, `forum/` and `profile/` to render result rows, `activity/` reaching
  into `channels/` to render inbox items that are channel messages, `pulse/` reaching
  into `channels/` and `profile/`, and smaller one-off pairs (`settings -> pairing`,
  `invites -> pairing`, `channels -> invites`/`pairing`/`activity`/`forum`, `forum ->
  profile`). These are the cases the stated rule appears to exist to prevent, and they
  are not composition-root wiring by any reading -- `channel_detail_page.dart`
  importing `user_profile_sheet.dart` from `profile/` is one feature's UI reaching
  directly into another's, not two apps meeting at a shared conductor.

One place where the *opposite* happened -- a potential lateral import was avoided --
is documented for balance: `SettingsPage`'s invite-creation and identity-recovery
entry points are injected as `WidgetBuilder` callbacks from `mobile/lib/app.dart`
rather than imported directly from `invites/` or `pairing/`, even though
`SettingsPage` *does* import `pairing/` directly for a different purpose
(`pairing_provider.dart`, shared state rather than a page). The pattern that would
keep the rule intact already exists in this codebase; it is simply not applied
consistently.

## Verification

**None automated.** Confirmed directly, not merely asserted: `mobile/analysis_options.yaml`
enables only `flutter_lints` plus the `custom_lint` plugin, and the only rule package
wired to `custom_lint` in `mobile/pubspec.yaml` is `riverpod_lint` -- a Riverpod-specific
linter, not an import-boundary or layered-architecture linter. `flutter analyze` and
`dart format --output=none --set-exit-if-changed .` do not check import direction.
`flutter test` exercises per-feature behavior (`mobile/test/features/<feature>/`, one
directory per `lib/features/` entry, confirmed 1:1) but nothing in that suite asserts
which directories a feature may import from. The only check that currently exists for
this contract is the manual, full-repository scan this node's own evidence ledger
records -- which is exactly the gap `architecture-containers-mobile`'s "enforced by
convention rather than by a build-time gate" already named, now with a measured count
behind it.

## Relationships

- part-of: architecture-containers-mobile

No `implements` edge: `CLAUDE.md`, the target this node checks against, is not itself
a corpus node at this revision (see *Target* above). No `references` edge: no
verification/test-strategy corpus node exists yet for the mobile container to point
at as the source backing this node's *Verification* section.

## Scope and omissions

**This node covers** a feature-to-directory index of `mobile/lib/features/`'s ten
feature directories -- what each is for, its file count, its entry point, how it is
reached from the app's composition root, and whether the codebase's actual imports
honor the feature-isolation contract `CLAUDE.md` states for this container. It exists
at map/breadth grain, not deep-dive grain.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Per-feature internals -- routing/navigation logic beyond entry points, provider implementation detail, widget-tree structure, state management patterns inside any one feature | `#950` (Flutter app internals, this same batch) |
| `mobile/lib/shared/`'s own structure and the relay/crypto/community subsystems it holds | `architecture-containers-mobile` (already covers this at container grain) |
| Fixing the 62 cross-feature import lines this node reports, or updating `CLAUDE.md`/`architecture-containers-mobile` to describe the rule as convention-only-and-currently-violated rather than simply convention-only | out of scope for a documentation task; a follow-up implementation or documentation issue, not filed by this node |
| Whether `pulse/`'s apparent lack of a call site is dead code, a route this scan did not reach, or work in progress | unresolved; reported as an INFERENCE with confidence 0.55 in the evidence ledger, not settled here |
| Desktop's or the CLI's equivalent feature/module organization | not this container's subject |

**Expected but not verified when this node was written:**

- Whether any of the 62 cross-feature import lines are recent regressions versus
  long-standing structure was not checked -- this node reports the current-state count
  from `git blame`-free evidence, not a trend.
- Whether a route table, deep link, or dynamic widget-builder dispatch this scan did
  not reach makes `pulse/` reachable after all was not ruled out; see the INFERENCE
  entry above.
- Whether any of the 19 feature-pair imports found are already tracked by an existing
  GitHub issue was not checked against the issue tracker.
