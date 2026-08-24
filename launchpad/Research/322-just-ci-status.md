---
description: Whether `just ci` passes on launchpad-26/buzz today — it does not, and the three reasons why are all parity gaps between the local gate and CI rather than product defects.
tags: [testing, ci, just, parity, flaky-tests, timezone, pnpm, research, issue-322]
---

# Does `just ci` pass on this fork today?

## Finding

**No. `just ci` fails at `mobile-test`, and on Intel macOS it cannot run to completion at all.**

Neither failure is a defect in Buzz. Both are **parity gaps between `just ci` and CI** — the
command that ADR-0020 adopts as "the contract, locally identical to CI" is not locally identical
to CI, in three concrete and separately-fixable ways:

1. **Three of the seven recipes cannot execute on Intel macOS**, because the repo pins
   `pnpm@11.4.0` and pnpm stopped publishing macOS-Intel builds at v11.0.5.
2. **Four `mobile-test` tests are timezone-dependent** and fail at UTC+12/+13. They pass in CI
   because GitHub runners are UTC.
3. **`just test-unit` runs a different test set depending on whether `cargo-nextest` is
   installed** — two branches, silently.

The practical consequence for #290: a document stating what `just ci` guarantees cannot say
"locally identical to CI" without qualification, and criterion 5's gate would be sound in CI
while the local promise it rests on is false for at least two classes of developer machine.

## What was run

Measured at `launchpad` tip `678008ea49e790ada52e84d54b47f47dd77c6b38`, in a clean worktree with
`. ./bin/activate-hermit` sourced. Host: `Darwin x86_64` (Intel macOS 24.6.0), timezone
`Pacific/Auckland`.

`just ci` chains seven recipes (`justfile:292`):

```
ci: check test-unit desktop-test desktop-build desktop-tauri-check desktop-tauri-test web-build mobile-test
```

and `check` expands to seven more (`justfile:95`):

```
check: fmt-check clippy desktop-check desktop-tauri-fmt-check desktop-tauri-clippy web-check mobile-check
```

Rather than invoke `just ci` and stop at its first failure, each leaf recipe was run
individually so every one gets its own verdict. Raw result:

```
RECIPE fmt-check EXIT 0 ELAPSED 5s
RECIPE clippy EXIT 0 ELAPSED 593s
RECIPE desktop-tauri-fmt-check EXIT 0 ELAPSED 8s
RECIPE desktop-tauri-clippy EXIT 0 ELAPSED 340s
RECIPE test-unit EXIT 0 ELAPSED 538s
RECIPE desktop-tauri-check EXIT 0 ELAPSED 99s
RECIPE desktop-tauri-test EXIT 0 ELAPSED 666s
RECIPE mobile-check EXIT 0 ELAPSED 77s
RECIPE mobile-test EXIT 1 ELAPSED 291s
```

Total wall-clock for the nine runnable recipes: **2,617s ≈ 44 minutes** on this hardware.

### Per-recipe verdict

| Recipe | Verdict | Note |
|---|---|---|
| `fmt-check` | **pass** | 5s |
| `clippy` | **pass** | 593s cold |
| `desktop-check` | **not runnable** | needs pnpm |
| `desktop-tauri-fmt-check` | **pass** | 8s |
| `desktop-tauri-clippy` | **pass** | 340s |
| `web-check` | **not runnable** | needs pnpm |
| `mobile-check` | **pass** | 77s — `dart format`, `flutter analyze`, file-size ratchet |
| `test-unit` | **pass** | 538s — but see §3, it took the fallback branch |
| `desktop-test` | **not runnable** | needs pnpm |
| `desktop-build` | **not runnable** | needs pnpm |
| `desktop-tauri-check` | **pass** | 99s |
| `desktop-tauri-test` | **pass** | 666s |
| `web-build` | **not runnable** | needs pnpm |
| `mobile-test` | **FAIL** | exit 1 — 1,461 passed, 4 failed |

Eight of the nine recipes that can run on this host pass. One fails. Five cannot run.

## 1. Why five recipes cannot run on Intel macOS

`package.json:4` pins the package manager:

```json
  "packageManager": "pnpm@11.4.0",
```

Hermit cannot resolve it here:

```
$ bin/pnpm --version
fatal:hermit: https://github.com/cashapp/hermit-packages.git/pnpm.hcl: pnpm-11.4.0: no source provided
```

This is deliberate upstream behaviour in the hermit manifest, which documents the reason in a
comment:

```
// pnpm dropped the `pnpm-darwin-x64.tar.gz` (macOS Intel) asset starting
// v11.0.5 (https://github.com/pnpm/pnpm/releases/tag/v11.0.5). Omit
// `platform "darwin" "amd64"` here entirely so the resolver returns
// ErrNoSource for it and `manifest auto-version --update-digests` skips
// probing the missing URL.
```

