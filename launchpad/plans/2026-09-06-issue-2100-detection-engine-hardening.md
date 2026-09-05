Issue #2100 (follow-up, no new issue filed) — harden professor.py's detection engine at the root
Stated size: no `Size` line and no dedicated GitHub issue (scoped directly from review findings) -> cap: 12 steps

(No `Size` line exists to read — same repo-template gap as the original plan — and there's no
dedicated GitHub issue either, since this is scoped directly from a third independent review
round's findings, at Serina's explicit direction to fix the underlying detection approach
rather than patch individual evasions. Sized from the two library integrations plus the
fixture/test migration they force -> more than an hour of work.)

ALREADY TRUE  (verified against the real code and a real `uv run` probe, not notes)
  Worktree `/home/serina/Launchpad/buzz/__worktrees/feature-2100-professor-tool-layer`, branch
  `feature/2100-professor-tool-layer`, HEAD `1c97473f0` (35 commits since the plan landed,
  across build + three review-driven fix rounds). `git status --short` clean except `.review/`.
  `tools/professor.py`'s PEP 723 header currently declares `dependencies = ["pyyaml"]`; `uv run
  --with detect-secrets --with markdown-it-py python3 -c "import detect_secrets, markdown_it"`
  succeeds cleanly (`detect-secrets` importable, `markdown_it` 4.2.0) — both are real,
  installable dependencies, not a hypothetical.
  `professor_lib/localcmd.py` (1115 lines) hand-rolls: `HEADING_RE`/`_fence_marker`/
  `_strip_fenced_lines`/`_split_sections` (structure detection, ~230 lines) and
  `API_KEY_PATTERNS`/`PASSWORD_LITERAL_RE`/`_high_entropy_tokens_near_keywords`/
  `PRIVATE_KEY_RE`/`CONNECTION_STRING_RE`/`WEBHOOK_URL_RE`/`_url_embedded_auth_token`/
  `EMAIL_RE`/`INTERNAL_HOST_RE`/`PHYSICAL_ADDRESS_RE` (detection, ~120 lines) as independent
  regex passes with no cross-category overlap handling.
  `screen_content()` builds each category's findings in its own `for match in
  PATTERN.finditer(content)` loop and appends directly to one flat `findings` list — confirmed
  by reading the function body (lines 950-1115) — so two different categories matching
  overlapping spans (e.g. `PASSWORD_LITERAL_RE` matching `password: X@example.com` as a whole,
  `EMAIL_RE` separately matching just `X@example.com` inside it) each get their own
  independently-computed `match`/`disposition`, with nothing correlating them.
  `_screen_finding()` (lines 921-945) already nulls `match`/`replacement` for `block` — but only
  for the finding whose OWN disposition is `block`; it has no visibility into a second,
  overlapping `redact` finding.
  `_roster_names_first_match()` (singular, line 893) returns one match, confirmed by name and by
  its one call site (`screen_content` line ~1005) — not "all matches."
  `check_page()` (line 679) and `_check_section()` (line 426) build `missing-citation`/
  `mixed-claim`/etc. messages that embed the flagged sentence's raw text via Python f-strings —
  confirmed by reading `_check_section`'s finding-construction lines.
  `_split_sections` only starts a section after a line matching `HEADING_RE` (`^#+\s+.*$`,
  ATX-only); a document using only Setext headings (`Heading\n=======`) or no headings at all
  produces zero sections, so `_check_section` never runs on any of its body text.
  `check_professor.py` is 957 lines, currently exercises 24 check-page fixtures, 14
  screen-content fixtures, plus dedicated tests for pack-root handling, the local/network
  citation split, shallow-clone safety, and frontmatter branches — all of it currently
  `ALL CHECKS PASSED` at HEAD.
  Third-round review findings this plan closes (Codex CLI, independent, 2026-09-06): 5 High
  (overlapping block+redact discloses a secret via the redact finding; check-page's own
  messages quote secrets before screening ever runs; `API_KEY=`/`access_token=` evade the
  keyword-adjacency regex because `_` is a regex word character; a JSON-quoted
  `"password": "..."` evades the password regex because a closing quote follows immediately;
  headingless/Setext documents skip every body check) and 3 Medium (roster-name dispatch only
  ever reports the first candidate; `check-page`'s `location.line` is body-relative while
  `screen-content`'s is file-relative, under the same field name; the shallow-clone-skip fix
  from the prior round is unreachable because a preceding mandatory check in
  `check_professor.py` exits before the skip logic runs).

