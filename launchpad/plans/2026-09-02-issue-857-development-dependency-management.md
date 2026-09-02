# Plan — issue #857: document `development/dependency-management.md`

Target: `launchpad/docs/corpus/development/dependency-management.md`
Branch: `task/857-development-dependency-management`
Base revision: `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90` (`origin/launchpad`)

## ALREADY TRUE

Verified at the base revision, in this worktree, before drafting.

- The target file **does not exist**, on this branch or on `origin/launchpad`
  (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus/development`
  lists `build.md`, `debugging.md`, `hermit.md`, `prerequisites.md` only).
- Four sibling `development/` nodes are already merged and are valid relationship
  targets: `corpus-development-build`, `debugging`, `development-hermit`,
  `development-prerequisites`. `corpus-template-procedure` is merged too.
- Rust: root `Cargo.toml` has `[workspace] members` (32 entries — 30 under
  `crates/`, plus `launchpad/crates/knowledge` and `examples/countdown-bot`),
  `exclude = ["desktop/src-tauri"]`, `[workspace.dependencies]` (62 entries,
  from line 46), and a one-entry `[patch.crates-io]` pin for `aws-creds`. Member crates inherit via `{ workspace = true }`.
  `desktop/src-tauri/Cargo.toml` is its own workspace with its own `Cargo.lock`.
- Node: `pnpm-workspace.yaml` covers `desktop`, `web`, `admin-web` plus
  `overrides`, `patchedDependencies` and `allowBuilds`; one root `pnpm-lock.yaml`.
  `just desktop-install` = `pnpm install`; `just desktop-install-ci` =
  `pnpm install --frozen-lockfile`, used by CI in seven workflow call sites.
- Flutter: `mobile/pubspec.yaml` + committed `mobile/pubspec.lock`;
  `just mobile-install` = `flutter pub get`; CI runs `cd mobile && flutter pub get`.
- Hermit: `bin/hermit.hcl` is the **only** `.hcl` file and sets one option
  (`manage-git = true`). Pins live in ten `bin/.<tool>-<version>.pkg` symlinks.
- Automation: root `renovate.json` exists (config:recommended, 3-day cooldown,
  automerge on non-major, `postUpdateOptions: cargo:updateLockfile`, seven
  `packageRules` including four hard version pins). **No** `.github/dependabot.yml`.
- Policy gate: `deny.toml` + CI job `security` running `cargo-deny check`, gated by
  the `rust` paths filter which includes `Cargo.toml`, `Cargo.lock`, `deny.toml`.
- Lockfile-drift enforcement exists for pnpm only (`--frozen-lockfile`). No
  `cargo build --locked` and no `flutter pub get --enforce-lockfile` anywhere.

## STEP 1 — draft the front matter and provenance ledger

Write `id: development-dependency-management`, `type: development`,
`status: draft`, `origin: launchpad`, `audiences: [developer, agent]`.
First ledger entry is the commit citation for `aef93f2c…`. One entry per
substantive claim, each citing a file opened in this session.
Declare three relationships, all confirmed merged on `origin/launchpad`:
`implements → corpus-template-procedure`, `references → development-hermit`,
`references → corpus-development-build`.

**done-when:** front matter parses; every FACT cites a path opened here; no
`confidence` on FACT/TEAM_KNOWLEDGE; every relationship target present in
`git ls-tree origin/launchpad`.

## STEP 2 — write the body against the procedure template

One `#` heading. Sections: overview, *Before you start*, four per-ecosystem
ordered task sequences (Rust / Node / Flutter / Hermit), *Verify*, *Roll back*,
*See also*, *Boundary*, *Relationships*, *Scope and omissions*.
Hermit's canonical content stays in `development-hermit` — link, state the
boundary, do not restate the pin table.

**done-when:** every issue DoD bullet has a section that answers it; exactly one
`#` heading; "front matter" spelled as two words; `evidence` called the
provenance ledger; file under 1000 lines.

## STEP 3 — validate

Run `python3 launchpad/project-intelligence/corpus/validate.py`.

**done-when:** exit 0, PASS, zero errors (UNVERIFIED notices acceptable).

## STEP 4 — earn the commit gate and commit

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as a sole command, confirm OK, then `git add` + `git commit -s` in a separate call.

**done-when:** commit exists on `task/857-development-dependency-management`; no
`--no-verify`; no stamp file touched.

## STEP 5 — verify against the DoD

Re-read the diff line by line against issue #857's checklist; re-open every
citation; confirm exactly one new canonical document; re-run validate.py.

**done-when:** each DoD bullet marked MET or PARTIAL with a reason.

## PARALLEL

None. Steps 1–2 share one file; 3–5 are sequential gates.

## GATES

- `validate.py` exits 0.
- Corpus test suite reports OK before commit.
- Pre-commit/pre-push hooks run unmodified; file-size gate (1000 lines) respected.

## BUDGET

One new file (the node) plus this plan. No edits to any existing corpus node, no
edits to any upstream-owned file.

## OPEN

- Whether the Renovate GitHub App is actually installed on `launchpad-26/buzz`, or
  whether `renovate.json` is inert upstream configuration in this fork, cannot be
  established from the repository contents. Record as a gap, not a claim.
- Whether `cargo-deny check` runs all four check families by default (advisories,
  bans, licenses, sources) is read from `deny.toml`'s section coverage, not from an
  executed run. Record honestly.

## LEFT OUT

- Security-response procedure for a CVE in a dependency — that is a separate node.
- Upstream-merge conflict resolution in lockfiles — separate concern, `launchpad/`
  upstream-intel tooling's subject.
- Editing `renovate.json`, `deny.toml`, or any manifest. This task documents; it
  does not change dependency state.
