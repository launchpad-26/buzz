Issue #2100 (follow-up, no new issue filed) — harden professor.py's detection engine at the root
Stated size: no `Size` line and no dedicated GitHub issue (scoped directly from review findings) -> cap: 12 steps

(No `Size` line exists to read — same repo-template gap as the original plan — and there's no
dedicated GitHub issue either, since this is scoped directly from a third independent review
round's findings, at Serina's explicit direction to fix the underlying detection approach
rather than patch individual evasions. Revised once already: an independent `review-plan` pass
found that this plan's first draft (swap to `detect-secrets`) would have been a net regression —
`detect-secrets`' default configuration misses this pack's actual content shapes (unquoted
`key: value`/`key=value`, markdown-prose-embedded examples) — so this revision hardens the
existing hand-rolled detectors directly instead, per Serina's explicit choice between the two
options presented. Sized from the markdown-parser swap plus the fixture/test migration it
forces -> more than an hour of work.)

ALREADY TRUE  (verified against the real code and real command output, not notes)
  Worktree `/home/serina/Launchpad/buzz/__worktrees/feature-2100-professor-tool-layer`, branch
  `feature/2100-professor-tool-layer`. `git status --short` clean except `.review/` (untracked
  review-package output, not build residue). No PR is currently open for this branch — #2103
  was closed (not merged) pending this hardening work; nothing here is being discarded.
  `tools/professor.py`'s PEP 723 header currently declares `dependencies = ["pyyaml"]`.
  `markdown-it-py` installs cleanly via `uv run --with markdown-it-py python3 -c "import
  markdown_it"` (version 4.2.0) — a real, installable dependency.
  **A real bug found during this plan's own `review-plan` pass, not by the third review round**:
  `tools/professor.py` is not executable (`ls -la` shows `-rw-r--r--`), and
  `check_professor.py`'s `_run_professor()` (line ~212) invokes it as `["python3",
  str(PROFESSOR_PY), *args]` — a bare `python3`, not the shebang-based direct execution
  (`<pack-root>/tools/professor.py <subcommand> ...`) that `skills/draft-page/SKILL.md` and
  `skills/update-page/SKILL.md` both document as the actual calling convention (confirmed:
  `grep -n "tools/professor.py" skills/draft-page/SKILL.md` shows direct-executable invocation
  throughout, never `python3 tools/professor.py`). This means the harness has never actually
  exercised the tool via its own documented interface, and any dependency declared only in the
  PEP 723 header (not already ambiently installed, like `pyyaml` happens to be) would silently
  never be available to the harness — confirmed directly: `python3 -c "import markdown_it"`
  (the harness's real invocation path) fails with `ModuleNotFoundError`, while `chmod +x
  tools/professor.py && PROFESSOR_PACK_ROOT=... ./tools/professor.py resolve-pin block/buzz
  main` (the real, documented path) succeeds and correctly resolves `uv`'s PEP 723 dependencies.
  `professor_lib/localcmd.py` (1115 lines) hand-rolls: `HEADING_RE`/`_fence_marker`/
  `_strip_fenced_lines`/`_split_sections` (structure detection, ~230 lines) and
  `API_KEY_PATTERNS`/`PASSWORD_LITERAL_RE`/`_high_entropy_tokens_near_keywords`/
  `PRIVATE_KEY_RE`/`CONNECTION_STRING_RE`/`WEBHOOK_URL_RE`/`_url_embedded_auth_token`/
  `EMAIL_RE`/`INTERNAL_HOST_RE`/`PHYSICAL_ADDRESS_RE` (detection, ~120 lines) as independent
  regex passes with no cross-category overlap handling.
  Verified directly, the two demonstrated evasions are real bugs in the existing regex text,
  not something a library swap is needed to fix: `_high_entropy_tokens_near_keywords`'s
  keyword-adjacency check uses `\b` around `key`/`token`/`secret`/`password`, and `\b` treats
  `_` as a word character, so `API_KEY=<random>` and `access_token=<random>` never match at all
  (confirmed: `API_KEY=Q7mK2vR9xN4pL8sT3wY6zB1cD5fG0hJq` through the current `screen-content`
  returns `{"findings": []}`). `PASSWORD_LITERAL_RE` (`\b(?:password|passwd|pwd)\s*[:=]\s*\S+`)
  requires the separator to follow the keyword immediately (modulo whitespace); a JSON-quoted
  key (`"password": "value"`) has a closing `"` between the keyword and the colon that the
  regex doesn't tolerate, so it never matches (confirmed: `{"password":
  "review-only-example"}` returns `{"findings": []}`).
  Also verified directly (still true, unrelated to which detector implementation is used):
  `password: FakeReviewPassword@example.com` — no quoting, the plain literal-password shape
  `PASSWORD_LITERAL_RE` already matches today — produces BOTH a `block`-disposition
  `connection-string` finding (already correctly `match: null`) AND a separately-computed
  `redact`-disposition `email-address` finding whose `match` field contains the full string
  `FakeReviewPassword@example.com` — the overlap-disclosure bug is real and reproducible against
  the EXISTING detectors, independent of any hardening this plan makes to them.
  `screen_content()` builds each category's findings in its own `for match in
  PATTERN.finditer(content)` loop and appends directly to one flat `findings` list — confirmed
  by reading the function body — so two different categories matching overlapping spans get
  independently-computed `match`/`disposition` with nothing correlating them.
  `_roster_names_first_match()` (singular) returns one match, confirmed by name and by its one
  call site — not "all matches."
  `check_page()` and `_check_section()` build `missing-citation`/`mixed-claim`/etc. messages
  that embed the flagged sentence's raw text via Python f-strings — confirmed by reading
  `_check_section`'s finding-construction lines.
  `_split_sections` only starts a section after a line matching `HEADING_RE` (`^#+\s+.*$`,
  ATX-only); a document using only Setext headings (`Heading\n=======`) or no headings at all
  produces zero sections, so `_check_section` never runs on any of its body text (confirmed
  live: both shapes return `{"findings": [], "skipped": false}` even with an uncited claim
  present).
  `check-page`'s `location.line` is body-relative (counts from after the frontmatter);
  `screen-content`'s is file-relative (it reads and numbers the whole raw file, frontmatter
  included) — confirmed live, same field name, two different coordinate systems.
  `check_fixture_commit_shallow_clone_safety()` runs in `check_professor.py`'s `main()`
  immediately before `check_check_page_fixtures()`, and returns a hard failure (not a skip) when
  the fixture-pinned commit is absent from local history — confirmed by reading `main()`'s
  sequence — so the shallow-clone-skip logic an earlier round believed it had added is
  unreachable in practice.
  `check_professor.py` is 957 lines, currently exercises 24 check-page fixtures, 14
  screen-content fixtures, plus dedicated tests for pack-root handling, the local/network
  citation split, shallow-clone safety, and frontmatter branches — all `ALL CHECKS PASSED` at
  HEAD before this plan's steps begin.

