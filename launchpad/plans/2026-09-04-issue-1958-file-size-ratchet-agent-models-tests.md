Issue #1958 — bug: file-size ratchet fails on launchpad HEAD (agent_models_tests.rs, 1001 > 1000), blocking every push
Stated size: no `Size` line on the issue (asking was skipped under active auto-mode direction from the caller, who had already scoped this as a bounded mechanical split) -> cap: 8 steps

ALREADY TRUE  (verified against git, worktree at __worktrees/fix-issue-1958-file-size-ratchet, based on origin/launchpad @ aef93f2c2)
  `desktop/src-tauri/src/commands/agent_models_tests.rs` is 1000 physical lines, no trailing
    newline (`wc -l` reports 1000; the file's last byte is `}` not `\n`).
  `desktop/scripts/check-file-sizes-core.mjs::countLines` does `content.split(/\r?\n/).length`,
    which reports 1001 for this content (1000 newline-terminated lines + one non-newline-terminated
    tail segment) — matching the ratchet's own reported `1001 > 1000`.
  `check-file-sizes-core.mjs::resolveBaseRef` compares against `merge-base(origin/main, HEAD)`
    outside CI, or `HEAD^1` in CI. Because this file only exists on the `launchpad` fork branch
    (not yet in upstream `main`), it reads as a *new* file (status "A") against that base for
    every branch cut from `launchpad` — so `baseLines` is `null`, the allowed limit is the flat
    `maxLines` (1000), and 1001 > 1000 fails regardless of what the pushing branch itself changed.
    This is issue #1958's own reproduction against PR #1957, whose diff touches nothing in `desktop/`.
  Six sibling files already exist in `desktop/src-tauri/src/commands/` following a
    `<module>.rs` + `<module>_tests.rs` split-test convention: `agent_models_databricks.rs` /
    `agent_models_databricks_tests.rs` (109 lines, doc comment explicitly says it exists "so the
    shared test file stays under its size ratchet") and `agent_models_update.rs` /
    `agent_models_update_tests.rs` (31 lines). Two more owner modules —
    `agent_models_env.rs` and `agent_models_openrouter.rs` — do NOT yet have their own
    `_tests.rs`, and their functions' tests are the ones bloating the shared file instead.
  `agent_models_tests.rs` is wired via `#[cfg(test)] #[path = "agent_models_tests.rs"] mod tests;`
    at `agent_models.rs:787-789`, with `use super::*;` at its own top — the established pattern
    for every split file in this directory.
  Verified via grep which file actually defines each function each test exercises (all are
    `pub(super)` on `commands`, so visible to every descendant of `commands`, i.e. any of these
    modules' own test children):
    - `agent_models_env.rs`: `effective_discovery_provider`, `env_value_or_process_if_absent`,
      `env_value`, `redaction_env_with_value`.
    - `agent_models_openrouter.rs`: `is_openrouter_provider`, `openrouter_models_url`,
      `filter_openrouter_models`.
    - `agent_models_discovery_config.rs`: `agent_model_discovery_config`,
      `draft_agent_model_discovery_env`.
    - `agent_models_databricks.rs`: `databricks_static_token_error`, `databricks_models_response`,
      `is_databricks_provider`, `should_start_interactive_auth`, `databricks_sign_in_required_error`.
    - `agent_models_update.rs`: `managed_agent_access_policy_changed`.
    - `agent_models.rs` itself: `model_discovery_error`, `normalize_openai_compatible_models`,
      `openai_compatible_models_url`, `anthropic_models_url`, `normalize_anthropic_models`.
  `agent_models_tests.rs` currently has exactly 43 `#[test]`/`#[tokio::test]` functions
    (`grep -c '#\[test\]\|#\[tokio::test'` → 43). This count is the before/after invariant for
    step 5's verification.
  `apply_model_provider_prompt_update`, used by the two "linked-instance write guard" tests, is
    actually defined `pub(super)` in `managed_agent_definition.rs`, not in `agent_models.rs` —
    the current test file only resolves `crate::commands::agent_models::apply_model_provider_prompt_update`
    because a private `use` re-export at `agent_models.rs:8` is visible to its own descendants.
    These two tests are staying in `agent_models_tests.rs` (still a descendant), so this path
    keeps working unchanged; nothing to fix.

STEP 1  Create `agent_models_env_tests.rs`, wired as a child of `agent_models_env.rs`.  [independent]
        Move these 11 tests out of `agent_models_tests.rs` verbatim (bodies unchanged):
        `redaction_env_records_value_used_for_request`,
        `effective_discovery_provider_prefers_the_explicit_provider`,
        `effective_discovery_provider_recovers_baked_provider_when_record_has_none`,
        `effective_discovery_provider_is_none_without_an_explicit_or_env_provider`,
        `env_derived_provider_falls_through_when_its_credential_is_missing`,
        `explicit_provider_still_reports_a_missing_credential`,
        `required_env_returns_a_configured_credential_however_the_provider_was_resolved`,
        `effective_discovery_provider_reads_the_runtimes_own_env_var`,
        `merged_filter_value_overrides_inherited_process_value_even_when_blank`,
        `absent_filter_value_uses_process_value_when_available`,
        `openrouter_credential_redaction_env_records_key`
        (plus their two supporting `const` items, `UNSET_PROVIDER_VAR` and `UNSET_CREDENTIAL`).
        Give the new file a one-paragraph module doc comment mirroring
        `agent_models_databricks_tests.rs`'s (why it's split out, that it reaches `pub(super)`
        items via `use super::*`). Add `#[cfg(test)] #[path = "agent_models_env_tests.rs"] mod
        tests;` to `agent_models_env.rs`, matching the `#[cfg(test)]` gating already used for
        `agent_models.rs`'s own `mod tests`.
        done when: `agent_models_env_tests.rs` exists, contains exactly those 11 `#[test]`
        functions plus the 2 consts, and `agent_models_env.rs` has the new `mod tests;` line.

STEP 2  Create `agent_models_discovery_config_tests.rs`, wired as a child of `agent_models_discovery_config.rs`.  [independent]
        Move these 6 tests: `saved_agent_model_discovery_uses_record_snapshot_for_definition_less_agent`,
        `model_discovery_ignores_stale_record_for_linked_agent`,
        `openrouter_saved_agent_model_discovery_resolves_provider`,
        `openrouter_draft_agent_model_discovery_derives_provider_env`,
        `draft_agent_model_discovery_env_omits_provider_when_absent`,
        `draft_agent_model_discovery_env_layers_all_three_tiers_in_order`.
        Same doc-comment convention and `#[cfg(test)] #[path = ...] mod tests;` wiring as step 1.
        done when: file exists with exactly those 6 tests; `agent_models_discovery_config.rs` has
        the new `mod tests;` line.

STEP 3  Create `agent_models_openrouter_tests.rs`, wired as a child of `agent_models_openrouter.rs`.  [independent]
        Move these 9 tests: `is_openrouter_provider_matches`,
        `openrouter_models_url_uses_default_base_url`,
        `openrouter_models_url_respects_custom_base_url`,
        `openrouter_models_url_strips_trailing_slash`,
        `openrouter_filter_keeps_tools_capable_models`,
        `openrouter_filter_excludes_absent_supported_parameters`,
        `openrouter_filter_excludes_empty_supported_parameters`,
        `openrouter_filter_empty_result_returns_error`,
        `openrouter_filter_preserves_selected_model`.
        Same convention as step 1.
        done when: file exists with exactly those 9 tests; `agent_models_openrouter.rs` has the
        new `mod tests;` line.

STEP 4  Append to the two existing split files, and trim `agent_models_tests.rs` down to its own 11 remaining tests.  [needs 1, 2, 3]
        Append `databricks_filtered_empty_response_is_authoritative`,
        `is_databricks_provider_matches_both_variants`,
        `databricks_interactive_auth_launches_only_without_a_static_token`,
        `databricks_passive_auth_error_has_reachable_create_flow_guidance`,
        `databricks_static_token_error_redacts_echoed_token` to
        `agent_models_databricks_tests.rs` (existing `use super::*;` stays; no new wiring needed
        — the file is already a `mod tests` child of `agent_models_databricks.rs`).
        Append `access_policy_change_requires_runtime_refresh_for_effective_gate_changes` to
        `agent_models_update_tests.rs` (same — no new wiring).
        Leave in `agent_models_tests.rs`: `openai_model_normalization_keeps_agent_text_models`,
        `openai_compat_model_normalization_preserves_provider_specific_ids`,
        `openai_models_url_uses_openai_default_base_url`,
        `anthropic_models_url_uses_anthropic_default_base_url`,
        `anthropic_models_url_accepts_versioned_base_url`,
        `anthropic_model_normalization_uses_display_names`,
        `update_request_mcp_command_parses_for_wire_compat`,
        `update_request_turn_timeout_parses_for_wire_compat`,
        `linked_instance_ignores_model_provider_prompt_writes`,
        `definition_less_instance_accepts_model_provider_prompt_writes`,
        `model_discovery_error_converts_dangling_sentinel_to_sentence`.
        This step is sequential after 1–3 only because it's the point where the giant file
        actually shrinks — do it last so a mid-flight diff never shows two copies of the same test.
        Run this order: append to the two existing files first, then delete the now-moved test
        bodies from `agent_models_tests.rs`, leaving only the 11 above (plus the file's leading
        `use super::*;`).
        done when: `wc -l desktop/src-tauri/src/commands/agent_models_tests.rs` shows a large drop
        from 1000 and `grep -c '#\[test\]\|#\[tokio::test'` on that file reports 11.

STEP 5  Verify no test was silently dropped and every file compiles and runs.  [needs 4] ← RUNS HERE
        Run, from the worktree root:
        `grep -rho '#\[test\]\s*\n\s*\(async \)\?fn [a-z_0-9]*' desktop/src-tauri/src/commands/agent_models*_tests.rs | wc -l`
        (or equivalent) and compare against the pre-split count of 43 captured above.
        Then run `cargo test --manifest-path desktop/src-tauri/Cargo.toml agent_models` (plain
        `cargo test` at repo root does NOT include this crate — it's excluded from the root
        workspace) and confirm the reported pass count is 43 and the set of test names printed
        with `--list` matches the pre-split list exactly (diff the two `--list` outputs, captured
        before step 1 and after step 4).
        done when: `cargo test --manifest-path desktop/src-tauri/Cargo.toml agent_models_` compiles
        cleanly and reports the same 43 tests passing, by name, as the pre-split run.

STEP 6  Confirm the ratchet itself now passes.                                   [needs 5]
        Run `just file-size-check` (or `node desktop/scripts/check-file-sizes.mjs` directly) from
        the worktree. Every new/changed file under the 1000-line rule must show comfortable margin,
        not a bare squeak-under.
        done when: the command exits 0 and its output shows no violation for any
        `agent_models*.rs`/`agent_models*_tests.rs` file.

STEP 7  Commit and push.                                                         [needs 6]
        `git commit -s` (DCO required — do not skip). Do not amend, do not force-push, do not use
        `--no-verify`. The pre-push `file-size-check` lane will itself exercise the exact bug this
        PR fixes; expect it to pass now that step 6 already proved it clean locally.
        done when: `git log -1 --format=%B` shows a `Signed-off-by:` trailer and `git push` (no
        force flags) succeeds against the new branch.

STEP 8  Open the PR against `launchpad`.                                         [needs 7]
        `gh pr create` as a standalone command (no `cd` prefix — the repo's `pr-gate.sh` hook
        rejects a chained `cd && gh pr create`). Base `launchpad`. Body includes "Closes #1958".
        Check 2–3 recent agent-authored merged PRs' labels
        (`gh pr list --repo launchpad-26/buzz --search "is:merged label:by:agent" --limit 3 --json
        number,labels`) to decide whether to add `by:agent` to match convention. Expect the
        `pr-gate.sh` hook's `review-final` ledger requirement to fall back to draft PR via its own
        documented escape valve — do not fight that, it is expected per the issue's own prior-agent
        note.
        done when: a PR (draft or ready) exists on GitHub with `Closes #1958` in its body,
        `pr-gate.sh`'s output (or its escape valve) is captured, and its URL is reported.

PARALLEL  Steps 1, 2, 3 touch three disjoint new files (`agent_models_env_tests.rs`,
          `agent_models_discovery_config_tests.rs`, `agent_models_openrouter_tests.rs`) plus three
          disjoint one-line wiring edits (`agent_models_env.rs`, `agent_models_discovery_config.rs`,
          `agent_models_openrouter.rs`) — genuinely independent, could be three subagents. Step 4
          must wait for all three (it deletes the moved bodies from the shared source file and
          appends to two more existing files) to avoid a step racing against content step 4 is
          about to delete. Steps 5–8 are strictly sequential — each gates on the previous one's
          proof (test parity → ratchet green → commit → PR).
GATES     `serina:review-code` after step 4 (mechanical move, but still a diff worth a second look
          for a copy/paste error). `serina:review-tests` after step 5, since this whole issue is
          about test-file structure — confirm no test lost its assertions in the move, not just
          its line count. `qa` explore mode does not apply: this is a pure test-code reorganisation
          with no runtime/CLI/UI surface to exercise: the "explore" step already *is* step 5's
          test run. `serina:review-final` per this repo's `build-change`/`pr-gate.sh` pipeline
          before the PR is considered ready (expected to land as a draft-PR escape valve per the
          issue's own note — see step 8).
BUDGET    Step 4 is where the budget risk lives: manually trimming `agent_models_tests.rs` down to
          exactly its 11 remaining tests, without a stray duplicate or a truncated function, is the
          one step where a copy/paste slip is easy and only step 5's exact-count diff will catch it.
OPEN      The issue does not say whether the six-way split-by-owner-module below is the intended
          shape versus a simpler 2-way split (e.g. "first half / second half"). This plan chose
          split-by-true-owner because it exactly matches this directory's own established
          `<module>.rs`/`<module>_tests.rs` convention (two files already do this, one's doc
          comment literally cites the size ratchet as the reason) and gives every resulting file
          large margin rather than a bare pass.
LEFT OUT  Not touching `check-file-sizes-core.mjs`'s `countLines` off-by-one-on-trailing-newline
          behavior, even though it's arguably a separate latent bug (every trailing-newline file
          in the repo is counted 1 line high). AGENTS.md is explicit: "never bump the limit or add
          an override to slip under it" — changing the counting function is the same category of
          workaround and out of scope for a "split the file" fix. Not touching any other file in
          the repo that may also sit near/over the 1000-line ratchet — issue #1958 names only
          `agent_models_tests.rs`.
