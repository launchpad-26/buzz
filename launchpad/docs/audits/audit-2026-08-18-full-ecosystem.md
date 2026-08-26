# Buzz (launchpad-26 fork) — Full Ecosystem Audit

**Date:** 2026-08-18 · **Auditor:** Claude (7 parallel shard agents + synthesis) · **Repo:** `launchpad-26/buzz` @ `task/209-project-memory` (commit `81810ab6`) · **Scope:** whole ecosystem — all 29 Rust workspace crates, desktop (Tauri+React), mobile (Flutter), web/, migrations/, CI/CD, and documentation. **Report-only — nothing in the repository was modified.**

**Severity counts (after cross-shard dedup): 6 Blocker · 19 High · 23 Medium · ~17 Low**

This audit was run as 7 parallel agent shards (core relay/data, agent-AI surface, CLI/SDK/interop, desktop, mobile, migrations/CI/infra/web, docs-vs-reality/live-state), each following an evidence-first methodology (adversarial invariant construction, no absence claims without a pasted search, full enumeration instead of spot-checks). This document merges their findings, removes duplicates found independently by more than one shard (noted inline), and cross-references contradictions between shards.

---

## Preflight (whole-repo, done before sharding)

- `just check` (fmt + clippy workspace + Tauri + desktop/web Biome + file-size/px-text/pubkey guards + mobile format/analyze) — **passed clean**, exit 0. Two trivial Biome nits (unsafe-fixable string-concat, one `!important`), 71 outdated Flutter packages (staleness only).
- Docker/Postgres/Redis were live and healthy throughout (`buzz-postgres`, `buzz-redis`), so shards could run real `cargo test`/migration verification against live infra, not just static reading.
- `gh` authenticated as `serina-mcfall`, live GitHub queries reachable throughout.

---

## Findings — Blocker

### BL1 — `buzz-admin reconcile-channels --relay-key` puts the relay's real signing key in argv
**Location:** `crates/buzz-admin/src/main.rs:89-95,461-483`
**Evidence:** The flag is documented as the primary "production use" path (ahead of the `BUZZ_RELAY_PRIVATE_KEY` env-var fallback at the same call site).
**Consequence:** The relay's stable NIP-29-signing identity gets written into `argv`, visible via `ps aux`, `/proc/<pid>/cmdline`, shell history, and any log aggregator/CI runner that captures command lines.
**Change:** (a) Stop accepting the key as a CLI arg; env-var only. (b) `{file: crates/buzz-admin/src/main.rs, location: lines 89-95 (flag) + 461,468 (fallback chain), change: "delete relay_key: Option<String> and its parameter, leaving only std::env::var(\"BUZZ_RELAY_PRIVATE_KEY\") (mirrors connect_member_services at line 393)", verify: "cargo build -p buzz-admin && ./target/debug/buzz-admin reconcile-channels --help shows no --relay-key", depends_on: none}`

### BL2 — `buzz-pairing-cli source --nsec` puts a Nostr private key in argv
**Location:** `crates/buzz-pairing-cli/src/main.rs:53-56`; `crates/buzz-pairing-cli/README.md:27,31`
**Evidence:** Same argv-leak pattern as BL1. The crate's own `Cargo.toml` already enables clap's `env` feature but it isn't wired to this flag.
**Change:** (a) Accept the key via env var instead. (b) `{file: crates/buzz-pairing-cli/src/main.rs, location: line 54, change: "#[arg(long)]" -> "#[arg(long, env = \"BUZZ_PAIR_SOURCE_NSEC\", hide_env_values = true)]"; update README.md:27,31, verify: "./target/debug/buzz-pair source --help shows the env var and hide_env_values masking", depends_on: none}`

### BL3 — `CommunityChangeOverlay` claims a modal dialog (`aria-modal="true"`, `role="dialog"`) with no real focus trap or focus restore
**Location:** `desktop/src/features/communities/ui/CommunityChangeOverlay.tsx:20-22,67-73`; caller `desktop/src/app/App.tsx:534-538`
**Evidence:** Only a one-time `.focus()` on mount; no Tab-cycling handler anywhere in the file; no focus-restore on close (`onClose` captures no ref).
**Consequence:** A keyboard/screen-reader user can Tab out of this "modal" into the background app while `aria-modal="true"` falsely claims the rest of the page is inert.
**Change:** (a) Add a real focus trap and restore, reusing the pattern that already works elsewhere in this codebase. (b) `{file: desktop/src/features/communities/ui/CommunityChangeOverlay.tsx, location: lines 17-33 and 66-99, change: "capture document.activeElement before open, add a Tab keydown handler cycling focus between first/last focusable descendants (mirror desktop/src/shared/ui/markdown.tsx:461-477,490-529, which already implements this for the image lightbox), restore captured focus on cleanup", verify: "Playwright/RTL test: Tab past the last focusable control and assert focus stays inside; assert focus returns to the trigger on close", depends_on: none}`

### BL4 — `VideoPlayer`'s video-review dialog has the identical fake-modal defect
**Location:** `desktop/src/shared/ui/VideoPlayer.tsx:1643-1650,1607-1627`
**Evidence:** Same shape as BL3 — only Escape is handled, no Tab trap, no focus restore on close.
**Change:** (a) Same fix pattern as BL3. (b) `{file: desktop/src/shared/ui/VideoPlayer.tsx, location: dialog div 1643-1650, handlers ~1607-1627, change: "add tabIndex={-1}+ref, Tab-cycling handler, initial focus on open, restore pre-open activeElement on close — reuse markdown.tsx's helper rather than a third copy", verify: "same Playwright pattern as BL3", depends_on: none}`