STEP 1  Fix the tool's actual invocation, found during this plan's own          [independent]
        pre-build review (not by any prior review round): `chmod +x
        tools/professor.py` (it must be directly executable for its own
        `uv run --script` shebang and every documented `SKILL.md` invocation
        to work at all), and change `check_professor.py`'s `_run_professor()`
        from `["python3", str(PROFESSOR_PY), *args]` to direct execution
        (`[str(PROFESSOR_PY), *args]`) — the harness must exercise the tool
        the same way its own documentation says to invoke it, not a
        `python3`-prefixed workaround that happens to bypass the PEP 723
        dependency mechanism entirely. Add `markdown-it-py` to
        `professor.py`'s PEP 723 `dependencies` list (no `detect-secrets` —
        that direction was rejected after this plan's own review found it
        wouldn't work for this pack's content).
                                                                    ← RUNS HERE
        done when: `git diff --stat` shows `professor.py`'s mode bit changed
        to executable; `PROFESSOR_PACK_ROOT=<pack-root>
        ./tools/professor.py resolve-pin block/buzz main` (direct execution,
        no `python3` prefix) succeeds and prints the JSON schema; running
        `python3 tools/check_professor.py` (the harness's own top-level
        invocation, unchanged) still reports `ALL CHECKS PASSED` — proving
        the harness now genuinely exercises the real invocation path and
        nothing regressed by fixing it.

