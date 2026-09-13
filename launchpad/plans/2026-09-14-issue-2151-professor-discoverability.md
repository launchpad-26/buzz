Issue #2151 — feature: the Professor suite is discoverable where sessions look for it

Covers both children in one plan, shipping as **one PR naming Feature #2151**:

- **#1397** — register all seven Professor skills at the repo root by relative symlink
- **#2152** — plugin manifest and persona frontmatter describe what shipped, not what was
  proposed

Stated size: none on any of the three issues  ->  cap: 5 steps

No `Size` line exists on #2151, #1397 or #2152 — verified with `gh issue view`, not assumed. The
cap is 5 because the work is 28 symlinks and two prose edits.

Worktree: `/home/serina/Launchpad/buzz/__worktrees/feature-2151-professor-discoverability`
Branch: `feature/2151-professor-discoverability`, fast-forwarded to `origin/launchpad` at
`772df7187` on 2026-09-14 (it had drifted 15 commits behind its original base `3fdafab0c`, with
no overlap on any file this plan touches; fast-forwarding was free because the branch carried no
commits of its own yet). Re-check before building — a sibling PR merging moves this again.

WHY THIS PLAN IS SHORT — read before adding a check to it

This plan was rewritten on 2026-09-14 after three adversarial review rounds on a longer
version, which produced 13, then 15, then 9 findings. It did not converge, and the reason was
consistent: **almost every finding was a defect in the plan's own verification scaffolding, not
in the work.** Serina's call was to strip it back rather than patch a fourth time.

The specific failure that generated the most damage is worth naming, because the temptation to
reintroduce it is real. Three successive versions of this plan tried to make a script decide
whether the new prose was *truthful* about build state:

  1. Ban the substring `not yet built` — which forbids the exact wording #2152 requires, since
     Phases 2-7 genuinely are not built.
  2. A built/unbuilt "shape" check — but `\b(built|shipped)\b` matches the word *built* inside
     *not yet built*, so a blanket unbuilt claim passed; `re.match` was anchored and
     case-sensitive, so moving the verbatim stale text to the end passed too.
  3. Require the text to enumerate Phase 1 and the later phases separately — but
     `"Phase 1 and Phase 1b and Phases 2-7 are not yet built"` enumerates all of them and is
     still a blanket claim, while `(?!\s*b)` rejected the accurate `"Phase 1 built and
     hardened"` because *built* starts with a b.

**Whether prose is accurate is not mechanically decidable, and every attempt to pretend
otherwise produced a check that rejected correct wording while admitting wrong wording.** So
the division of labour below is deliberate and is the fix:

- **The script asserts only what is decidable** — structure, modes, targets, JSON/YAML
  validity, and the absence of the *exact literal* strings being replaced.
- **`review-docs` and human review judge whether the new wording is true.** That is what those
  gates are for, and STEP 3 gives the reviewer an explicit checklist so the judgement is not
  left vague.

SHELL CONVENTIONS — all three measured in this environment, not assumed

  1. **Every `<!-- COPY -->` block runs inside `( ... )`.** A bare `exit 1` on a failure path
     would otherwise close the shell of whoever pasted the block.
  2. **Skill lists are written out literally, never held in a variable.** This environment's
     shell is zsh, which does **not** word-split an unquoted `$SKILLS`. Measured: the literal
     list iterates 7 times, the variable iterates **once**. A ```bash fence does not change the
     executing shell.
  3. **Every command whose failure must stop the block carries an explicit `|| exit 1`. Do not
     rely on `set -e`.** Measured here: inside `( set -eu; … )` a failing `python3` fell
     straight through to the next command and the block exited **0**; the same construct under
     `zsh -c` exits 1. Context-dependent, so not safe to depend on. `|| exit 1` was verified to
     stop the block and propagate 1.
     This applies to `git add` and to `git status` too — a `git add` that fails without a guard
     lets the following commit record whatever else was staged, and `[ -z "$(git status
     --porcelain)" ]` reads a *failed* `git status` as a clean tree.

ALREADY TRUE  (verified against git in this worktree, not against the issue text)