> **Pattern note:** BL3/BL4 (desktop) and finding H15 below (web/`InvitePage`, rated High rather than Blocker by its shard) are the *same* defect recurring in three places across two different frontends. Fixing the pattern once (a shared focus-trap hook/component) and auditing every `role="dialog"` site against it would resolve all three at once — see Recommended Additions.

### BL5 — `cardMintStore` (agent card-mint jobs) is a community-scoped singleton whose reset function is defined but never called
**Location:** `desktop/src/features/agents/cardMintStore.ts:61-66,190-195`; not referenced in `desktop/src/features/communities/useCommunityInit.ts:50-76`
**Evidence:** `resetCardMintStore()` exists and is called only from its own test file's `beforeEach` — zero production call sites. Full diff of all module-level singletons in `desktop/src` against the 17 calls actually wired into `resetCommunityState()` confirms this one is the omission.
**Consequence:** A card-mint job or open card viewer started in community A survives a switch to community B, showing another community's agent name/card state in the new community's UI.
**Change:** (a) Wire the existing reset function in. (b) `{file: desktop/src/features/communities/useCommunityInit.ts, location: import block + resetCommunityState body (lines 50-76), change: "import resetCardMintStore from '@/features/agents/cardMintStore' and call it inside resetCommunityState()", verify: "extend cardMintStore.test.mjs or add an integration test asserting resetCommunityState() clears jobs/viewer/galleryOpen", depends_on: none}`

### BL6 — Moderation timeout state (`timeoutStore.ts`) is never cleared on community switch
**Location:** `desktop/src/features/moderation/lib/timeoutStore.ts:20-29,64-71`; only call site `desktop/src/features/messages/hooks.ts:620`
**Evidence:** `clearTimeoutState()` is only invoked from the message-send success path, never from `resetCommunityState()`. The module's own doc comment assumes "one community per relay connection," which switching invalidates.
**Consequence:** A member timed out in community A keeps showing as write-blocked after switching to community B, where they aren't timed out, until their next send attempt in B.
**Change:** (a) Wire the existing clear function in. (b) `{file: desktop/src/features/communities/useCommunityInit.ts, location: import block + resetCommunityState body, change: "import clearTimeoutState from '@/features/moderation/lib/timeoutStore' and call it inside resetCommunityState()", verify: "test asserting useTimeoutState() reports inactive immediately after a switch even if active pre-switch", depends_on: "same test scaffold gap as BL5/Medium finding M-D1 below"}`

---

## Findings — High