STEP 2  Replace `_split_sections`/`HEADING_RE`/`_fence_marker`/                 [needs 1]
        `_strip_fenced_lines` with `markdown-it-py`-based parsing, with
        frontmatter handled correctly from the start (this is where the
        first draft of this plan had a real bug, found by `review-plan`):
        extract the frontmatter block with the existing `FRONTMATTER_RE`
        first, feed ONLY the remaining body to `MarkdownIt().parse()` (never
        the whole raw file — feeding the whole file lets `markdown-it-py`
        misparse the frontmatter's closing `---` as a Setext heading
        underline, turning the entire YAML block into a phantom section),
        then add the frontmatter's own line count back to every line number
        `markdown-it-py` reports, so `_split_sections` returns file-relative
        line numbers directly — closing the location-coordinate mismatch
        against `screen-content` (which is already file-relative) in the
        same step, rather than as separate follow-up work. Walk the token
        stream for `heading_open` tokens (covers ATX and Setext — both
        produce the same token type) for section boundaries, and `fence`
        tokens' own `.map` for fenced-code spans, replacing the hand-tracked
        fence-open/close state.
        done when: the existing `compliant-tilde-fenced-code.md` and
        `compliant-nested-fence-length.md` fixtures still pass with zero
        findings; a NEW fixture using only Setext headings, and a NEW
        fixture with no headings at all, each with a real uncited claim, now
        both get that claim caught (proving the headingless-skip bug is
        closed); running check-page against the existing
        `broken-missing-citation.md` fixture reports a `location.line` that
        matches the actual file line of the offending sentence (verified by
        `grep -n` against the fixture file), not a body-relative
        undercounted value; EVERY compliant fixture with real frontmatter
        (there are several) still produces zero findings — proving the
        frontmatter-as-phantom-heading bug the first plan draft would have
        introduced does not exist in this version.

STEP 3  Harden the two demonstrated regex evasions directly, no library        [needs 1]
        swap: (a) fix the keyword-adjacency check in
        `_high_entropy_tokens_near_keywords` (and any other place using the
        same `\bkey\b`-style boundary) so `_` counts as a valid separator
        between a keyword (`key`/`token`/`secret`/`password`) and the rest of
        an identifier — e.g. require a non-alphanumeric-and-non-underscore
        boundary only where the keyword is NOT already underscore-adjacent,
        so `API_KEY`, `access_token`, `secret_key` all match while ordinary
        words like `keyword`/`tokenizer` still do not; (b) fix
        `PASSWORD_LITERAL_RE` to tolerate an optional quote character
        between the keyword and its separator, and an optional leading quote
        before the value, so a JSON-shaped `"password": "value"` matches.
        Leave `PRIVATE_KEY_RE`, `CONNECTION_STRING_RE`, `WEBHOOK_URL_RE`,
        `EMAIL_RE`, `INTERNAL_HOST_RE`, `PHYSICAL_ADDRESS_RE` untouched — no
        evasion was found in any of them across three review rounds, so this
        step doesn't touch them.
        done when: `API_KEY=Q7mK2vR9xN4pL8sT3wY6zB1cD5fG0hJq` now produces a
        `block` finding (previously a silent miss); `{"password":
        "review-only-example"}` now produces a `block` finding (previously a
        silent miss); the existing `block-high-entropy-token.md` and any
        existing password/connection-string fixtures still correctly fire;
        run the existing `clean.md` fixture (and any other fixture that
        legitimately contains the substrings "key"/"token"/"password" in
        ordinary non-secret prose) and confirm no NEW false positive was
        introduced by loosening the boundary — say explicitly what was
        checked for this, since a boundary loosened to catch snake_case
        names is exactly the kind of change that can also start matching
        unrelated words it shouldn't.

