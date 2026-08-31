Issue #1057 — task: document layers/configuration/relay-configuration.md
Stated size: no `Size` line/label on the issue itself → cap: 5 steps, per the
corpus-batch-author dispatch brief governing this run.

ALREADY TRUE  (verified against git and the working tree, not notes)
  Worktree `/home/serina/Launchpad/buzz/__worktrees/task-1057-relay-configuration` exists on
    branch `task/1057-relay-configuration`, clean, HEAD `338b4d0cf` — same corpus-tree object
    (`git ls-tree -d HEAD -- launchpad/docs/corpus` and the same command against
    `origin/launchpad` both report tree `efdf91b05ccdd88f0c503334c10aa44047e77cf7`), so this
    worktree's corpus content is not behind `origin/launchpad` even though the branch is 206
    commits behind overall.
  `launchpad/docs/corpus/layers/` does not exist anywhere in the corpus tree yet — this is the
    first node under `layers/`, not a case of matching an already-merged sibling file (the
    task brief's premise that one exists was checked and does not hold; the precedent used
    below instead comes from the `architecture/` surface, which does have merged examples).
  `node.schema.json`'s `type` enum includes `layers` as one of its 13 members, so the value is
    real, not invented.
  `architecture/containers/relay.md` (merged, id `architecture-containers-relay`, type
    `architecture`) establishes the corpus's own `id`/`type` convention for a path-mirrored
    node: `id` = the path's directory segments plus basename, kebab-joined
    (`architecture-containers-relay` for `architecture/containers/relay.md`); `type` = the
    top-level directory name. Applied to this task's target path
    (`layers/configuration/relay-configuration.md`), that yields `id:
    layers-configuration-relay-configuration` and `type: layers` — matching what the task
    brief specifies, now confirmed against a real merged example rather than assumed.
  `launchpad/docs/corpus/templates/configuration.md` (merged, id `corpus-template-configuration`,
    type `governance`) is the assigned template. Its own *Expected but not verified* section
    names this exact document as the test case: *"No node has yet been authored from this
    template... The first real configuration node -- likely buzz-relay's environment
    variables, given crates/buzz-relay/src/config.rs's size -- is what will actually test
    whether the required sections above are sufficient."* This task is that first instance.
  `crates/buzz-relay/src/config.rs` (1736 lines) defines `pub struct Config`, its two nested
    structs `AdminConfig`/`JoinPolicyConfig`, and `impl Config::from_env()`. A grep for
    quoted `[A-Z][A-Z0-9_]{3,}` names across the file finds 81 distinct environment-variable
    names read via `std::env::var`/`std::env::var_os` (some read more than once, e.g.
    `BUZZ_GIT_HOOK_HMAC_SECRET`). `crates/buzz-relay/src/main.rs` calls `Config::from_env()`
    exactly once, at process startup (line 142); an `Err` propagates through `anyhow` and the
    process exits before serving any traffic (fail-closed on bad config). `state.rs:632,858`
    stores the loaded value as `pub config: Arc<Config>` inside `AppState`, with no
    interior-mutability wrapper and no reload/SIGHUP/watch code found anywhere in
    `crates/buzz-relay/src/*.rs` — the surface is load-once, restart-required, never
    dynamically reloadable.
  No `clap` dependency or CLI-arg parsing exists anywhere in `crates/buzz-relay` (checked
    `Cargo.toml` and every `src/*.rs` for the string `clap`) — the relay's config surface is
    environment-variable only; there is no CLI-flag surface to document for this crate.
  `.env.example` (root, 252 lines) and `deploy/charts/buzz/values.yaml` (a real Helm chart,
    lines 83-95 list the exact secret-bearing keys — `BUZZ_RELAY_PRIVATE_KEY`,
    `BUZZ_GIT_HOOK_HMAC_SECRET`, `DATABASE_URL`, `READ_DATABASE_URL`, `REDIS_URL`,
    `BUZZ_S3_ACCESS_KEY`, `BUZZ_S3_SECRET_KEY` — with no live values, only comments) are both
    real, citable, non-secret deployment examples for the required "deployment examples"
    DoD bullet.
  Two real, already-in-code compatibility/deprecation examples exist to ground the DoD's
    "compatibility/deprecation" bullet without inventing one: (1) `BUZZ_REPLICA_HEAD_MAX_AGE_SECS`
    is a hard startup error (renamed to `BUZZ_REPLICA_READ_MAX_AGE_MS`, `config.rs:474-482`);
    (2) `INERT_MEDIA_READ_AUTH_VARS` (`BUZZ_REQUIRE_MEDIA_GET_AUTH`,
    `BUZZ_REQUIRE_MEDIA_READ_AUTH`, `config.rs:434-457,800-806`) are accepted but ignored,
    with a startup warning naming them inert.