STEP 1  Add `detect-secrets` and `markdown-it-py` to `professor.py`'s PEP        [independent]
        723 `dependencies` list (alongside the existing `pyyaml`). No behavior
        change yet — this step only makes the dependencies resolvable.
        done when: `uv run tools/professor.py --help` still exits 0 and lists
        all four subcommands, with no dependency-resolution error; `python3
        -c "import detect_secrets, markdown_it"` succeeds when run the same
        way `check_professor.py` invokes `professor.py` (via `uv run`, not a
        bare `python3` that might use a different environment).

STEP 2  Replace `_split_sections`/`HEADING_RE`/`_fence_marker`/                 [needs 1]
        `_strip_fenced_lines` with `markdown-it-py`-based parsing: parse the
        document body once with `MarkdownIt()`, walk the resulting token
        stream for `heading_open` tokens (covers ATX **and** Setext — both
        produce the same token type in CommonMark) to find section
        boundaries with real line numbers (each token's `.map` gives a
        `[start_line, end_line]` pair), and use `fence` tokens' own `.map` to
        identify fenced-code spans instead of hand-tracking fence-open/close
        state line by line. Preserve the existing public shape
        `_split_sections` returns (whatever `_check_section`'s caller
        currently expects) so downstream code doesn't need to change in this
        step — only the parsing internals change.
                                                                    ← RUNS HERE
        done when: the existing `compliant-tilde-fenced-code.md` and
        `compliant-nested-fence-length.md` fixtures (added to fix hand-rolled
        fence bugs in an earlier round) still pass with zero findings; a NEW
        fixture using only Setext headings (`Title\n=====`) with a real,
        correctly-marked section now gets its body actually checked (a
        missing citation in it is caught, proving the headingless-skip bug
        from the third review round is closed); a NEW fixture with no
        headings at all and an uncited claim also now gets checked (same
        proof, no-heading case).