STEP 4  Stop `screen-content` from ever printing the flagged text, for any     [needs 1]
        disposition — not just `block`, and not just where a span happens to
        overlap another finding. A second, independent `review-plan` pass
        (2026-09-06) found that the block-only suppression an earlier round
        added leaves the ordinary, non-overlapping case wide open: any
        standalone `redact` finding (`email-address`,
        `internal-hostname-private-ip`, `physical-address` — the majority of
        real `redact` findings, not a rare edge case) still prints the exact
        matched text in `_screen_finding`'s `match` field, which is exactly
        the disclosure channel `skills/screen-sensitive/SKILL.md` forbids
        ("never the redacted value itself"). The first draft of this fix
        (a post-processing pass that merges overlapping spans and only
        suppresses `match` for a group containing a `block` finding) was
        over-engineered for what's actually needed — simpler and more
        complete: `_screen_finding` always sets `match: null`, unconditionally,
        for every disposition. The calling skill (`draft-page`/`update-page`)
        already has the full draft file in its own context (it wrote it) — it
        does not need this tool to hand back the secret text at all, only
        WHERE (`location.line`, already present) and WHAT KIND (`category`,
        already present) to redact, so it can read that line itself and
        perform the replacement using tools it already has. `replacement`
        (the literal `"[REDACTED: <category>]"` string to substitute in)
        stays exactly as it is now — it never carried the secret, only the
        placeholder text.
        done when: running `screen-content` against the existing
        `redact-email.md` fixture (an ordinary, non-overlapping case) now
        reports `match: null` — previously this printed the literal email
        address; running it against `password: FakeReviewPassword@example.com`
        (the overlapping-block+redact case from the third review round)
        also reports `match: null` on both findings, closed by the same
        one-line change rather than a separate merge pass; grep the tool's
        full output across every existing screen-content fixture and confirm
        `match` is `null` in every single result, with no exceptions. Update
        `skills/screen-sensitive/SKILL.md`'s "Act on the result" section if
        it currently describes reading `match` to perform a redaction — it
        should describe using `location`+`category` to find and redact the
        span in the draft file directly.

STEP 5  Generalize check-page's "never quote flagged content" rule (already   [needs 2]
        applied to screen-content's block findings in an earlier round) to
        every message `_check_section`/`check_page` construct: stop
        embedding the flagged sentence's raw text in `missing-citation`,
        `mixed-claim`, and any other message that currently quotes it
        directly. Report rule name + location only.
        done when: running check-page against a fixture whose uncited
        behaviour claim contains a fabricated secret-shaped string no longer
        includes that string anywhere in check-page's own JSON output
        (`draft-page` runs check-page before screen-content, so check-page's
        own messages were an unscreened disclosure path); existing fixtures'
        `rule` values are unchanged (only `message` text changes), so update
        only the specific assertions (if any) that check `message` for the
        quoted sentence.

STEP 6  Fix `_roster_names_first_match` to return every candidate, not just    [needs 2]
        the first — rename appropriately and have `screen_content` emit one
        `roster-names` finding per candidate found, each with its own
        location, matching `skills/screen-sensitive/SKILL.md`'s documented
        "once per name screen-content flags" dispatch contract (which cannot
        work if only one name ever surfaces).
        done when: a fixture with two separate roster-shaped name pairs in
        different sentences now produces two distinct `roster-names`
        findings, each with its own correct line location — not one.

STEP 7  Fix `check_professor.py`'s shallow-clone-skip control flow: a         [independent]
        preceding mandatory check exits the whole harness with a failure
        when the fixture-pinned commit is absent, before the fixture
        runner's own skip logic ever gets a chance to run — so a genuinely
        shallow clone still fails the harness instead of skipping cleanly.
        Fix the control flow so the shallow-clone case reaches an actual
        skip, not a hard failure, at whichever point in `main()`'s sequence
        first detects it.
        done when: reproduce the failure with a temporary repo/checkout
        without the pinned commit and confirm `check_professor.py` reports a
        clean, named skip — not a failure — for the affected checks, while a
        normal (non-shallow) run still passes everything unchanged.