The manifest carries `pnpm-linux-x64.tar.gz` for 11.4.0 but no `darwin-x64`:

```
$ grep "v11\.4\.0" .../pnpm.hcl
  ".../v11.4.0/pnpm-linux-x64.tar.gz": "f3f8d1217eef..."
  ".../v11.4.0/pnpm-darwin-arm64.tar.gz": "ba59014c2c1c..."
  ".../v11.4.0/pnpm-linux-arm64.tar.gz": "cc38ebd5b261..."
```

So every pnpm-dependent recipe is unrunnable on any Intel Mac. CI is unaffected — the desktop and
web jobs run `ubuntu-latest`, which is linux/amd64 and has a source.

**This is not a fork defect and not fixable within the fork** without changing the pin, which is
an upstream file. It is a fact about who can run the local gate: Apple-Silicon and Linux
developers can, Intel-Mac developers cannot.

## 2. Why `mobile-test` fails — four timezone-dependent tests

`flutter test` ran 1,465 tests; 1,461 passed and 4 failed:

```
00:19 +1461 -4: Some tests failed.
error: Recipe `mobile-test` failed on line 683 with exit code 1
```

The four:

```
mobile/test/features/pulse/note_card_test.dart: constrains timestamp with agent and follow metadata
mobile/test/features/pulse/compose_note_page_test.dart: reply preview constrains its timestamp at large text sizes
mobile/test/features/forum/forum_widgets_test.dart: ForumPostCard constrains an older timestamp at large accessible text sizes
mobile/test/features/forum/forum_widgets_test.dart: ForumThreadPage constrains post and reply timestamps at large text sizes
```

All four fail the same way — a finder matching nothing:

```
The following StateError was thrown running a test:
Bad state: No element

#0      Iterable.single (dart:core/iterable.dart:694:25)
#1      WidgetController.widget (package:flutter_test/src/controller.dart:823:30)
#2      main.<anonymous closure> (.../compose_note_page_test.dart:86:30)
```

### Root cause

Each test builds a fixture timestamp as **UTC noon** and asserts the **rendered date string**:

```dart
// mobile/test/features/pulse/compose_note_page_test.dart:73,86
createdAt: DateTime.utc(2025, 9, 30, 12).millisecondsSinceEpoch ~/ 1000,
...
final timestamp = tester.widget<Text>(find.text('Sep 30'));
```

The formatter converts that epoch to **local** time, not UTC:

```dart
// mobile/lib/features/pulse/note_card.dart:318-319
String formatPulseRelativeTime(int createdAt) {
  final date = DateTime.fromMillisecondsSinceEpoch(createdAt * 1000);
  ...
  return '${months[date.month - 1]} ${date.day}';
```

At UTC+13 (New Zealand daylight time, in force on 30 September) the epoch lands on the *next
calendar day*:

```
$ python3 -c "..."
utc 2025-09-30 12:00 -> local Oct 1 01:00
utc 2025-12-31 12:00 -> local Jan 1 01:00
```

So the widget renders `Oct 1`, the test looks for `Sep 30`, and the finder is empty. The forum
pair fails identically against `find.text('12/31/2025')` (`forum_widgets_test.dart:236`), which
renders as `1/1/2026` locally.

These tests pass anywhere from roughly UTC-11 to UTC+11 and fail at UTC+12 or beyond. GitHub
runners are UTC, so CI never sees it.

### This is not the fork's doing

`mobile/` is byte-identical to the upstream merge-base — the fork has no divergence there at all:

```
$ git diff --numstat f8692fa9b52ddcfeb4b95fb4862109983509f131 launchpad/launchpad -- mobile/
$            # (no output)
```

So the failure is inherited from `block/buzz`, not introduced here, and it would reproduce on
upstream `main` on any machine east of UTC+11. It is a latent upstream test defect that only
certain developers can observe — **and this cohort is in one of the timezones that observes it.**

It is worth reporting to `block/buzz` on that basis. No issue was filed as part of this research.

### Controlled confirmation

Running only the three affected files, changing nothing but `TZ`:

```
$ TZ=Pacific/Auckland flutter test test/features/pulse/compose_note_page_test.dart \
    test/features/pulse/note_card_test.dart test/features/forum/forum_widgets_test.dart
00:12 +32 -4: Some tests failed.

$ TZ=UTC flutter test test/features/pulse/compose_note_page_test.dart \
    test/features/pulse/note_card_test.dart test/features/forum/forum_widgets_test.dart
00:10 +36: All tests passed!
```

Same commit, same machine, same Flutter, same test files — four failures at UTC+13, zero at UTC.
The timezone is the whole of the difference.

