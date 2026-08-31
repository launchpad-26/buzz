Plan: issue #1052 — document layers/configuration/defaults.md

Issue #1052 (child of Feature #611, parent PRD #602/#605-family corpus build-out)

Stated size: not given an explicit Size line in the issue body -> cap: 5 steps (per
task instruction capping this plan at 5 steps)

ALREADY TRUE

- `launchpad/docs/corpus/layers/` does not exist anywhere on `origin/launchpad`
  (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` lists only
  `AGENTS.md`, `README.md`, `schema/**`, `standards/**`, `templates/**` — no
  `layers/` subtree and no prior `type: layers` node exists to copy front matter
  from). The issue's instruction to "check one" sibling `layers` node for
  front-matter shape has no target on `origin/launchpad` yet; this plan follows
  `node.schema.json` + `AGENTS.md` directly instead, and records that gap in OPEN
  rather than inventing a precedent.
- `node.schema.json`'s `type` enum is 13 fixed values: `architecture`, `layers`,
  `capabilities`, `platforms`, `implementation`, `interfaces-events`, `verification`,
  `operations`, `development`, `release`, `governance`, `agent`, `ingestion`.
  `layers` is the correct value — this node documents a corpus surface (the
  configuration layer's default-resolution mechanism), not corpus-authoring
  governance.
- `launchpad/docs/corpus/layers/configuration/defaults.md` does not exist (`ls`
  confirms the `layers` directory itself is absent).
- Sibling tasks #1051/1053/1054/1056/1057/1058/1059 own each surface's *specific*
  settings (agent, desktop, environment, mobile, relay, secrets, validation). This
  node stays scoped to the cross-cutting *mechanism*: how a default value is decided
  and what precedence order resolves it, illustrated with mechanism-level evidence
  from more than one surface, never a full settings catalogue for any one surface.
- Real, opened evidence for the mechanism, gathered this session (paths, not just
  descriptions):
  - `crates/buzz-relay/src/config.rs` — `Config::from_env()` doc comment: "Loads
    configuration from environment variables, falling back to development
    defaults." Concrete pattern: `std::env::var("NAME").unwrap_or_else(|_| "literal
    default".to_string())` (bind_addr, database_url, redis_url, relay_url) and
    `std::env::var("NAME").ok().and_then(|v| v.parse().ok()).filter(...).unwrap_or(N)`
    for numeric settings with validation (redis_pool_size, db_pool_size).
  - `crates/buzz-cli/src/lib.rs` lines 63-95 — clap derive: `#[arg(long, env =
    "BUZZ_RELAY_URL", default_value = "http://localhost:3000")]`, and the CLI's own
    `long_about` states outright: "Configuration (flags override env vars)"; the
    field's doc comment says "Overrides BUZZ_RELAY_URL env var." First-party,
    self-documented three-tier precedence: explicit flag > env var > baked
    `default_value`.
  - `Justfile` line 3 — `set dotenv-load := true`: `.env` is loaded into the process
    environment by the `just` task runner itself, not by any `buzz-*` binary.
    Cross-checked against `Cargo.lock`: `dotenvy` appears only as a dependency of
    `sqlx-macros-core`/`sqlx-mysql`/`sqlx-postgres` (compile-time query-macro
    resolution), never of `buzz-relay`, `buzz-cli`, or any other `buzz-*` crate — so
    at runtime a `.env` value and a truly-exported shell env var are indistinguishable
    to `std::env::var`; `.env` is a dev convenience layered in before the process
    starts, not a second runtime precedence tier the code itself implements.
  - `.env.example` header: "All defaults here work with `docker compose up` out of
    the box," and individual commented-out lines (e.g. `# BUZZ_REDIS_POOL_SIZE=16`)
    match the code's own hardcoded fallback exactly — confirming `.env.example`
    documents a *suggested* value, while the authoritative default is whatever the
    loading code falls back to, per Twelve-Factor's own config/code distinction.
  - `mobile/lib/shared/relay/relay_provider.dart` lines 62-72 — `Env.relayUrl =
    String.fromEnvironment('BUZZ_RELAY_URL', defaultValue: 'http://localhost:3000')`,
    doc comment: "Compile-time environment config via --dart-define." A third,
    structurally distinct mechanism: the default and the override are both baked
    into the binary at build time; changing either requires a rebuild, not a
    restart.
  - `desktop/src/shared/features/resolveEnabled.ts` — `overrides[featureId] ??
    defaultEnabled` (default parameter `false`); `desktop/src/shared/features/
    useFeatureEnabled.ts` doc comment: "in manifest (preview): explicit user
    override, then manifest default (off if omitted); NOT in manifest (stable):
    always true (fail-open)." A fourth mechanism: a static manifest default,
    overridable at runtime by a user preference persisted in `localStorage`,
    reactive without restart via `useSyncExternalStore`.
  - `desktop/src/shared/features/manifest.ts` — schema validation failure on the
    bundled manifest itself falls back to `EMPTY_MANIFEST` (`{version: 1,
    features: []}`) with a `console.warn`, rather than crashing the app: a
    fail-open default at the manifest-loading layer itself, one level above any
    single feature's default.
- `launchpad/docs/corpus/templates/configuration.md` exists **only** on this task's
  own worktree/unmerged branches, not on `origin/launchpad` (confirmed by the same
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` check
  above). Its Twelve-Factor-App-plus-Good-Docs-Project framing is a genuinely useful
  industry-model lens for what counts as configuration at all, but since it is not
  merged into the target branch this node ships to, this node cites the primary
  source (`12factor.net/config`) directly rather than treating the unmerged
  template as an authority, and declares no `references` edge to it (unmerged =
  can't resolve in CI per `AGENTS.md` step 9's merge-target rule).

STEP 1 — Confirm scope, non-duplication and the schema/AGENTS.md contract [independent]

Re-read `node.schema.json`, `AGENTS.md`, and issue #1052's DoD checklist side by
side; confirm no corpus node already covers this (nothing under
`origin/launchpad`'s `launchpad/docs/corpus/` mentions configuration defaults —
confirmed above from the `git ls-tree` listing). Decide the `id`:
`layers-configuration-defaults` (matches the issue's target path, permanent per
`AGENTS.md` step 4).

done when: `id`, `type: layers`, `status: draft`, `origin: launchpad` are settled
and traceable to the ground-truth checks above, with no unresolved naming question.

STEP 2 — Draft the node body against the DoD checklist <- RUNS HERE [needs 1]

Write `launchpad/docs/corpus/layers/configuration/defaults.md`: front matter (id,
type, status, origin, audiences, evidence — no `relationships`, since nothing in
`origin/launchpad`'s corpus tree is a fit, matching the same reasoning
`corpus-template-configuration`'s own (unmerged) ledger used for its four merged
siblings) plus a body covering, per issue #1052's own DoD bullets:

- type/shape, source and default/required behavior for each mechanism family
  documented (env-var+code-fallback, CLI-flag-over-env, compile-time
  `--dart-define`, runtime manifest+override), and how each is validated (numeric
  parse-with-filter-and-fallback for the Rust case; zod schema validation with a
  fail-open empty-manifest fallback for the desktop case);
- whether each mechanism is sensitive/secret (never — this node documents no
  specific secret values; that is `#1058`'s scope), environment-specific,
  restart-required (Rust runtime env fallback: yes, read once at `Config::from_env`
  call; CLI: re-evaluated per invocation; Dart `--dart-define`: rebuild required,
  not merely restart; desktop feature manifest: no restart, reactive) or
  dynamically reloadable;
- effects/failure behavior (fail-open empty-manifest fallback in
  `desktop/src/shared/features/manifest.ts`; numeric env vars that fail to parse or
  fail a positivity filter silently fall back to the coded default rather than
  erroring) and compatibility/deprecation (`.env.example`'s own documented
  `BUZZ_ADMIN_TOKEN` removal-but-still-read-and-warned pattern as a real in-repo
  compatibility example, cited but not re-explained);
- links to the concrete implementation sites above as evidence, and a Scope and
  omissions section naming every sibling surface issue this node defers to plus
  what was expected but not independently checked (mobile's own manifest-equivalent
  mechanism beyond the single `Env.relayUrl` example; whether every relay `Config`
  field follows the two patterns quoted or whether exceptions exist elsewhere in
  the 733-line file).

done when: the file exists, every substantive claim has an `evidence` entry
classified FACT/INFERENCE/TEAM_KNOWLEDGE per `AGENTS.md`, every FACT cites a source
actually opened this session, and every DoD bullet in issue #1052 is addressed
somewhere in the body (checked line-by-line against the issue text).

STEP 3 — Validate and test [needs 2]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo root
and confirm it ends `PASS`. Run `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in
its own tool call and confirm `OK`. Fix any reported error (never silence or route
around it) and re-run both until clean.

done when: both commands are run as separate calls, `validate.py` prints `PASS`,
and the unittest run prints `OK`.

STEP 4 — Commit [needs 3]

`git add` the new corpus document and this plan file only; `git commit -s` with
message `docs(corpus): document configuration defaults (#1052)`. Do not push, do
not open a PR — this ships later as part of one shared PR for all 36 #611
children.

done when: `git show --stat HEAD` shows exactly the corpus doc plus this plan
file, and the commit carries a `Signed-off-by` trailer.

STEP 5 — Self-review [needs 4]

Re-read the committed document line by line against issue #1052's DoD checklist,
confirm `git show --stat HEAD` shows no unexpected second file, and confirm no
`relationships` block was added pointing at anything unmerged
(`corpus-template-configuration` in particular, since it is real, useful, and
tempting to cite as a target, but unmerged).

done when: every DoD bullet is checked off against the actual committed text (not
the plan's intent), and the two-file diff is confirmed.

PARALLEL

Nothing in this plan runs concurrently with anything else — it is a single-file
authoring task with a strict read-then-write-then-validate-then-commit order, and
sibling issues #1051/1053/1054/1056/1057/1058/1059 are separate worktrees
authoring independently, not part of this plan's parallelism.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must print `PASS`
  before commit (Step 3).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
  "test_*.py"` must print `OK`, run as its own call, never combined with the
  validate command or the commit (Step 3).
- No `git push`, no `gh pr create` — explicitly out of scope for this task.

BUDGET

One new file (`launchpad/docs/corpus/layers/configuration/defaults.md`) plus this
plan file. No code changes, no other corpus files touched. Five steps, capped as
stated above.

OPEN

- No merged `type: layers` sibling exists on `origin/launchpad` to copy
  front-matter shape from, despite the task instructions assuming one exists. This
  plan proceeds directly from `node.schema.json` + `AGENTS.md` instead; a human
  should confirm this is acceptable rather than blocking on a precedent that does
  not yet exist.
- Whether `corpus-template-configuration` (`#1332`, unmerged) should later gain a
  `references` edge from this node once both are merged and its `id` is confirmed
  present on `origin/launchpad` — deliberately left undeclared here per
  `AGENTS.md`'s merge-target rule.

LEFT OUT

- Any specific surface's settings table (agent/desktop/environment/mobile/relay/
  secrets/validation) — each owned by its own sibling issue (#1051/1053/1054/1056/
  1057/1058/1059); this node illustrates the cross-cutting mechanism with a small,
  representative set of citations from more than one surface, not an exhaustive
  catalogue of any one.
- A full field-by-field audit of `crates/buzz-relay/src/config.rs` (733 lines) —
  two representative patterns (string-with-fallback, numeric-with-parse-filter-
  fallback) are cited as the mechanism; auditing every field is out of scope and
  named as an open gap in the node's own Scope and omissions section.
- Declaring a `references`/`implements` relationship toward
  `corpus-template-configuration` (#1332) or any other unmerged sibling node — none
  are on `origin/launchpad`, so none can resolve in CI.