Several of these decay when a sibling PR merges. Commands are given so a builder can re-run
them rather than trust this list.

  1. The gap is real. No Professor skill is registered at root today —
     `git ls-tree -r origin/launchpad --name-only -- .claude/skills .agents/skills .codex/skills .goose/skills`
     grepped for the seven names returns nothing.
  2. All four root skill dirs exist and are tracked, each already carrying
     `skills/desktop-screenshot/SKILL.md` and `skills/sprout-cli/SKILL.md` at mode `120000`.
     `.claude/skills/` additionally holds seven cohort skills as real files — out of scope, but
     evidence that this fork already uses that directory for discovery.
  3. Depth arithmetic. The precedent blob is
     `../../../desktop/src-tauri/src/managed_agents/screenshot_skill.md`
     (`git cat-file -p origin/launchpad:.claude/skills/desktop-screenshot/SKILL.md`). A relative
     link resolves against its containing directory, so `../../../` walks
     `desktop-screenshot` -> `skills` -> `.claude` and lands on the repo root. Every root skill
     dir is one level deep and every skill dir one below `skills/`, so the target string is
     `../../../launchpad/agents/the-professor/skills/<skill>/SKILL.md` for all four.
     A prior review independently built all 28 links in a throwaway clone and resolved every one.
  4. All seven canonical `SKILL.md` files exist under
     `launchpad/agents/the-professor/skills/<skill>/`, each with a `name:` frontmatter field
     matching its directory name. Per `crates/buzz-persona/PERSONA_PACK_SPEC.md` §6 the load key
     is that `name:` field, not the directory name.
  5. ADR-0030 is Accepted and generic: it permits all four dirs, requires "a symlink, never a
     copy", and states "No future cohort skill under `launchpad/agents/` needs its own ADR."
     **No new ADR is needed.** `launchpad/AGENTS.md` §3 (around lines 97-108) already carries
     the exception in writing, naming all four dirs.
  6. Both stale claims are still present, and these are their **exact** current strings — the
     literals STEP 3 asserts are gone:
     - `plugin.json` `description` begins:
       `PROPOSED (see launchpad/Research/the-professor-skill-suite-redesign.md — not yet built):`
       (note the em dash)
     - the persona frontmatter's first comment line is:
       `# PROPOSED — not yet built. See launchpad/Research/the-professor-skill-suite-redesign.md.`
     - and it also carries:
       `# The seven skills below, and the tool layer they call, do not exist as working code yet`
     STEP 3 bans these as **full sentences**, never as fragments. The fragment
     `do not exist as working code yet` would reject accurate replacement prose such as
     "The later phases do not exist as working code yet" — the same false-positive that broke
     all three earlier versions of this check.
  7. `plugin.json`'s keys are exactly `$schema, description, id, name, personas, version`, with
     `version` = `0.1.0`. **No `skills` array** — the do-not-change assertion.
  8. The persona's `skills:` list names all seven as `"./skills/<name>/"`. Resolution is against
     the **pack root**, not the persona file: `crates/buzz-persona/src/validate.rs` (≈363-369)
     strips the trailing slash, takes `file_name()`, and builds
     `pack_dir.join("skills").join(skill_name)`; the real loader `pack.rs::resolve_skills`
     (≈249-311) normalises the same way. So `./skills/scan-repo/` resolves to
     `launchpad/agents/the-professor/skills/scan-repo/`, which exists.
  9. The tool layer exists — `tools/professor.py` with `resolve-pin`, `path-exists-at`,
     `check-page`, `screen-content`, plus `professor_lib/` and `tools/check_professor.py`.
 10. The pack `README.md` does **not** carry the blanket stale claim. Its heading reads
     "Phase 0 and Phase 1 resolved, Phases 1b-7 not yet built" and its body "Phase 1 (the tool
     layer) is now built (issue #2100)". STEP 3 re-checks at branch tip rather than trusting
     this line.
 11. Phase status, for the rewrite wording. Phase 0 decided. Phase 1 shipped in PR #2106
     (merged 2026-09-08 as `29ca9b189`); its hardening in PR #2133 (merged 2026-09-09), Feature
     #2132 closed 2026-09-14. Phase 1b is Feature #2131, **open and unstarted**. Phases 2-7
     unbuilt, no Features filed.
 12. CI fires on these paths. `.github/workflows/launchpad-agents-tests.yml` triggers on
     `launchpad/agents/**`, so STEP 3's edits run its `tests` and `professor-tools` jobs.
     Neither asserts the description text.
 13. Pre-push cost is low. The always-on lanes are `branch-skew`, `push-head-scope` and
     `file-size-check`; every other lane is glob-scoped to `crates/**`, `desktop/**`, `web/**`,
     `mobile/**`. `just file-size-check` governs only `desktop/`, `web/`, `mobile/`, so neither
     the symlinks nor the `launchpad/` edits are in its roots.
     **But it cannot be run bare in this checkout.** Its core resolves
     `git merge-base origin/main HEAD`, and this is a shallow clone of a fork whose base is
     `launchpad`, so that fails with a stack trace and exit 1 regardless of the change under
     test. The pre-push hook avoids this only because `bin/.lefthookrc` — sourced by the
     generated `.git/hooks/*`, not by an ordinary shell — computes and exports
     `CHECK_FILE_SIZES_BASE`. STEP 4 sets it explicitly for the same reason. Measured
     2026-09-14: bare run exits 1; with the base set, exits 0.
 14. **`launchpad/AGENTS.md` line 404** — the cohort file, not the root one — requires
     *"Keep one commit per child Task."* Say which file: root `AGENTS.md` line 404 is unrelated
     Playwright documentation, and a builder checking there finds nothing and may conclude the
     rule is invented. That is why STEP 1 makes one commit for #1397 and STEP 3 one for #2152;
     an earlier draft split #2152 across two or three and broke the rule. STEP 1's separate
     plan-document commit is not a child-Task deliverable and does not count against it.

     **As shipped, the branch has two commits per child Task, not one.** Review findings were
     fixed after each task's original commit, and `git-safety.sh` blocks `--amend` for agents
     with no override, so the fixes landed as new commits rather than folded in. `review-final`
     judged this the better outcome and recommended against squashing, quoting the rule's own
     stated purpose in `launchpad/AGENTS.md`: those commits are what a reviewer walks and what
     `git bisect` gets, and squashing would discard the commit message explaining *why* the
     design-doc citation was wrong. Recorded here so the plan does not assert a commit shape the
     branch does not have.
 15. No name collisions with existing root skills, and symlinks materialise on this filesystem
     (`ls -la .claude/skills/desktop-screenshot/` shows `lrwxrwxrwx`, so WSL is not checking
     links out as plain files).

STEP 1  Create the 28 relative symlinks, in one commit                       [independent]

        7 skills x 4 root dirs (`.agents/`, `.claude/`, `.codex/`, `.goose/`). Every entry is
        `<dir>/skills/<skill>/SKILL.md` pointing at
        `../../../launchpad/agents/the-professor/skills/<skill>/SKILL.md` (ALREADY TRUE item 3).

        **Commit this plan document first, as its own commit.** It is untracked, and until it is
        committed STEP 4's clean-tree check fails deterministically with a message reading
        "STEP 3 was not committed" — the wrong diagnosis entirely. It cannot ride along in either
        other commit: STEP 1's check (d) forbids `launchpad/` paths in the symlink commit, and
        STEP 3's `git add` names only the two metadata files. `launchpad/plans/` is not ignored
        and 439 plan files are already tracked on `origin/launchpad`, so committing it is the
        house pattern — this plan simply has to say so. It is not a child-Task deliverable, so it
        does not disturb the one-commit-per-child-Task rule.

        None of the 28 parent directories exist and `ln -s` will not create them, so `mkdir -p`
        first. Create with `ln -s`, never by writing a file — PR #1398 was closed unmerged for
        copying, and check (a) below is what stops this PR repeating it.

        **One commit for the symlinks** (ALREADY TRUE item 14), separate from the plan commit.
        `-s` is required on every commit: the DCO check fails any unsigned one. The creation
        loop was dry-run verified 2026-09-14 in a throwaway clone — 28 entries, all staged at
        mode `120000`, all resolving.

        done when: the second block prints `STEP 1 CHECKS PASSED` and exits 0.

<!-- COPY -->
```bash
( set -u

# 1) the plan document, its own commit — see above
git add launchpad/plans/2026-09-14-issue-2151-professor-discoverability.md || exit 1
git commit -s -m "docs(plans): plan the Professor suite's root discoverability (#2151)" || exit 1

# 2) the 28 symlinks
for d in .agents .claude .codex .goose; do
  for s in scan-repo draft-page update-page provenance-log screen-sensitive library-index verify-claims; do
    mkdir -p "$d/skills/$s" || exit 1
    ln -s "../../../launchpad/agents/the-professor/skills/$s/SKILL.md" "$d/skills/$s/SKILL.md" || exit 1
  done
done
git add .agents/skills .claude/skills .codex/skills .goose/skills || exit 1
git commit -s -m "feat(the-professor): register the seven skills at the repo root by symlink (#1397)" || exit 1

echo "CREATED — now run the verification block below"
)
```

<!-- COPY -->
```bash
( set -u

STEP1_SHA=$(git rev-parse HEAD) || exit 1   # pin it: HEAD moves, and `git show --name-only
echo "STEP1_SHA=$STEP1_SHA"                 # --format=` prints NOTHING for a merge, reading as a pass

ENTRIES=$(mktemp) || exit 1                 # not a fixed /tmp path — parallel worktrees would clobber it
trap 'rm -f "$ENTRIES"' EXIT

# Both checks below read THE COMMIT, not the index and not the working tree. `git ls-files`
# reads the index and `readlink` reads the working tree, so a correct-on-disk link with a
# different blob committed would have passed both. What merges is the commit.

# a) exactly 28 entries, every one committed at mode 120000. The COUNT is an assertion, not
#    a message: an empty result set must FAIL, not pass vacuously. A 100644 copy fails here.
git ls-tree -r "$STEP1_SHA" -- .agents/skills .claude/skills .codex/skills .goose/skills \
  | grep -E '/(scan-repo|draft-page|update-page|provenance-log|screen-sensitive|library-index|verify-claims)/SKILL\.md$' \
  > "$ENTRIES"
awk 'BEGIN{bad=0} $1!="120000"{print "NOT A SYMLINK:", $0; bad=1} \
     END{if (NR!=28) {print "WRONG COUNT:", NR; exit 1} exit bad}' "$ENTRIES" \
  || { echo "CHECK (a) FAILED"; exit 1; }

# b) each link points at ITS OWN skill. Per link, never as a deduped set: collapsing 28
#    targets to 7 unique strings passes even when two skills' links are swapped — both
#    resolve, and one silently serves the wrong procedure. For a symlink blob,
#    `git show <sha>:<path>` prints the target string.
for d in .agents .claude .codex .goose; do
  for s in scan-repo draft-page update-page provenance-log screen-sensitive library-index verify-claims; do
    want="../../../launchpad/agents/the-professor/skills/$s/SKILL.md"
    got=$(git show "$STEP1_SHA:$d/skills/$s/SKILL.md" 2>/dev/null) \
      || { echo "NOT IN COMMIT: $d/skills/$s/SKILL.md"; exit 1; }
    [ "$got" = "$want" ] || { echo "WRONG TARGET $d/$s: got '$got' want '$want'"; exit 1; }
  done
done

# c) single-parent, so (d) cannot be vacuous on a merge
[ "$(git rev-list --parents -n1 "$STEP1_SHA" | wc -w)" = 2 ] \
  || { echo "NOT SINGLE-PARENT — the path check below would be vacuous"; exit 1; }

# d) exactly 28 paths, none under launchpad/
PATHS=$(git show --name-only --format= "$STEP1_SHA") || exit 1
printf '%s\n' "$PATHS" | grep -q '^launchpad/' \
  && { echo "COMMIT TOUCHED launchpad/ — canonical files must not change"; exit 1; }
[ "$(printf '%s\n' "$PATHS" | grep -c .)" = 28 ] \
  || { echo "COMMIT DOES NOT CONTAIN EXACTLY 28 PATHS"; exit 1; }

echo "STEP 1 CHECKS PASSED"
)
```

STEP 2  Prove the links resolve from a clean checkout                        [needs 1]  ← RUNS HERE

        First point the feature is observably real, and the strongest evidence #1397 asks for:
        *"verified after `git clone`, not only in a working tree where the target happens to be
        present."* The `cd` is inside the block deliberately — with it in prose, a builder
        pasting the block and then the checks would re-test the building worktree and get an
        identical clean result, manufacturing clean-clone evidence that tested nothing.

        If the local clone fails (the source is a shallow clone), push the branch and clone from
        `https://github.com/launchpad-26/buzz` instead. Record which was used in the PR — the
        remote clone is the stronger evidence.

        done when: the block prints `STEP 2 CHECKS PASSED`, and its `pwd` line and seven `name:`
        lines are captured for the PR.