STEP 3  Replace the regex-based secret detectors (`API_KEY_PATTERNS`,          [needs 1]
        `PASSWORD_LITERAL_RE`, `_high_entropy_tokens_near_keywords`,
        `PRIVATE_KEY_RE`, `CONNECTION_STRING_RE`) with `detect-secrets`'
        plugin-based scanning (`detect_secrets.core.secrets_collection` /
        `detect_secrets.settings`, initialized with a sensible default plugin
        set: high-entropy string detectors, keyword detector, private-key
        detector — check the library's actual current API via `uv run
        --with detect-secrets python3 -c "import detect_secrets; help(...)"`
        rather than assuming a remembered API shape, since detect-secrets'
        public interface has changed across versions). Map each of its
        findings back to this pack's existing category names
        (`api-key-token`, `private-key`, `connection-string`) so the output
        shape and `block` disposition are unchanged from the caller's
        perspective — this step changes what triggers a finding, not the
        finding's shape.
        done when: the existing `block-high-entropy-token.md`,
        `block-webhook-url-token-param.md` (keep `WEBHOOK_URL_RE`/
        `_url_embedded_auth_token` as-is for this step — they're a distinct
        category detect-secrets doesn't cover, not part of this step's
        scope), and PEM/connection-string fixtures still correctly fire; TWO
        new fixtures reproducing the third review round's exact findings now
        correctly fire as `block`: `API_KEY=Q7mK2vR9xN4pL8sT3wY6zB1cD5fG0hJq`
        (underscore-separated keyword) and `{"password": "review-only-example"}`
        (JSON-quoted key) — both were silent misses before this step.

STEP 4  Add a post-processing overlap-merge pass in `screen_content()`,        [needs 3]
        run once after all category detectors have produced their raw
        findings and before the final `findings` list is assembled: group
        findings whose spans overlap, and for any group containing at least
        one `block`-disposition finding, force every finding in that group to
        report `match: null` (matching `block`'s own existing suppression),
        regardless of that individual finding's own disposition. This is the
        direct fix for the third review round's highest-severity finding — a
        `redact`-disposition email finding overlapping a `block`-disposition
        connection-string finding for the same text currently still leaks
        the full secret via the redact finding's own `match` field.
        done when: `password: FakeReviewPassword@example.com` (the exact
        reproduction from the third review round) now produces a `block`
        finding with `match: null` AND the overlapping `email-address`
        finding also reports `match: null` — no finding in the output
        contains the credential text anywhere; a fixture with two genuinely
        non-overlapping findings (e.g. an email in one sentence, an
        unrelated internal hostname in another) still reports both with
        their normal per-disposition `match` behavior, proving the merge
        only suppresses genuinely overlapping spans, not everything.

STEP 5  Generalize check-page's "never quote flagged content" rule (already   [needs 2]
        applied to screen-content's block findings in an earlier round) to
        every message `_check_section`/`check_page` construct: stop
        embedding the flagged sentence's raw text in `missing-citation`,
        `mixed-claim`, and any other message that currently quotes it
        directly. Report rule name + location only, matching the principle
        already applied on the screen-content side.
        done when: running check-page against a fixture whose uncited
        behaviour claim contains a fabricated secret-shaped string no longer
        includes that string anywhere in check-page's own JSON output
        (reproducing the third review round's finding that `draft-page` runs
        check-page before screen-content, so check-page's own messages were
        an unscreened disclosure path); existing fixtures' finding `rule`
        values are unchanged (only `message` text changes), so no fixture's
        expected verdict needs updating — only the specific assertions (if
        any) that check `message` for the quoted sentence.

STEP 6  Fix `_roster_names_first_match` to return every candidate, not just    [needs 2]
        the first — rename to `_roster_names_all_matches` (or similar) and
        have `screen_content` emit one `roster-names` finding per candidate
        found, each with its own location, matching `skills/screen-sensitive/
        SKILL.md`'s documented "once per name screen-content flags" dispatch
        contract (which cannot work if only one name ever surfaces).
        done when: a fixture with two separate roster-shaped name pairs in
        different sentences (reproducing the third review round's exact
        input) now produces two distinct `roster-names` findings, each with
        its own correct line location — not one.

STEP 7  Unify the `location.line` coordinate system: make check-page's        [needs 2, 5]
        line numbers file-relative (matching screen-content's convention and
        matching what a human opening the file in an editor would expect) —
        add back the frontmatter's line count, which markdown-it-py's line
        numbers (from step 2) should make straightforward since the parser
        operates on the whole file if fed the whole file rather than the
        post-frontmatter body.
        done when: running check-page against the existing
        `broken-missing-citation.md` fixture reports a `location.line` that
        matches the actual file line of the offending sentence (verified by
        `grep -n` against the fixture file itself), not a body-relative
        offset that undercounts by the frontmatter's line count.

STEP 8  Fix `check_professor.py`'s shallow-clone-skip control flow: the       [independent]
        third review round found that `check_fixture_commit_shallow_clone_safety()`
        (a check that runs earlier in `main()`) exits the whole harness with
        a failure when the fixture-pinned commit is absent, before
        `check_check_page_fixtures()`'s own skip logic ever gets a chance to
        run — so a genuinely shallow clone still fails the harness instead
        of skipping cleanly, defeating the fix an earlier round believed it
        had made. Fix the control flow so the shallow-clone case reaches an
        actual skip, not a hard failure, at whichever point in `main()`'s
        sequence first detects it.
        done when: reproduce the third review round's exact repro (a
        temporary repo/checkout without the pinned commit) and confirm
        `check_professor.py` reports a clean, named skip — not a failure —
        for the affected checks, while a normal (non-shallow) run still
        passes everything unchanged.

STEP 9  Full fixture and assertion sweep: run `check_professor.py` after       [needs 3, 4, 5, 6, 7, 8]
        steps 1-8 land together, and fix any existing fixture whose expected
        verdict changed because `detect-secrets`/`markdown-it-py` parse or
        detect something differently than the hand-rolled code did (a real
        possibility — these are different engines, not drop-in behavioral
        clones). Do not weaken an existing fixture's assertion to make it
        pass; if a fixture's expected result is genuinely different under
        the new engine, say so explicitly and confirm the new result is
        still correct against the actual spec (`page-contract.md`/
        `sensitive-patterns.md`), not just "different."
        done when: `python3 tools/check_professor.py` exits 0 and prints
        `ALL CHECKS PASSED` with every fixture from steps 1-8 included, and
        every pre-existing fixture from prior rounds still passing (or, for
        any whose expected result genuinely changed, an explicit note in the
        commit message naming which fixture, what changed, and why the new
        result is correct).

PARALLEL  Steps 1 and 8 are independent of everything else (1 only touches
          the dependency declaration; 8 only touches check_professor.py's
          control flow, not the detection code) and could run as parallel
          subagents. Steps 3, 5, 6 all depend on step 2's parsing rewrite
          landing first (they either consume its section/location data or
          touch adjacent code in the same functions) but are themselves
          mutually independent of each other's *logic* — however, per
          build-change's own rule, do not actually dispatch them in parallel
          within one working tree; sequential-with-review is the safer
          default even where independence would allow more. Step 4 needs
          step 3's detectors in place first (there's nothing to merge
          overlaps for until the new detectors exist). Step 7 needs step 5's
          message changes first (touches the same message-construction code
          paths). Step 9 is last, needs everything.
GATES     `review-code` and `review-tests` both apply, same as the original
          plan's own GATES line. Given this is the fourth round to touch the
          detection surface specifically and three independent whole-branch
          reviews have each found real issues here, run BOTH `review-code`
          and an independent Codex pass again after this lands, before
          calling it done — the pattern so far has consistently found real
          issues on repeat passes. `qa` explore mode applies, same as
          before, and has still never actually been run on this branch —
          worth doing once after this step, not deferred again.
BUDGET    Step 3 (swapping the actual detection engine) is the step most
          likely to eat the budget — it needs the library's real current API
          (not a remembered one), careful category-name mapping so the
          output shape stays stable for callers, and step 9's fixture sweep
          will surface whatever step 3 gets subtly wrong.
OPEN      Whether `detect-secrets`' own default plugin set's false-positive
          rate is acceptable for this pack's real-world use (sensitive-
          patterns.md itself warns a high false-positive rate "would train
          reviewers to ignore the gate's output") is not something this plan
          can fully answer from fixtures alone — that needs real-world usage
          data this branch doesn't have yet, so it's left as a known
          open question for whoever operates this pack for real, not decided
          here. Whether webhook/URL-embedded-token detection
          (`WEBHOOK_URL_RE`/`_url_embedded_auth_token`) should also move to
          detect-secrets or a dedicated URL-secret library is left open —
          step 3 deliberately keeps that category as-is, since detect-secrets
          doesn't natively cover it and no evasion was found there in three
          review rounds.
LEFT OUT  The `[dispatch]` roster-names category's actual semantic
          classification ($PROFESSOR_VERIFIER_CMD, Phase 1b) — step 6 only
          fixes enumeration (finding every candidate), not classification,
          which stays deferred exactly as before. Reconciling the remaining
          known-stale `SKILL.md` drafts beyond `screen-sensitive`'s already-
          patched subsection — unchanged from the original plan's own scope
          boundary. `#1402`'s branch/PR — untouched, as always.