STEP 8  Full fixture and assertion sweep: run `check_professor.py` after       [needs 3, 4, 5, 6, 7]
        steps 1-7 land together, and fix any existing fixture whose expected
        result changed because `markdown-it-py`'s real line numbers differ
        from the old hand-rolled body-relative numbers (a real, expected
        consequence of step 2 unifying the coordinate system — any fixture
        or assertion pinned to a specific body-relative line number needs
        updating to the new file-relative value; this is not a regression,
        it's the fix). Do not weaken an assertion to make it pass silently —
        if a fixture's expected value changed, say so explicitly in the
        commit message and confirm the new value is actually correct
        (verified against the real file, e.g. `grep -n`), not just
        "different."
        done when: `python3 tools/check_professor.py` exits 0 and prints
        `ALL CHECKS PASSED` with every fixture from steps 1-7 included, and
        every pre-existing fixture from prior rounds still passing (updated
        where step 2's coordinate change genuinely requires it, each such
        update named explicitly).

PARALLEL  Step 1 and step 7 are independent of everything else (1 fixes the
          invocation path and adds the one new dependency; 7 only touches
          check_professor.py's control flow, not the detection code) — but
          per build-change's own rule, do not actually dispatch them in
          parallel within one working tree; build sequentially regardless.
          Steps 5 and 6 need step 2's parsing rewrite landed first (they
          consume its data or touch adjacent code in the same functions).
          **Step 3 needs only step 1, not step 2** — a second `review-plan`
          pass (2026-09-06) caught an earlier draft of this note wrongly
          grouping step 3 with 5/6: `screen_content()` (what step 3 edits)
          never calls `_split_sections()` (what step 2 rewrites; that
          function is called only from `check_page()`), so step 3 has no
          real dependency on step 2 landing first. Step 4 also needs only
          step 1, for the same reason (it edits `_screen_finding`, in
          `screen_content()`'s code path, not `check_page()`'s). Step 8 is
          last, needs everything.
GATES     `review-code` and `review-tests` both apply, same as the original
          plan's own GATES line. This is the fourth round to touch the
          detection surface specifically, and three independent whole-branch
          reviews plus this plan's own `review-plan` pass have each found
          real issues here — run BOTH `review-code` and an independent Codex
          pass again after this lands, before considering this ready for a
          new PR. `qa` explore mode applies, and has still never actually
          been run on this branch — worth doing once after this step.
BUDGET    Step 2 (the markdown-it-py rewrite, including the corrected
          frontmatter handling) is the step most likely to eat the budget —
          it changes the coordinate system every downstream step depends on,
          and step 8's fixture sweep will surface whatever it gets subtly
          wrong, same as the risk profile the withdrawn detect-secrets swap
          carried.
OPEN      Whether the loosened keyword-boundary regex from step 3 could
          introduce new false positives on real-world prose beyond what this
          plan's fixture set can prove — step 3's own done-when asks the
          builder to check this explicitly, but a fixture set is not the
          same as real-world usage data; left as a known risk for whoever
          operates this pack for real, not fully closed here. Whether
          webhook/URL-embedded-token detection needs similar hardening is
          left open — no evasion was found there in three review rounds, so
          it's out of this plan's scope, not confirmed safe.
LEFT OUT  The `[dispatch]` roster-names category's actual semantic
          classification ($PROFESSOR_VERIFIER_CMD, Phase 1b) — step 6 only
          fixes enumeration (finding every candidate), not classification,
          which stays deferred exactly as before. Reconciling the remaining
          known-stale `SKILL.md` drafts beyond `screen-sensitive`'s already-
          patched subsection — unchanged from the original plan's own scope
          boundary. `#1402`'s branch/PR — untouched, as always. Adopting
          `detect-secrets` or any other external secret-scanning library —
          explicitly rejected this round, not merely deferred.