<!-- COPY -->
```bash
( set -u

SCRATCH=$(mktemp -d) || exit 1
trap 'rm -rf "$SCRATCH"' EXIT        # cleans up on the FAILURE path too, not just success
CLONE="$SCRATCH/clean-2151"

git clone --branch feature/2151-professor-discoverability --single-branch \
  /home/serina/Launchpad/buzz "$CLONE" \
  || { echo "local clone failed — push the branch and clone from https://github.com/launchpad-26/buzz"; exit 1; }

cd "$CLONE" || exit 1
pwd                                  # capture: proof of WHICH tree was tested
CLONE_REAL=$(readlink -f "$CLONE") || exit 1   # resolved-to-resolved, or a symlinked TMPDIR
                                               # makes every link look like it escapes

for d in .agents .claude .codex .goose; do
  for s in scan-repo draft-page update-page provenance-log screen-sensitive library-index verify-claims; do
    f="$d/skills/$s/SKILL.md"
    [ -L "$f" ] || { echo "NOT A SYMLINK IN CLONE: $f"; exit 1; }  # git checked out a real link,
    [ -f "$f" ] || { echo "DANGLING IN CLONE: $f"; exit 1; }       # not a text file; -f follows it
    r=$(readlink -f "$f") || { echo "UNRESOLVABLE: $f"; exit 1; }
    case "$r" in "$CLONE_REAL"/*) ;; *) echo "ESCAPES CLONE: $f -> $r"; exit 1;; esac
  done
done

# the load keys a harness indexes, read THROUGH the links, in the clean clone. Counted, not
# just printed: a file whose name: fell outside the first 8 lines would print nothing and
# still reach CHECKS PASSED.
NAMES=$(for s in scan-repo draft-page update-page provenance-log screen-sensitive library-index verify-claims; do
          awk 'FNR<=8 && /^name:/{print; exit}' ".claude/skills/$s/SKILL.md"
        done) || exit 1
printf '%s\n' "$NAMES"
[ "$(printf '%s\n' "$NAMES" | grep -c .)" = 7 ] || { echo "EXPECTED 7 name: LINES"; exit 1; }

echo "STEP 2 CHECKS PASSED"
)
```