The whole suite was then run under `TZ=UTC`:

```
$ TZ=UTC flutter test          # full mobile suite
66:47 +1445: All tests passed!
```

So `mobile-test` — the one recipe that fails on this machine — passes once the timezone is UTC.
Two caveats on that run, both honest: it reports 1,445 completions against the 1,465 of the
Auckland run (flutter's `+N` counter is not a stable total, so the two numbers are not directly
comparable), and it took 66 minutes against the Auckland run's 4:19. That slowdown coincided with
the host sitting at 99% disk and other cargo builds running concurrently; it is not attributed to
the timezone change, and it is not evidence about the test suite.

## 3. `just test-unit` has two branches and took the quieter one

`test-unit` (`justfile`) begins:

```bash
if command -v cargo-nextest &>/dev/null; then
    cargo nextest run -p buzz-core -p buzz-auth --lib
    ... nine explicit package invocations ...
else
    ./scripts/run-tests.sh unit
fi
```

`cargo-nextest` is not present in this Hermit environment, so the run took the `else` branch:

```
$ command -v cargo-nextest >/dev/null && echo PRESENT || echo ABSENT
ABSENT
```

Both branches exited 0, but they are not the same test set, and nothing tells the developer which
one ran. The nextest branch also carries a comment that matters for the methodology document:

> Enumerated explicitly because nothing in CI runs `cargo test --workspace` — workspace
> membership alone buys clippy/check, not a single executed test.

So `just test-unit` is a curated list of nine packages, not the workspace. A reader who assumes
"unit tests" means "the workspace's unit tests" is wrong, and the justfile says so itself.

## What this changes for #290

**Criterion 1 (write the methodology down).** The document cannot repeat ADR-0020 ruling 7's
phrasing — "`just ci` is the contract. One command, locally identical to CI" — without
qualification. Three qualifications are now evidenced: it is unrunnable on Intel macOS; one of
its recipes is timezone-sensitive; and one recipe silently runs a different test set depending on
whether an optional tool is installed. The honest sentence is that `just ci` is the *local
approximation* of CI, and the document should say where the approximation breaks.

It also needs to state what `just ci` does **not** cover, which is more than the tests it does:
no integration tests (that is `just test`, needing Postgres and Redis), no relay E2E (`#[ignore]`,
needing a live relay), no desktop E2E, and not the web E2E suite that exists. `just ci` green and
CI green are different claims.

**Criterion 5 (make the promise mechanical).** Nothing here blocks a required check *in CI* —
the failure is local-only and CI is UTC linux. But it removes the assumption that a developer can
reproduce the gate locally before pushing. On an Intel Mac they cannot run it at all, and in
NZ they get a red `mobile-test` that CI will not reproduce. That is exactly the "gate you cannot
trust" dynamic ADR-0019 warns about, arriving from the local side rather than the CI side.

**A note on the pre-push hook.** `mobile-test`'s four failures mean any NZ-based contributor
running the repo's pre-push hooks sees mobile tests fail on every branch, for reasons unrelated
to their change. That is a live cost today, not a hypothetical.

## Confidence and what was not checked

**High confidence** in: the per-recipe verdicts above (each exit code was captured), the pnpm
root cause (the manifest states it in a comment), the timezone root cause (the epoch conversion
was computed and the formatter read), and that `mobile/` carries no fork divergence (the diff is
empty).

**Not checked:**

- **`just ci` was never invoked as a single command.** Nine leaf recipes were run individually.
  The chained recipe would have stopped at its first failure and never reached `mobile-test`;
  running them separately gives more information, but it is not literally the same invocation.
- **The five pnpm-dependent recipes were not run anywhere.** Whether `desktop-test`,
  `desktop-build`, `web-build`, `desktop-check` and `web-check` pass at this commit is
  **unestablished**. I believe they do, because CI's desktop and web jobs pass on recent runs,
  but belief is not evidence and those jobs are not identical to the recipes.
- **Whether `just ci` passes end to end on linux/amd64 in UTC** — the configuration where all
  three problems above disappear. `mobile-test` was shown to pass under `TZ=UTC` on this host,
  but the five pnpm recipes still never ran anywhere, so the end-to-end question is unsettled.
  That single measurement would settle the headline question cleanly and needs a machine this
  research did not have.
- **The host was at 99% disk (4.3 GiB free) throughout.** A cargo test in a parallel lane died
  with "No space left on device". No failure reported here was traced to disk, but the
  environment was not clean and the 66-minute mobile run is unexplained.
- **Stability across repeat runs.** Each recipe ran once. Nothing here says whether any of them
  is flaky.
- **Any other timezone.** The UTC+12/+13 failure was reproduced; the UTC-13 boundary and the
  exact passing band were reasoned from the arithmetic, not observed.