### H1 — [Systemic, cross-shard] ~14 crates' real, passing test suites never execute in CI or the pre-push hook
**Found independently by 3 shards** (core relay/data, agent-AI surface, CLI/SDK/interop) — the single broadest finding in this audit.
**Location:** `Justfile:294-324` (`test-unit`), `.github/workflows/ci.yml:112-132,354-361`, `lefthook.yml:58-60`, `scripts/run-tests.sh:70-135`
**Evidence:** `test-unit`'s own comment admits the design: *"nothing in CI runs `cargo test --workspace` — workspace membership alone buys clippy/check, not a single executed test"* — so every crate must be individually enumerated, and these are not:
| Crate | Tests confirmed passing (ran directly) |
|---|---|
| `buzz-pubsub` | 42 |
| `buzz-search` | 6 |
| `buzz-audit` | 26 |
| `buzz-media` | 206 |
| `buzz-relay` (`--lib`) | 899 archived-but-never-executed (2 selectors run, rest don't) |
| `buzz-acp` | 686 |
| `buzz-agent` | 430 |
| `buzz-persona` | 127 |
| `buzz-workflow` | 154 (2 ignored, need Postgres) |
| `buzz-dev-mcp` (non-Windows) | 96 — its `#[cfg(unix)]` code, incl. process-group kill path, never runs on *any* platform in CI (only run inside the `windows-rust` job) |
| `buzz-relay-mesh` | 32 |
| `buzz-sdk` | 257 |
| `buzz-ws-client` | 3 |
| `buzz-pair-relay` | 51 |

That's **3,000+ test functions with zero CI execution path**, across roughly half the Rust workspace. `buzz-admin` and `buzz-pairing-cli` (the two crates holding BL1/BL2) have **zero tests at all**.
**Consequence:** Concrete proof this already bites: H2 and H3 below are both currently-failing tests in exactly this blind spot, invisible to every gate.
**Change:** (a) Add the missing crates to the enumerated test recipe. (b) `{file: Justfile, location: test-unit recipe (294-324), change: "add cargo nextest run invocations for buzz-pubsub, buzz-search, buzz-audit, buzz-media, buzz-relay --lib, buzz-acp, buzz-agent, buzz-persona, buzz-workflow, buzz-dev-mcp --lib, buzz-relay-mesh, buzz-sdk --lib, buzz-ws-client --lib, buzz-pair-relay, following the existing enumerated pattern", verify: "just test-unit reports nonzero pass counts for each newly added crate", depends_on: "H2/H3 will turn this gate red immediately upon adding buzz-relay/git-sign-nostr — expected and desired, not a blocker to merging the Justfile change itself"}`

### H2 — A `buzz-relay` test is red right now, invisible to CI (direct proof of H1)
**Location:** `crates/buzz-relay/src/api/mesh_demo.rs:339` (`demo_join_forwarded_arm_round_trips_echo`)
**Evidence:** Reproduced deterministically against live Postgres/Redis: `assertion left==right failed: left: 504, right: 200`. A second consecutive run hangs past 2 minutes (suspected leaked Redis lease from the first run's teardown — itself a test-isolation gap).
**Change:** (a) Needs diagnosis by someone with mesh/QUIC context — real regression vs. environment timing is not yet determined. (b) `{file: crates/buzz-relay/src/api/mesh_demo.rs, location: line 339 + call chain, change: "trace why the forwarded-arm request returns 504, and separately why a second run hangs", verify: "cargo test -p buzz-relay --lib api::mesh_demo::tests::demo_join_forwarded_arm_round_trips_echo -- --test-threads=1, twice in a row without restarting Redis", depends_on: none}`

### H3 — `git-sign-nostr`'s NIP-OA owner-pubkey rejection test is red right now, invisible to CI (direct proof of H1)
**Location:** `crates/git-sign-nostr/src/lib.rs:1422-1424` (validation), `:2117-2138` (test)
**Evidence:** `cargo test -p git-sign-nostr --lib` → 55 passed, 1 failed. An all-zero BIP-340 x-only pubkey is supposed to be rejected as invalid but the underlying `nostr` crate's `PublicKey::from_hex` accepts it (confirmed against a standalone scratch harness — x=0 genuinely has a curve solution). Test and code landed in the same commit (`70a691517b`, 2026-05-11) — broken since day one, silent for ~3 months purely because of H1.
**Change:** (a) Needs a maintainer decision on the intended invariant. (b) `{file: crates/git-sign-nostr/src/lib.rs, location: line 1423 area, change: "either add an explicit reject for the all-zero/degenerate key, or rewrite the test's premise if curve-membership rejection was never achievable for this input", verify: "cargo test -p git-sign-nostr --lib passes 56/56", depends_on: "maintainer decision on intended invariant"}`

### H4 — `flutter test` currently fails: 4 accessibility-related large-text-size tests broken
**Location:** `mobile/test/features/forum/forum_widgets_test.dart:236,630`; `mobile/test/features/pulse/compose_note_page_test.dart:86`; `mobile/test/features/pulse/note_card_test.dart:75`
**Evidence:** `flutter test` → `+1253 -4`, exit 1. Each is a `StateError: No element` when locating a timestamp `Text` widget under `TextScaler.linear(2)`. Root cause not fully isolated (not a stale-clock artifact — checked; not an overflow exception — checked).
**Consequence:** These are exactly the large-text-size regression tests the project's non-negotiable accessibility mandate exists to protect, and the suite meant to catch large-text breakage in Forum/Pulse is itself currently broken.
**Change:** (a) Needs a debugging pass. (b) `{file: mobile/test/features/forum/forum_widgets_test.dart, location: lines 236, 630 (+ the two Pulse files), change: "not diagnosable further without executing test-debug code, which a report-only audit must not do — needs tester.allWidgets/debugDumpApp() inspection", verify: "flutter test --plain-name 'large text sizes'", depends_on: none}`

### H5 — [Merged, found by 2 shards] `cargo deny check` is currently failing for two independent, untriaged reasons
**Location:** workspace-wide `deny.toml`; `.github/workflows/ci.yml:889-901` (`security` job)
**Evidence:**
1. `RUSTSEC-2026-0257` (webbrowser 1.2.1 argument-injection) via `buzz-agent → sprig → webbrowser` — not in `deny.toml`'s triaged ignore list.
2. Two yanked `spin` versions via `buzz-relay-mesh → iroh` and via a `mesh-llm-host-runtime` dev-dependency — also untriaged.
Both reproduced with `cargo deny check` run directly; a CI run on the identical `Cargo.lock` a few hours earlier showed `Security: success` — meaning the failure comes from live RustSec/crates.io state, not a lockfile change, making this a ticking time bomb for the next Rust-touching PR.
**Change:** (a) Triage both — either bump/patch the transitive deps or add dated `deny.toml` exemptions matching the existing documented-exemption style. (b) `{file: deny.toml, location: [advisories] section, change: "add ignore entries for RUSTSEC-2026-0257 and the two yanked spin versions, each with an owner-supplied dated reason, or resolve via dependency updates", verify: "cargo deny check exits 0", depends_on: "owner confirmation of exact cargo-deny 0.19.0 config syntax for yanked-crate overrides — not verified in this audit"}`

### H6 — This fork has zero branch protection or ruleset — every "required" gate is currently advisory-only
**Location:** GitHub repo settings, `launchpad-26/buzz`, branch `launchpad` (this fork's actual default branch)
**Evidence:** `gh api repos/launchpad-26/buzz/branches/launchpad/protection` → 404; `.../rulesets` → `[]`; `.../rules/branches/launchpad` → `[]`. Live proof: PR #194 merged with its own PR-body-check job **failing** and **zero recorded reviews**.
**Consequence:** Every gate described in the docs (DCO, PR-body check, "two approving reviews," CI itself) currently rests entirely on human discipline — nothing in the GitHub merge button is actually blocked by anything.
**Change:** (a) Configure a ruleset requiring the key CI jobs + reviews. (b) Not a file edit — a GitHub repo-settings change requiring admin access this fork's `gh` token doesn't have (`permissions.admin: false`), so flagged for a human with the right access. `{depends_on: "admin:org or repo-admin access"}`

### H7 — The documented "required DCO Check" does not exist as any GitHub check anywhere on this fork
**Found independently by 2 shards.**
**Location:** `AGENTS.md:112`, `CONTRIBUTING.md:52`, `launchpad/AGENTS.md:236,241`
**Evidence:** `grep -rniI "dco" .github/workflows/` → nothing. All 10 open PRs' `statusCheckRollup` checked — no check named/matching DCO on any of them. The only DCO-related artifact is a **local, opt-in, trivially-bypassable** `lefthook.yml` commit-msg hook that auto-appends `Signed-off-by` (this part works correctly — the gap is enforcement, not the hook mechanism).
**Change:** (a) Needs a decision: install a DCO GitHub App, or add a CI job checking every commit for the trailer and mark it required (depends on H6 being resolved first to actually block anything). Not precise enough for a blind mechanical edit.

### H8 — Genuine upstream Buzz product bugs are being filed in the fork's own tracker instead of `block/buzz`
**Location:** `launchpad-26/buzz` issues **#220**, **#204** (Windows-clippy failures in `desktop/src-tauri` and `buzz-terminal`)
**Evidence:** Both crates are confirmed upstream product code (`buzz-terminal`'s first commit predates the fork's existence by months), squarely in-scope for `block/buzz` per this repo's own ecosystem table — yet both bug reports sit in the cohort's tracker, which `block/buzz` maintainers never see.
**Change:** (a) Refile at `block/buzz/issues` with cross-references in both directions. Process action, not a code change; needs a human decision on whether to close the fork copies or keep them as pointers.

### H9 — `git-credential-nostr`'s keyfile loading lacks the TOCTOU/symlink/ownership protections its sibling `git-sign-nostr` already implements for the identical task
**Location:** `crates/git-credential-nostr/src/lib.rs:28-72` vs. `crates/git-sign-nostr/src/lib.rs:769-839`
**Evidence:** `git-credential-nostr` makes 3 separate path-based fs calls (symlink-followable, no ownership check); `git-sign-nostr` does the equivalent job via one `O_NOFOLLOW` file handle + fstat + uid check, with its own doc explaining exactly why ("no TOCTOU since we already have the fd").
**Consequence:** On a shared-filesystem deployment (this ecosystem explicitly runs shared-host Blox agents), an attacker with write access to the keyfile's parent directory could swap/symlink the file between check and read, bypassing the 0600 gate.
**Change:** (a) Port the sibling crate's pattern over. (b) `{file: crates/git-credential-nostr/src/lib.rs, location: lines 28-72, change: "replace the three path-based fs calls with a single OpenOptions...custom_flags(libc::O_NOFOLLOW).open(path), then metadata()/uid checks and read_to_string() on the open handle, mirroring git-sign-nostr's open_keyfile", verify: "add a symlink-rejection test analogous to git-sign-nostr's, confirm cargo test -p git-credential-nostr passes red-then-green", depends_on: none}`

### H10 — `examples/countdown-bot` gets zero CI signal on pull requests
**Location:** `.github/workflows/ci.yml` `changes` job's `rust` path filter
**Evidence:** `examples/**` is absent from the filter list; a PR touching only this example skips lint/build/test entirely (and even the `push`-event fallback is unreliable on this fork — see H12).
**Change:** (a) Add the path. (b) `{file: .github/workflows/ci.yml, location: the "rust:" filter block, change: "add \"- 'examples/**'\"", verify: "a PR touching only examples/countdown-bot/src/main.rs now runs Rust Lint/Unit Tests/Server Cross-Compile", depends_on: none}`

### H11 — `crates/buzz-cli/TESTING.md` documents a `buzz-admin mint-token` subcommand that doesn't exist
**Location:** `crates/buzz-cli/TESTING.md:66-70` vs. `crates/buzz-admin/src/main.rs`'s actual `Command` enum
**Evidence:** `cargo run -p buzz-admin -- mint-token --help` → `error: unrecognized subcommand`. This is documented as the primary path in the CLI's live-testing runbook.
**Change:** (a) Needs a maintainer who knows where token-minting moved to (buzz-auth directly? a seed script?) — not something this audit can prescribe blindly.

### H12 — `ci.yml`'s `push` trigger targets `main`/`release`, never this fork's actual default branch (`launchpad`) — confirmed 0-for-94 runs
**Location:** `.github/workflows/ci.yml:3-5`
**Evidence:** `gh api .../actions/workflows/ci.yml/runs?event=push` → empty; a `--jq` group-by over the last 94 runs shows 100% `pull_request`, 0% `push`. `docker.yml` was correctly updated to include `launchpad` — proving the team does update some workflows for the fork, just missed this one.
**Change:** (a) Add the fork's branch. (b) `{file: .github/workflows/ci.yml, location: line 4, change: "branches: [main, release] -> [main, release, launchpad]", verify: "merge a trivial PR, confirm a new push-triggered run appears", depends_on: none}`

### H13 — Pre-push hooks don't run workspace `clippy`, contradicting CLAUDE.md's Quality Gates claim
**Location:** `lefthook.yml:49-81` vs. CLAUDE.md's "Pre-push hooks run clippy (workspace + Tauri)"
**Evidence:** The only `clippy` invocation in `lefthook.yml` is Tauri-scoped (`desktop-tauri-clippy`); no `cargo clippy --workspace` anywhere in pre-push.
**Change:** (a) Add a workspace-clippy pre-push command, or fix the doc — either is valid, a human should choose. (b) `{file: lefthook.yml, location: pre-push.commands block, change: "add a rust-clippy command running just clippy alongside rust-tests", verify: "lefthook run pre-push on a clippy-triggering branch fails locally before push", depends_on: none}`

### H14 — `buzz-agent`'s README "Security Model" table understates its MCP-child env allowlist by more than 4x
**Location:** `crates/buzz-agent/README.md:298` vs. `crates/buzz-agent/src/mcp.rs:39-94` (`PASSTHROUGH_ENV`, 26 entries not 6)
**Evidence:** The doc claims a 6-variable whitelist and states the operator's `ANTHROPIC_API_KEY` doesn't leak — true, but the real allowlist also passes `SSH_AUTH_SOCK` (the live ssh-agent socket) and `NOSTR_PRIVATE_KEY`/`BUZZ_PRIVATE_KEY`/`BUZZ_AUTH_TAG` through to MCP child processes, none of which the doc mentions.
**Change:** (a) Correct the table or point at the real constant so it can't drift again. (b) `{file: crates/buzz-agent/README.md, location: line 298, change: "list the real 26-entry allowlist or reference PASSTHROUGH_ENV directly, calling out SSH/git/proxy/TLS vars and Buzz identity keys explicitly", verify: "grep PASSTHROUGH_ENV in src/mcp.rs and diff against the README's claim", depends_on: none}`

### H15 — web/'s two invite-page dialogs violate the W3C APG dialog pattern — one has no keyboard dismissal at all
**Location:** `web/src/features/invite/ui/InvitePage.tsx:294-364,366-395`
**Evidence:** Both carry `role="dialog"` + `aria-modal="true"`; Escape handling is gated to only one of the two dialogs; neither traps focus or moves focus in on open; `web/package.json` has no dialog-primitive dependency at all.
**Consequence:** Same pattern as BL3/BL4 (see cross-reference note there) — a keyboard-only user has zero way to close the document/policy dialog.
**Change:** (a) Add Escape handling to both + a real focus trap, or adopt `@radix-ui/react-dialog`. (b) `{file: web/src/features/invite/ui/InvitePage.tsx, location: lines 178-185, 366-395, change: "extend the Escape-close effect to the second dialog; add focus-trap + initial focus + focus-restore to both", verify: "manual keyboard-only walkthrough", depends_on: none}`

### H16 — Two custom "combobox" widgets (desktop) expose zero listbox/option semantics — highlight state is color-only
**Location:** `desktop/src/features/agents/ui/PersonaModelCombobox.tsx:129,179-208`; `desktop/src/features/workflows/ui/ChannelCombobox.tsx:96`
**Evidence:** `role="combobox"` on the trigger, but the popup's rows are plain buttons with no `role="listbox"`/`role="option"`/`aria-selected`/`aria-activedescendant`. Contrast: `agentConfigControls.tsx` implements the correct shape nearby, proving the pattern is known and available in this codebase.
**Change:** (a) Mirror the working implementation. (b) `{file: desktop/src/features/agents/ui/PersonaModelCombobox.tsx and .../ChannelCombobox.tsx, location: popup content, change: "wrap options in role=listbox with id, add aria-controls on the trigger, role=option+aria-selected per row, aria-activedescendant tracking highlightedIndex — mirror agentConfigControls.tsx", verify: "axe/RTL test asserting aria-controls+aria-activedescendant update on Arrow keys", depends_on: none}`

### H17 — Mobile theme picker's selected state is invisible to screen readers
**Location:** `mobile/lib/features/settings/theme_picker_page.dart:220-249`
**Evidence:** `selected` is computed correctly but only conditions a visual checkmark icon; `ListTile`'s first-class `selected:` parameter (which also sets `Semantics(selected: ...)`) is never passed.
**Change:** (a) One-line fix. (b) `{file: mobile/lib/features/settings/theme_picker_page.dart, location: _ThemeRow.build, ListTile(...) at line 220, change: "add selected: selected,", verify: "flutter analyze && flutter test test/features/settings/", depends_on: none}`

### H18 — `buzz-dev-mcp`'s `view_image` tool description falsely tells the agent paths "may not escape" the workspace
**Location:** `crates/buzz-dev-mcp/src/lib.rs:65` vs. `crates/buzz-dev-mcp/src/paths.rs:1-5` and `view_image.rs:803-829` (a test that proves the opposite)
**Evidence:** `paths.rs`'s own doc says "no containment enforcement"; the crate's own test `allows_path_outside_workspace` passes, confirming the tool reads files anywhere the process can read.
**Consequence:** An agent trusting its own tool description would wrongly believe it's sandboxed against reading e.g. `/etc/passwd` or SSH keys.
**Change:** (a) Fix the one false sentence. (b) `{file: crates/buzz-dev-mcp/src/lib.rs, location: line 65, change: "delete the trailing clause 'and may not escape it'", verify: "cargo test -p buzz-dev-mcp --lib view_image, re-read the rendered description string", depends_on: none}`

### H19 — This audit's own preflight lead, confirmed: crate inventory drift with a full git-blame timeline
See merged Medium finding **M1** below — rated Medium by consensus of the 3 shards that found it independently, but flagged here in the High section's cross-reference because of how many docs and how long it's been silently drifting (kept as Medium in the final tally per shard consensus).

---

## Findings — Medium

**M1 — [Merged, found independently by 3 shards] Crate inventory in `CLAUDE.md`/`AGENTS.md`/`ARCHITECTURE.md` has been silently out of date for two months.** Six real workspace members — `buzz-conformance`, `buzz-push-gateway`, `buzz-relay-mesh`, `buzz-voice`, `buzz-backend-kubernetes`, `examples/countdown-bot` — are in `Cargo.toml`'s 29-member workspace list but in none of the three docs. `git blame` shows the docs' crate-list section was last touched 2026-06-29 (the same commit that introduced `buzz-conformance` without listing it), and 4 more crates landed since without ever updating the list. **Fix:** add all six with one-line descriptions to CLAUDE.md/AGENTS.md/ARCHITECTURE.md; verify with a `comm -23` diff of Cargo.toml members vs. the doc's list.

**M2 — Audit hash-chain tamper-evidence has a real, adversarially-proven blind spot at the chain tip.** `crates/buzz-audit`: a hand-crafted test that tampers the *most recent* entry and recomputes a self-consistent hash makes `verify_chain` return `Ok(true)` — false negative. Interior tampering and cross-community replay ARE correctly caught (confirmed via the crate's own, CI-unexecuted tests). Not a coding bug — inherent to hash chains without an external anchor — but undocumented. **Fix:** either `REVOKE UPDATE/DELETE` on `audit_log` from the relay's runtime role, or document the limitation on `verify_chain`'s doc comment.

**M3 — Dead, duplicate reply-counter functions in `buzz-db::thread`.** `increment_reply_count`/`decrement_reply_count` are fully unused (zero call sites, including their own tests); the real, correctly-wired counter logic lives inline in `event.rs`. No live defect (confirmed both paths are correctly wired), but a maintenance trap inviting future divergence. **Fix:** delete the dead functions and the dead `Database::decrement_reply_count` wrapper.

**M4 — `buzz-workflow`'s evalexpr timeout path has zero test coverage of the timeout actually firing.** The 100ms `tokio::time::timeout` wrapper (mitigation for "evalexpr is not designed for adversarial input") is only indirectly exercised by a length-limit test that never reaches the timeout logic. Manually verified the length cap does bound real evaluation time in practice (~1ms at max nesting) — reassuring, but unverified by CI. **Fix:** add a test with a custom evalexpr function that sleeps past 100ms and asserts the timeout error fires.

**M5 — `requires_elevated_authority` (buzz-workflow) is a single hardcoded variant match with no exhaustiveness guard.** Currently correct (only `CallWebhook` reaches an external destination among 7 `ActionDef` variants) but a future exfiltration-capable action variant would silently default to `false` (not requiring elevation) unless someone remembers to touch this function too. **Fix:** convert to an exhaustive `match` with no wildcard arm, so the compiler forces a decision on every new variant.

**M6 — `buzz-persona`'s name-validation logic is implemented twice, independently, contradicting its own doc comment.** `validate.rs`'s header claims it delegates structural checks to `load_pack()`; in reality the character-class/length check is duplicated in `resolve.rs` and `validate.rs`, with `pack.rs` doing neither. Currently in agreement, nothing enforces they stay that way. **Fix:** extract one shared `validate_persona_name()` both call sites use.

**M7 — `buzz-cli`'s documented exit-code contract has zero direct test coverage.** The mapping function itself is correct today, but no test asserts each `CliError` variant maps to its documented exit code (0/1/2/3/4/5) — a future reordering would compile and pass every existing test while silently breaking the contract agent harnesses branch on. **Fix:** add a table test asserting each variant's exit code.

**M8 — Non-Unix keyfile permission checks are a silent no-op in `git-sign-nostr` (parity gap with its sibling crate).** Both signing crates skip real permission enforcement on Windows, but `git-credential-nostr` at least emits a warning; `git-sign-nostr`'s non-unix branch is fully silent. **Fix:** add the equivalent warning for parity (a real Windows ACL check is a larger undertaking, not prescribed here).

**M9 — No test or lint mechanically enforces the desktop community-switch singleton-reset contract.** Zero of 416 desktop test files reference `resetCommunityState`/`useCommunityInit`; no custom lint rule checks new module-level state gets registered. BL5 and BL6 are proof this convention has already been silently violated twice. **Fix:** add at least one integration test asserting a community switch clears every known singleton's observable state — this doubles as the verification test for BL5/BL6.

**M10 — `profileActivityFeedScope.ts`'s `cachedScopes` Map has no reset and grows unbounded across the app's lifetime.** Traced and confirmed it does *not* cause a visible cross-community leak today (equality-checked before substitution), but it's an ever-growing cache with no eviction and no reset hook — exactly the pattern M9's missing enforcement exists to catch. **Fix:** add an exported reset function, wire into `resetCommunityState()`.

**M11 — Mobile: `AvatarImageContent extends StatefulWidget`, the sole exception to CLAUDE.md's "NEVER StatefulWidget" rule.** Confirmed via full-repo grep (the only hit in 260 files). No functional breakage, `flutter analyze` is clean — but the "never" rule has one live, undocumented exception. **Fix:** rewrite with `flutter_hooks` (its state is a textbook `useState`/`useEffect` case), or document the exception explicitly.

**M12 — Mobile: feature-module import isolation is violated pervasively, not as an edge case.** CLAUDE.md states features must not import each other; a full cross-feature import diff shows every feature except `settings/` (5 files) both imports from and is imported by siblings — `channels` (104 files) is the hub. The documented rule doesn't describe the actual, working architecture at all. **Fix:** needs a decision — rewrite the doc to describe reality (e.g. a documented shared-hub pattern) vs. a large refactor toward real isolation; not a quick mechanical fix either way.

**M13 — Mobile: unlabeled, sub-touch-target "clear search" button in theme picker.** Bare `GestureDetector`+`Icon`, no `Semantics`, 16×16 hit target (well under the ~48dp guidance). **Fix:** wrap in `Semantics(button: true, label: 'Clear search', child: IconButton(...))`.

**M14 — Mobile: avatar-tap-to-view-profile in the message timeline is unreachable by screen readers.** Nested inside a row that already exposes its own accessible tap/long-press semantics, but the inner avatar tap adds none of its own — reachable via other entry points, but this specific shortcut is invisible to assistive tech. **Fix:** wrap in its own `Semantics(button: true, label: 'View profile', ...)`.

**M15 — Pre-commit and pre-push hooks do overlap on desktop lint, contradicting CLAUDE.md's explicit "no overlap" claim.** Both run `biome check` + `check:file-sizes` over the same glob (one auto-fixing, one verifying) — a reasonable fix-then-verify pattern, but directly contradicts the stated design. **Fix:** reword the doc, or redesign the hooks — either is valid.

**M16 — No dependency-vulnerability scanning for JS/Dart, no secret scanning, no Dependabot anywhere in this repo.** The only `security` CI job runs `cargo-deny check` and is itself conditionally skipped on PRs that don't touch Rust files (confirmed on a docs-only PR). Desktop/web (pnpm) and mobile (pub) trees have zero automated vulnerability scanning. **Fix:** add `pnpm audit --audit-level=high` for desktop/web at minimum.

**M17 — `docker-compose.yml`'s Keycloak healthcheck can never pass — reproduced live.** Keycloak 26's `start-dev` doesn't expose `/health/ready` on the app port unless `KC_HEALTH_ENABLED=true`, which isn't set anywhere in the repo. `docker inspect` confirms continuous `unhealthy` status. Currently harmless (nothing depends on Keycloak's health today) but a live, reproducible misconfiguration. **Fix:** add `KC_HEALTH_ENABLED: "true"` to the compose environment block.

**M18 — The test-harness fast-path schema (`schema/schema.sql`) is only cross-checked against 3 of 28 migrations by automated test.** `schema.sql` is manually maintained in parallel to the real sqlx migrations specifically so CI/E2E setup can skip running the full migration sequence — but only migrations 20/25/27/28 have an equivalence assertion; 1-24 have none. No confirmed drift found, only a coverage gap in the check that would catch one. **Fix:** needs scoping by the `buzz-db` owner — a full schema-diff test comparing a `pgschema apply`'d DB against a migrated one.

**M19 — Three different "the Rust version" numbers for the same toolchain.** `rust-toolchain.toml` pins `1.95.0`; `Cargo.toml`'s declared MSRV is `1.88.0`; `README.md` tells manual-install contributors to get "Rust 1.88+" — satisfying that literally puts them ~7 minor versions behind what CI (via Hermit) actually uses. **Fix:** bump the README's floor or add a one-line MSRV-vs-pinned-toolchain note.

**M20 — sprout→buzz rename left inconsistent repo references across three files, including within the same document.** `RELEASING.md` calls the same Buildkite pipeline `sprout-releases` at one line and `buzz-releases` two lines later; `Cargo.toml`'s `repository` field still points at `block/sprout`. **Fix:** confirm the live name with whoever owns the pipeline, then make all references consistent.

**M21 — Duplicate ADR number: two accepted decision records both claim ADR-0015.** Both authored by Serina, ~4 hours apart on 2026-08-18 — the repo's own `decisions/README.md` states numbers are never reused. **Fix:** renumber the later one to ADR-0016; check whether any issue/PR text already cites the old number.

**M22 — M0 and M1 GitHub milestones are both 4 days overdue with 46 combined open issues.** An open ADR issue (#93) already exists to resolve this scope/date mismatch but is itself unresolved — no new issue needed, just a decision.

**M23 — `buzz-pair-relay`'s "binds loopback only, must run behind a reverse proxy" doc claim is contradicted by its own reference Helm chart**, which rebinds it to `0.0.0.0` with no Ingress/NetworkPolicy wiring and no chart-level guardrail forcing an operator to add the documented TLS/path-restriction proxy. Not confirmed as directly internet-exposed (Service type not checked). **Fix:** needs a design decision — align the doc to the chart's real posture, or add the missing Ingress/NetworkPolicy to the chart.

---

## Findings — Low (aggregated by theme; full location list available on request)

| Theme | Count | Representative example |
|---|---|---|
| Stale/simplified doc wording (non-blocking) | 5 | CLAUDE.md's "p-gate" description generalizes a narrower, correctly-enforced mechanism (real gate: 6 specific `P_GATED_KINDS`, global-scope only); a stale `resetLinkPreviewTitleCache()` name in CLAUDE.md (actual: `resetLinkPreviewMetadataCache()`); a migration comment claiming "verified on PostgreSQL 16" when the live container is 17 (re-confirmed compatible) |
| Accepted/deliberate, flagged only for completeness | 4 | Dev-only credentials in `docker-compose.yml`/`docker-compose.harness.yml` (`buzz_dev`, `admin`); a documented shared "public Tyler test identity" private key in `Justfile`'s `mesh-dev-fresh` recipe; no down-migration convention anywhere (deliberate, forward-only policy); migration 0007's table-wide lock on `events` (already mitigated by a fail-closed guard, worth an ops-runbook note) |
| Dependency/build hygiene | 4 | `buzz-admin`'s `Cargo.toml` declares 4 unused dependencies (`buzz-search`, `buzz-audit`, `buzz-workflow`, `buzz-media`); `buzz-pair-relay` hardcodes `sha2`/`secp256k1` versions instead of workspace pins, duplicating a compiled C dependency; 71 outdated Flutter packages (staleness only, no deprecations found) |
| Workspace/doc gaps | 3 | `examples/meadow-core` exists on disk but isn't a declared workspace member; mobile's file-size gate is a diff-based ratchet, not a full-repo scan (doc implies otherwise; two files currently sit at 999/1000 lines); `buzz-pair-relay`'s doc says "6 accepted EVENTs" but code counts sig-verified attempts, stricter than documented, not laxer |
| Fork operational hygiene, informational only | 1 | 678 live branches on the fork against 10 open PRs, with no documented cleanup cadence — not itself a problem, no policy exists to judge it against either way |

---

## Positive / non-findings worth recording

- **Migration atomicity is sound.** All 28 migrations run inside sqlx's default per-file transaction; none opts out. A live run of all 28 against a fresh scratch database on the real `buzz-postgres:17-alpine` container succeeded end to end.
- **NIP-29 h-tag channel scoping is genuinely enforced server-side** on both read and write paths, against server-resolved community/membership state, not client-supplied filter values (one small coverage gap noted: 6 kinds that bypass the generic membership gate were only spot-checked 2-of-6 for their per-kind validators).
- **Mobile's Nostr event-kind constants and desktop's `kinds.ts` were fully diffed — zero numeric mismatches** across ~35 shared kinds (one gap flagged as unverified: desktop's `KIND_REMINDER=40007` has no mobile counterpart, unclear if by design).
- **web/ is actively maintained**, not abandoned (commits ~3 weeks apart from desktop), and its Nostr kind handling matches `buzz-core` exactly via shared types rather than magic numbers.
- **`launchpad-pr-check.yml`'s "scripts" job is genuinely mutation-tested** — it rewrites and restores its own control modules to prove they can fail, and its own comment disclaims being a security boundary, an unusually self-aware piece of CI design.
- The DCO commit-msg hook itself (the mechanism, not its enforcement — see H7) works correctly.

---

## Coverage (aggregated across all 7 shards)

| Dimension | Status |
|---|---|
| Invariants, adversarially | Checked in every shard — hand-tampered audit-log rows, all-zero BIP-340 keys, forbidden ActionDef exfiltration paths, hand-built p-gate filters, forbidden UI states. Highest-yield row across the whole audit; source of most High/Medium findings. |
| Tests (falsifiability) | Checked — real suites run against live Postgres/Redis for all Rust crates in scope; `flutter test` and desktop's `pnpm test`/`tsc` run directly. Found 3 currently-red tests (H2, H3, H4) and the systemic H1 gap. |
| Accessibility | Checked as mandatory on desktop, mobile, and web — 4 Blockers, 3 High, several Medium/Low. Not applicable to pure backend Rust shards (explicitly noted, not silently skipped). |
| Dependencies & security | Checked — `cargo-deny`/`pnpm outdated`/secret-pattern greps run directly in every applicable shard. Found the currently-failing security gate (H5) and the JS/Dart scanning gap (M16). |
| Build & CI | Checked — every relevant workflow YAML and Justfile recipe read and cross-referenced against doc claims. Source of H1, H6, H7, H10, H12, H13. |
| Docs vs reality | Checked exhaustively across README/CONTRIBUTING/ARCHITECTURE/RELEASING/TESTING/CLAUDE.md/AGENTS.md/launchpad docs/ADRs. Source of M1, M19-M23, H8, H11, H14. |
| Process & automation | Checked — H6/H7 (gates that are social convention only), M9 (undocumented-in-practice singleton contract). |
| Live project state | Checked — live PR/issue/milestone/branch counts queried fresh via `gh`, not assumed from memory. Source of H8, M21, M22, Low-theme "fork operational hygiene." |

**Not reached / lower depth (stated explicitly per shard, not silently skipped):**
- `buzz-relay`'s huddle-audio, git-smart-HTTP, and mesh-tunnel subsystems — surveyed for structure and covered by the full-crate test/clippy runs, but no dedicated adversarial pass against git-transport auth or audio fencing specifically.
- `buzz-core`'s QR/SAS device-pairing code — surveyed only.
- Desktop's Rust backend (`desktop/src-tauri`) beyond what TS call sites reference — the shard's time went to the mandated a11y sweep and the singleton audit instead.
- Playwright e2e specs were not executed (relied on static CI-wiring confirmation instead).
- 8 of ~11 custom desktop combobox/menu/listbox widgets were grepped for role-pairing but not individually verified for `aria-activedescendant`/keyboard behavior beyond the two flagged in H16.
- A full crate-by-crate `unsafe_code` sweep beyond the two production instances found was not independently re-verified by every shard that touched adjacent crates (only shard G's docs-focused pass did the full 29-crate sweep).

## Unverified Suspicions (carried forward, not asserted as fact)

- Whether desktop's `KIND_REMINDER=40007` gap in mobile is a deliberate scope difference or a missing feature.
- Whether the buzz-relay `mesh_demo` test's second-run hang (H2) is a leaked Redis lease specifically, vs. some other resource leak.
- Whether an org-level GitHub App (not ruleset-based) might independently enforce DCO outside what H6/H7's `gh api` queries could see (the audit's token lacks `admin:org` scope to check this directly).
- Whether `examples/meadow-core`'s exclusion from the workspace is deliberate or an oversight — its purpose wasn't read.
- Whether `buzz-conformance`'s "enforced by code review" claim about new relay endpoints arming `EmitGuard` is actually followed for every current handler (outside the assigned shard).

---

*Methodology: 7 parallel agent shards, each independently running the sweep-every-dimension / evidence-required / full-enumeration-not-spot-check protocol, synthesized here with cross-shard dedup and contradiction notes. No file in this repository was modified in the course of this audit.*