STEP 3  Rewrite both metadata texts, in one commit; check the README         [independent]

        Two files, one commit for #2152 (ALREADY TRUE item 14):
        `launchpad/agents/the-professor/.plugin/plugin.json` and
        `launchpad/agents/the-professor/personas/the-professor.persona.md`.

        **What to write.** Replace the stale claims with text that distinguishes what is built
        from what is not. The true state (ALREADY TRUE item 11): Phase 0 decided; Phase 1 — the
        `tools/professor.py` tool layer — built and hardened; Phase 1b (#2131) filed and not
        started; Phases 2-7 unbuilt. All seven `SKILL.md` procedures are written. Any vocabulary
        that conveys that is fine — `implemented`/`planned` is as good as `built`/`not yet
        built`. Keep the persona's two still-accurate paragraphs: the note that the comment is
        stripped before the body becomes a prompt, and the "OPTIONAL COMPANION, NOT REQUIRED
        INFRASTRUCTURE" reframe.

        **Do not touch** `version` (escalated in STEP 5, per #2152 and Serina's 2026-09-14 call
        to leave it at `0.1.0`), the `skills:` list, or the persona body.

        **The script does not judge your wording** — see WHY THIS PLAN IS SHORT. It asserts the
        exact literal stale strings are gone and that both files are still structurally valid.
        Whether the replacement is *accurate* is `review-docs`' call and a human's, against this
        checklist: does each text say Phase 1 is built, that Phase 1b is filed but not started,
        and that Phases 2-7 are not built — without asserting one blanket status over all of
        them, in either direction?

        **README:** #2152 makes this a check with a mandatory written answer, not a conditional
        edit. Re-check at branch tip; ALREADY TRUE item 10 is a snapshot, not the finding. Edit
        only if it carries a blanket claim about the whole suite — differently-phrased-but-
        accurate is not a defect. If you do edit it, include it in this same commit.

        done when: the block prints `STEP 3 CHECKS PASSED`, exits 0, and the PR records the
        README verdict either way plus both new texts for `review-docs` to judge.

<!-- COPY -->
```bash
( set -u

python3 - <<'PY' || exit 1
import json, re, sys, yaml
errs = []

# ---- plugin.json: structure, and the exact stale literal gone -------------------------
pj = 'launchpad/agents/the-professor/.plugin/plugin.json'
try:
    d = json.load(open(pj))
except Exception as e:
    print('FAIL: plugin.json does not parse:', e); sys.exit(1)

if 'skills' in d:
    errs.append('plugin.json must NOT declare a skills array (#2152, design doc §5)')
if d.get('version') != '0.1.0':
    errs.append('version must stay 0.1.0 — it is a STEP 5 escalation, not an edit')
# The EXACT current literal, not a pattern. A pattern cannot tell an obsolete suite-wide
# claim from accurate new prose that happens to reuse a word.
if 'PROPOSED (see launchpad/Research/the-professor-skill-suite-redesign.md' in d.get('description', ''):
    errs.append('plugin.json still carries the verbatim stale PROPOSED claim')

# ---- persona: frontmatter parses, skills is a real list of seven ----------------------
pp = 'launchpad/agents/the-professor/personas/the-professor.persona.md'
t = open(pp).read()
m = re.match(r'^---\n(.*?)\n---\n', t, re.S)
if not m:
    print('FAIL: persona frontmatter block not found'); sys.exit(1)
fm_text = m.group(1)

# Parse, don't fence-test: the edit is to a comment block INSIDE the frontmatter, so a
# wrapped line that loses its leading '#' breaks the YAML while both --- fences survive.
try:
    fm = yaml.safe_load(fm_text)
except Exception as e:
    print('FAIL: persona frontmatter does not parse as YAML:', e); sys.exit(1)
if not isinstance(fm, dict):
    print('FAIL: persona frontmatter is not a mapping'); sys.exit(1)

skills = fm.get('skills')
if not isinstance(skills, list):
    # A mapping whose keys are the seven names iterates identically but the loader wants a list.
    errs.append(f'skills: must be a YAML list, got {type(skills).__name__}')
else:
    want = ['scan-repo', 'draft-page', 'update-page', 'provenance-log',
            'screen-sensitive', 'library-index', 'verify-claims']
    got = [str(s).strip('/').split('/')[-1] for s in skills]
    missing = [s for s in want if s not in got]
    if missing:
        errs.append(f'skills list missing {missing} — got {got}')

# Full sentences, not fragments. 'do not exist as working code yet' alone would reject the
# accurate new wording "The later phases do not exist as working code yet" -- the exact
# false-positive failure mode that broke all three earlier versions of this check.
for lit in ('# PROPOSED — not yet built. See launchpad/Research/the-professor-skill-suite-redesign.md.',
            'The seven skills below, and the tool layer they call, do not exist as working code yet'):
    if lit in fm_text:
        errs.append(f'persona still carries the verbatim stale line: {lit!r}')

if errs:
    for e in errs:
        print('FAIL:', e)
    sys.exit(1)

print('OK: structure valid, stale literals gone, skills is a list of', len(skills))
print('--- plugin description (for review-docs) ---'); print(d['description'])
PY

# every listed skill path still resolves on disk, pack-root relative (ALREADY TRUE item 8)
for s in scan-repo draft-page update-page provenance-log screen-sensitive library-index verify-claims; do
  [ -f "launchpad/agents/the-professor/skills/$s/SKILL.md" ] || { echo "PATH BROKEN: $s"; exit 1; }
done

# the README verdict — output goes in the PR verbatim, either way
echo "--- README check (#2152) ---"
grep -nE 'PROPOSED|not yet built|now built|Phase 1' launchpad/agents/the-professor/README.md

# ONE commit for #2152 (launchpad/AGENTS.md line 404). Guard `git add`: unguarded, a failed
# add lets the commit record whatever else happened to be staged.
#
# The README is staged ONLY if this step actually edited it. An earlier version listed just
# the two metadata files while the prose said "if you do edit it, include it in this same
# commit" -- so a README edit was silently dropped, the block still printed CHECKS PASSED,
# and STEP 4 then failed one step later blaming STEP 3 for not committing. Measured.
# Positional parameters, NOT a space-joined string: zsh does not word-split an unquoted
# variable (SHELL CONVENTIONS item 2), so `git add $LIST` would pass all three paths as a
# single argument. `set --` / `"$@"` behave identically in bash and zsh.
README=launchpad/agents/the-professor/README.md
set -- launchpad/agents/the-professor/.plugin/plugin.json \
       launchpad/agents/the-professor/personas/the-professor.persona.md
if ! git diff --quiet -- "$README"; then
  echo "README was edited — including it in this commit"
  set -- "$@" "$README"
fi
git add "$@" || exit 1

# nothing this step touched may be left behind unstaged
for f in "$@"; do
  git diff --quiet -- "$f" || { echo "UNSTAGED CHANGES REMAIN IN: $f"; exit 1; }
done
git commit -s -m "docs(the-professor): metadata states what shipped, not what was proposed (#2152)" || exit 1

echo "STEP 3 CHECKS PASSED"
)
```

STEP 4  Run the gates and prove the branch is clean                          [needs 1, 3]

        Activate Hermit first so `./bin` leads `PATH`. The pre-push hook self-pins, but non-hook
        commands do not.

        A branch-skew failure here is **real**. An earlier draft carried a caveat that the lane
        misfires on the first remote alphabetically (buzz#2108) — that bug is fixed and closed
        (`d22184b41`: the remote whose URL names the cohort repo wins, first-match only as a
        fallback, `BRANCH_SKEW_BASE` overriding). The stale caveat would have pre-authorised
        pushing past a genuine failure.

        `scripts/check-push-head-scope.sh` is deliberately **not** run. It is a `use_stdin: true`
        lane reading git's pre-push ref records from stdin: standalone it blocks until EOF, and
        with empty stdin it checks no ref and exits 0 regardless, being warn-only by design. It
        is exercised by the real push, not simulable here.

        done when: the block prints `STEP 4 CHECKS PASSED` and exits 0, with output captured.

<!-- COPY -->
```bash
. ./bin/activate-hermit   # outside the subshell: it must affect the commands below

( set -u

# 0) nothing left uncommitted. Capture the status separately and guard git's OWN exit code —
#    `[ -z "$(git status --porcelain)" ]` reads a FAILED git status as a clean tree.
STATUS=$(git status --porcelain) || { echo "git status failed"; exit 1; }
[ -z "$STATUS" ] || { echo "UNCOMMITTED CHANGES:"; printf '%s\n' "$STATUS"; exit 1; }

# 1) the branch actually carries both #2152 edits — the backstop for STEP 3 having committed
CHANGED=$(git diff --name-only origin/launchpad...HEAD) || exit 1
printf '%s\n' "$CHANGED" | grep -q '\.plugin/plugin\.json$' \
  || { echo "branch does not change plugin.json — STEP 3 was not committed"; exit 1; }
printf '%s\n' "$CHANGED" | grep -q 'the-professor\.persona\.md$' \
  || { echo "branch does not change the persona — STEP 3 was not committed"; exit 1; }

# 2) the pack's own harness — CI runs exactly this on launchpad/agents/** changes
python3 launchpad/agents/the-professor/tools/check_professor.py --offline \
  || { echo "HARNESS FAILED"; exit 1; }

# 3) the two pre-push lanes that can be run standalone.
#    file-size-check MUST be given a base. Bare, it resolves `git merge-base origin/main HEAD`,
#    which fails in this shallow fork checkout -- measured here: a stack trace and exit 1,
#    for a reason unrelated to any change. The pre-push hook does not hit this because
#    `bin/.lefthookrc` (sourced only by the generated .git/hooks/*) computes and exports
#    CHECK_FILE_SIZES_BASE. Running the lane by hand must do the same. Verified: with the
#    base set it exits 0.
CHECK_FILE_SIZES_BASE="$(git merge-base origin/launchpad HEAD)" \
  just file-size-check || { echo "file-size-check FAILED"; exit 1; }
./launchpad/scripts/check-branch-skew.sh || { echo "branch-skew FAILED — treat as real"; exit 1; }

echo "STEP 4 CHECKS PASSED"
)
```

STEP 5  Write the PR body and open the PR                                    [needs 2, 3, 4]

        Five things this PR must say, each required by an issue rather than by taste.

        The plain-language opener is a `> [!NOTE]` callout, **not** an `## In plain terms`
        heading: `launchpad/AGENT_PR_TEMPLATE.md` Hard Rule A forbids headings not in the
        template, and no such heading exists there. `pr_body_check.py` never looks for the
        phrase, so a heading would break the rule silently. PR #2097 solved the same tension the
        same way.

        (a) **Directory choice, with the reason.** All four — `.agents/`, `.claude/`, `.codex/`,
        `.goose/`. ADR-0030 permits all four by name; `launchpad/AGENTS.md` §3 repeats the list;
        and the repo already registers both existing symlinked skills (`desktop-screenshot`,
        `sprout-cli`) into all four, so this matches precedent rather than inventing one. Add
        ADR-0030's own Context point: `.agents/skills/` is **not** read by Claude Code and
        `.claude/skills/` is, so registering into `.agents/` alone would satisfy the original
        issue's letter while failing its purpose.

        (b) **Discovery evidence, with an honest statement of its limit.** Paste STEP 2's raw
        output. Then state plainly: this proves the 28 entries are symlinks, that each resolves
        to its canonical file *from a clean clone*, and that each carries the `name:` load key a
        harness indexes — it does **not** prove any particular harness's loader enumerated them,
        because that happens inside the harness and no shell command can produce it.

        For the session half of #1397's criterion, start a **new** session with cwd at the repo
        root on this branch and capture its actual skill listing as text. A session's skill
        inventory is fixed at start, so the session that built this cannot report on itself.
        **Do not synthesise a transcript.** If a real listing cannot be captured, write that
        sentence into the PR under the criterion and leave the box unticked.

        **And the closing keyword follows that outcome:**
        - listing captured -> `Closes #1397` and `Closes #2152`
        - listing not captured -> `Refs #1397` and `Closes #2152`, with one sentence saying why

        Leaving the box honestly unticked while still auto-closing #1397 on merge would undo the
        honesty. The knock-on is intended: with #1397 open, Feature #2151 cannot close yet.

        A weaker supporting point may be offered, labelled an argument rather than evidence:
        `.claude/skills/` already holds `agentic-debugging` and `review-final` as working
        discoverable skills here, so the mechanism is live and the new entries share its shape.

        (c) **The README verdict** from STEP 3, stated either way, quoting the line.

        (d) **Escalation — the `version` field.** It stays `0.1.0`. #2152 forbids picking a
        number, and Serina confirmed on 2026-09-14: leave it, escalate. Under `Escalations`, ask
        whether Phase 1 shipping should move it and note that nobody has decided the pack's
        release-numbering rule. File an issue in `launchpad-26/buzz` if none covers it, and link
        it from the PR and from #2152.

        (e) **Both new metadata texts, quoted**, so `review-docs` and a human can judge accuracy
        — the script deliberately does not (see WHY THIS PLAN IS SHORT). State the checklist
        they are judging against, from STEP 3.

        Also record, so a reviewer need not re-derive it: no new ADR is required (ADR-0030 is
        generic and AGENTS.md §3 carries the exception); and PR #1398 was closed unmerged for
        copying rather than symlinking, with STEP 1's mode-`120000` assertion the thing that
        stops this PR repeating it.

        `pr_body_check.py` takes **no arguments** — it reads everything from the environment,
        and `CLOSING_REFS` must name the issues the body's closing keywords actually close. It
        is not "unknown": the checker reads `[]` as GitHub authoritatively reporting that
        nothing closes, which false-fails a correct body and lets the `Refs` variant pass while
        asserting something untrue. Keep it in sync with the (b) branch by hand — the command
        cannot verify that for you.

        done when: the check below passes; the body names all four directories with the reason,
        carries the explicit "does not prove" sentence from (b), names the `version` question
        under `Escalations`, quotes both new texts, and uses the correct keyword for #1397.

<!-- COPY -->
```bash
# Mirrors .github/workflows/launchpad-pr-check.yml (~lines 86-111). Write the body to a file
# first so the check can be re-run unchanged.
#   listing captured     -> body: Closes #1397, Closes #2152 -> CLOSING_REFS='[1397,2152]'
#   listing NOT captured -> body: Refs #1397,   Closes #2152 -> CLOSING_REFS='[2152]'
BODY="$(cat pr-body.md)" \
LABELS='["by:agent"]' \
CLOSING_REFS='[1397,2152]' \
FEATURE_CHILDREN="$(gh api repos/launchpad-26/buzz/issues/2151/sub_issues --jq '[.[].number]')" \
python3 launchpad/scripts/pr_body_check.py
```

PARALLEL

  **Run this plan serially.** STEP 1 and STEP 3 touch disjoint files but both commit, so they
  contend for one `.git/index.lock`, and STEP 1's checks are pinned to `$STEP1_SHA` precisely
  because a concurrent commit moving `HEAD` made them report false failures. Concurrency would
  need one worktree per step, and for 28 symlinks and two prose edits the coordination costs
  more than it saves.

GATES

  review-plan — on this rewritten plan, before any build.

  Codex cross-model review — standing instruction, on whatever artefact the pipeline is about.
  Read its `.raw` output, not only its summary.

  **review-docs — load-bearing here, not routine.** This change is majority prose, and by
  design the script does not judge whether the new wording is accurate. That judgement is this
  gate's job. Give it STEP 3's checklist explicitly.

  If review-docs is skipped, **#2152's DoD bullets 1, 2 AND 3 have nothing enforcing them** —
  not bullet 3 alone, as an earlier draft of this section claimed. The exact-literal check
  catches the stale text verbatim, but a *reflowed or re-punctuated* restatement defeats it and
  still violates bullets 1 and 2. Measured: wrapping the persona's stale sentence across a line
  break, and re-punctuating the plugin description's `PROPOSED (…)` parenthetical, both pass the
  script while leaving the claim false. That is the accepted price of exact literals — a false
  *negative* on cosmetically-altered stale text — and the answer is this gate, not a fourth
  generation of smarter matcher.

  review-final — after STEP 4, before the PR opens.

  review-gate caution: the changed set is 28 `.md` symlinks plus one `.json` and one `.md`.
  review-gate has a documented history of failing to route file types its case arms do not
  cover. If `prepare` fails to route `plugin.json`, widen the roster by hand rather than
  skipping the review — an unroutable file is not an unreviewed-but-fine file.

  qa explore mode: does not apply. No new runtime interface — no CLI argument, no API, no UI.
  Symlink resolution and skill enumeration are already first-class planned steps.

  Accessibility: out of scope. No UI is touched.

  Not a gate but it will run: `launchpad-agents-tests.yml` fires on `launchpad/agents/**`.
  STEP 4 runs its `professor-tools` command locally, so CI is confirmation, not discovery.

BUDGET

  STEP 5(b) is the only step with real overrun risk, and specifically obtaining a genuine
  fresh-session listing. Creating 28 symlinks is minutes. Budget for the possibility that the
  listing cannot be captured and that the correct outcome is a plainly stated partial plus
  `Refs #1397`.

  Second: STEP 2's clone, if the shallow local source misbehaves and the branch must be pushed
  so it can be cloned from the remote.

OPEN

  1. The `version` field stays `0.1.0`. Whether Phase 1 shipping should move it is undecided;
     escalated in STEP 5(d), not resolved here.
  2. Whether a fresh-session skill listing is obtainable before the PR opens. STEP 5(b) plans
     both outcomes and forbids inventing one.
  3. `launchpad/ARCHITECTURE.md`, `REQUIREMENTS.md` and `VISION.md` also contain the string
     `PROPOSED`. Not checked whether any describes the Professor's build state — #2152 scopes to
     `plugin.json`, the persona, and the README. If a builder finds a genuine stale Professor
     claim there, file it; do not fix it here.
  4. No `Size` line on any of the three issues. Worth adding one to the children if this fork's
     template expects it.

LEFT OUT

  Any edit to the seven `SKILL.md` files — **with one recorded exception, added after review.**

  As planned: both #1397 and #2151 exclude it, this work adds pointers and changes no content,
  and STEP 1's check (d) asserts the *symlink commit* touches nothing under `launchpad/`.

  The exception: `review-skill` found `screen-sensitive/SKILL.md` waived its
  `$PROFESSOR_PACK_ROOT` check on the stated premise that it "is never invoked standalone" — a
  premise this registration falsifies — while still carrying a manual-pass branch that could
  report a secrets gate clean without screening. Serina agreed on 2026-09-14 to fix it here
  rather than ship a fail-open, so that one file **is** edited on this branch (commit
  `58fc4598c`).

  Be precise about what check (d) did: it is scoped to `$STEP1_SHA`, a single commit, so it
  could never have caught an edit made in a later one. It did not assert this exception away —
  nothing mechanical did. The authorisation is recorded here and in the PR body, not only in a
  commit message.

  A new ADR. ADR-0030 is Accepted and generic, and AGENTS.md §3 already carries the exception in
  writing. Writing one would re-decide a settled question.

  Executing a skill from a checkout outside this fork — Open Questions item 6 (`<pack-root>`
  resolution), named as unbuilt in #2151's own Out of scope.

  ADR-0046 and the `tools/server.py` references in AGENTS.md §3 — #2104 owned those, and it is
  closed.

  Any Phase 1b work. #2131 is open and unstarted; a separate Feature.

  The seven non-Professor cohort skills sitting in `.claude/skills/` as real files with no
  canonical copy under `launchpad/`. Real, a different shape from ADR-0030's exception, and
  #2151 files it as separate.

  Adding a `skills` array to `plugin.json`. Forbidden by #2152; STEP 3 asserts its absence.

  Any script that tries to judge whether the new prose is truthful. Three rounds proved it
  cannot be done mechanically; `review-docs` and human review own that.