STEP 1  Write the front matter and full body of                                [independent]
        `launchpad/docs/corpus/layers/configuration/relay-configuration.md` against
        `templates/configuration.md`'s required sections (Configuration description,       ← RUNS HERE
        Settings table, Litmus test, Secrets discipline, Boundary, Relationships, Scope and
        omissions), covering every one of the 81 environment variables `config.rs` reads —
        grouped by the `Config` struct's own field-order sections (network/pool, auth,
        rate limits, media/S3, git server, push gateway, join policy/admin, web UI) rather
        than alphabetically, per the template's own row-order rule. Front matter: `id:
        layers-configuration-relay-configuration`, `type: layers`, `status: draft`, `origin:
        launchpad`, `audiences: [agent, developer, operator, reviewer]`, an `evidence` entry
        per substantive claim (commit citation for the recorded revision, `config.rs`/
        `main.rs`/`state.rs` citations for load-once/fail-closed/no-CLI-flags, `.env.example`
        and `deploy/charts/buzz/values.yaml` for deployment examples, the two compatibility
        examples above), no `relationships` unless `architecture-containers-relay` (confirmed
        merged on `origin/launchpad`) is genuinely used as a `part-of` target. Never quote a
        live secret value — only variable names, code paths, and placeholder/dev-only values
        already committed in `.env.example`.
        done when: the file exists, every one of the 81 variable names above appears as a
        table row, and every required section from the template is present as a heading.

STEP 2  Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo root.  [needs 1]
        done when: the run's final line is `PASS` (pre-existing `UNVERIFIED` notices
        elsewhere are expected and not a failure; fix anything this node itself introduces
        and re-run until clean).

STEP 3  Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p  [needs 2]
        "test_*.py"` as the sole command in one tool call; confirm it prints `OK`. In a
        SEPARATE tool call, `git add` the new document plus this plan file and
        `git commit -s` with message `docs(corpus): document relay configuration (#1057)`.
        Never combine the verify and commit calls, never `--no-verify`.
        done when: the unittest run prints `OK`, and a new commit exists on
        `task/1057-relay-configuration` whose message matches exactly.

STEP 4  Self-review: re-read the committed document line by line against every bullet in     [needs 3]
        issue #1057's own Definition-of-done checklist, and run `git show --stat HEAD`.
        done when: every DoD bullet is confirmed satisfied in the committed text (not just
        planned), and `git show --stat HEAD` names only the corpus document and this plan
        file — no second canonical document, no generated/index file.

PARALLEL  None — one file, four sequential steps in one worktree; step 1 is the only
  independent step and every later step needs the one before it.

GATES     `validate.py` must end `PASS` (step 2). The unittest suite must print `OK` before
  any commit (step 3), run as its own tool call, never combined with the commit. No push, no
  PR, no `review-adjudicate`/cross-model final review in this session — per the task's
  explicit instruction, those are the batch owner's to run once all 36 sibling documents are
  cherry-picked onto one shared branch.

BUDGET    One document, one sitting. The settings table is large (81 rows across roughly
  eight subsystem groups) because the DoD requires "type/shape, source, default/required
  behavior and validation" per setting, not a sample — this is the deliberate cost of being
  the template's own first real test case, not scope creep.

OPEN      The template predicted its first instance would test "whether the required
  sections above are sufficient or need revision" — this plan chooses full enumeration of
  all 81 variables over a representative sample, since the issue's DoD asks for
  default/required/validation per setting rather than "a settings surface exists." If a
  reviewer judges a sampled table sufficient instead, that is a scope call for review, not
  one this plan makes unilaterally.

LEFT OUT  A CLI-flag surface: `buzz-relay` has none (verified — no `clap` dependency, no
  arg parsing anywhere in the crate), so the document says so rather than inventing rows.
  `main.rs`'s own separate environment reads outside the `Config` struct (`RUST_LOG`,
  `BUZZ_AUTO_MIGRATE`, `BUZZ_USAGE_METRICS_PER_COMMUNITY`, `storage_sweep::
  StorageSweepConfig::from_env`) — these are a different struct/module's surface, not
  `config.rs`'s `Config`, and folding them in would violate the corpus's one-idea-per-node
  rule. Secrets-handling mechanism generally (#1058), the environment-variable loading
  mechanism generally (#1054), desktop/mobile/agent-side configuration (#1053/#1056/#1051),
  configuration validation framework (#1059), and configuration-defaults policy (#1052) are
  all sibling child issues under Feature #611 and are explicitly out of this task's scope.
