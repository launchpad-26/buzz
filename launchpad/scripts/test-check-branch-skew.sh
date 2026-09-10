#!/usr/bin/env bash
# Exercises launchpad/scripts/check-branch-skew.sh (#15) against real git repos in
# a scratch directory, covering both remote-naming conventions the issue names:
# `origin` pointing straight at the cohort repo, and `origin` as a personal fork
# with a separate `launchpad` remote for the cohort repo. Each scenario gets its
# own fresh bare "cohort repo" fixture, so scenarios cannot see each other's
# commits and no scenario's outcome depends on the order the others ran in.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUARD="${SCRIPT_DIR}/check-branch-skew.sh"

WORK=$(mktemp -d)
trap 'rm -rf "${WORK}"' EXIT

PASS=0
FAIL=0

check() {
  local label=$1 expected=$2 got=$3
  if [ "${expected}" = "${got}" ]; then
    echo "PASS: ${label}"
    PASS=$((PASS + 1))
  else
    echo "FAIL: ${label} — expected exit ${expected}, got ${got}"
    FAIL=$((FAIL + 1))
  fi
}

new_bare_cohort_repo() {
  local name=$1
  git init --bare --initial-branch=launchpad --quiet "${WORK}/${name}.git"
}

configure() {
  git -C "$1" config user.email "test@example.invalid"
  git -C "$1" config user.name "Test"
}

seed() {
  # Commits + pushes an initial AGENTS.md to $1's launchpad branch, via a
  # throwaway clone so the bare repo itself is never checked out directly.
  local bare=$1
  rm -rf "${WORK}/seed"
  git clone --quiet "${bare}" "${WORK}/seed"
  configure "${WORK}/seed"
  echo "seed" > "${WORK}/seed/AGENTS.md"
  git -C "${WORK}/seed" add AGENTS.md
  git -C "${WORK}/seed" commit --quiet -m "seed"
  git -C "${WORK}/seed" push --quiet origin HEAD:launchpad
}

run_guard() {
  (cd "$1" && bash "${GUARD}")
}

# --- convention A, current: branch is at the tip of origin/launchpad -----------
new_bare_cohort_repo cohort-a1
seed "${WORK}/cohort-a1.git"
rm -rf "${WORK}/a1"
git clone --quiet "${WORK}/cohort-a1.git" "${WORK}/a1"
configure "${WORK}/a1"
git -C "${WORK}/a1" checkout --quiet -b feature-current
status=0
run_guard "${WORK}/a1" || status=$?
check "convention A: branch current with origin/launchpad exits 0" 0 "${status}"

# --- convention A, behind, no overlap: must not block --------------------------
new_bare_cohort_repo cohort-a2
seed "${WORK}/cohort-a2.git"
rm -rf "${WORK}/a2"
git clone --quiet "${WORK}/cohort-a2.git" "${WORK}/a2"
configure "${WORK}/a2"
git -C "${WORK}/a2" checkout --quiet -b feature-behind-no-overlap
echo "unrelated" > "${WORK}/a2/other-file.txt"
git -C "${WORK}/a2" add other-file.txt
git -C "${WORK}/a2" commit --quiet -m "unrelated local change"
# Advance the cohort repo's launchpad branch AFTER the feature branch forked,
# touching a DIFFERENT file, via a second independent clone.
rm -rf "${WORK}/a2-upstream"
git clone --quiet "${WORK}/cohort-a2.git" "${WORK}/a2-upstream"
configure "${WORK}/a2-upstream"
echo "upstream change" > "${WORK}/a2-upstream/unrelated-upstream.txt"
git -C "${WORK}/a2-upstream" add unrelated-upstream.txt
git -C "${WORK}/a2-upstream" commit --quiet -m "upstream advances"
git -C "${WORK}/a2-upstream" push --quiet origin HEAD:launchpad
status=0
run_guard "${WORK}/a2" || status=$?
check "convention A: behind but no overlapping files exits 0" 0 "${status}"

# --- convention A, behind, WITH overlap: must block -----------------------------
new_bare_cohort_repo cohort-a3
seed "${WORK}/cohort-a3.git"
rm -rf "${WORK}/a3"
git clone --quiet "${WORK}/cohort-a3.git" "${WORK}/a3"
configure "${WORK}/a3"
git -C "${WORK}/a3" checkout --quiet -b feature-behind-overlap
echo "feature branch also edits this" >> "${WORK}/a3/AGENTS.md"
git -C "${WORK}/a3" commit --quiet -am "feature branch edits AGENTS.md"
rm -rf "${WORK}/a3-upstream"
git clone --quiet "${WORK}/cohort-a3.git" "${WORK}/a3-upstream"
configure "${WORK}/a3-upstream"
echo "upstream also edits this" >> "${WORK}/a3-upstream/AGENTS.md"
git -C "${WORK}/a3-upstream" commit --quiet -am "upstream edits AGENTS.md too"
git -C "${WORK}/a3-upstream" push --quiet origin HEAD:launchpad
status=0
run_guard "${WORK}/a3" || status=$?
check "convention A: behind WITH overlapping file exits 1" 1 "${status}"

# --- convention B: origin is a personal fork, `launchpad` is the cohort repo ---
new_bare_cohort_repo cohort-b
seed "${WORK}/cohort-b.git"
rm -rf "${WORK}/personal-fork.git"
git init --bare --initial-branch=launchpad --quiet "${WORK}/personal-fork.git"
rm -rf "${WORK}/b"
git clone --quiet "${WORK}/cohort-b.git" "${WORK}/b" --origin launchpad
configure "${WORK}/b"
git -C "${WORK}/b" remote add origin "${WORK}/personal-fork.git"
git -C "${WORK}/b" checkout --quiet -b feature-b
echo "feature branch edits this" >> "${WORK}/b/AGENTS.md"
git -C "${WORK}/b" commit --quiet -am "edits AGENTS.md on convention B"
rm -rf "${WORK}/b-upstream"
git clone --quiet "${WORK}/cohort-b.git" "${WORK}/b-upstream"
configure "${WORK}/b-upstream"
echo "cohort repo also edits this" >> "${WORK}/b-upstream/AGENTS.md"
git -C "${WORK}/b-upstream" commit --quiet -am "cohort repo edits AGENTS.md too"
git -C "${WORK}/b-upstream" push --quiet origin HEAD:launchpad
status=0
run_guard "${WORK}/b" || status=$?
check "convention B: launchpad remote (not origin) is found and still blocks" 1 "${status}"

# --- #2108: a fork remote that sorts first must not shadow the cohort repo -----
# The work clone has two remotes with a `launchpad` ref: `aaa-fork` (sorts before
# `origin`, diverged, would block) and `origin` (URL ends launchpad-26/buzz, the
# branch is current with its tip). First-match picked aaa-fork and blocked a
# valid push; the URL preference must pick origin and pass.
mkdir -p "${WORK}/launchpad-26"
git init --bare --initial-branch=launchpad --quiet "${WORK}/launchpad-26/buzz.git"
seed "${WORK}/launchpad-26/buzz.git"
rm -rf "${WORK}/fork.git"
git init --bare --initial-branch=launchpad --quiet "${WORK}/fork.git"
rm -rf "${WORK}/fork-clone"
git clone --quiet "${WORK}/launchpad-26/buzz.git" "${WORK}/fork-clone"
configure "${WORK}/fork-clone"
echo "fork-only change" >> "${WORK}/fork-clone/AGENTS.md"
git -C "${WORK}/fork-clone" commit --quiet -am "fork-only edit of AGENTS.md"
git -C "${WORK}/fork-clone" push --quiet "${WORK}/fork.git" HEAD:launchpad
rm -rf "${WORK}/d"
git clone --quiet "${WORK}/launchpad-26/buzz.git" "${WORK}/d"
configure "${WORK}/d"
git -C "${WORK}/d" remote add aaa-fork "${WORK}/fork.git"
git -C "${WORK}/d" checkout --quiet -b feature-d
echo "feature edits this too" >> "${WORK}/d/AGENTS.md"
git -C "${WORK}/d" commit --quiet -am "feature edits AGENTS.md"
status=0
run_guard "${WORK}/d" || status=$?
check "#2108: cohort-URL remote wins over an alphabetically-earlier fork" 0 "${status}"

# --- #2108: cohort-URL match is case-insensitive --------------------------------
# GitHub treats org/repo names case-insensitively, so a differently-cased remote
# URL is the same functioning repo and must still be preferred over the fork.
# Same shape as the scenario above, but the cohort repo path is Launchpad-26/Buzz.
mkdir -p "${WORK}/Launchpad-26"
git init --bare --initial-branch=launchpad --quiet "${WORK}/Launchpad-26/Buzz.git"
seed "${WORK}/Launchpad-26/Buzz.git"
rm -rf "${WORK}/fork2.git"
git init --bare --initial-branch=launchpad --quiet "${WORK}/fork2.git"
rm -rf "${WORK}/fork2-clone"
git clone --quiet "${WORK}/Launchpad-26/Buzz.git" "${WORK}/fork2-clone"
configure "${WORK}/fork2-clone"
echo "fork-only change" >> "${WORK}/fork2-clone/AGENTS.md"
git -C "${WORK}/fork2-clone" commit --quiet -am "fork-only edit of AGENTS.md"
git -C "${WORK}/fork2-clone" push --quiet "${WORK}/fork2.git" HEAD:launchpad
rm -rf "${WORK}/d2"
git clone --quiet "${WORK}/Launchpad-26/Buzz.git" "${WORK}/d2"
configure "${WORK}/d2"
git -C "${WORK}/d2" remote add aaa-fork "${WORK}/fork2.git"
git -C "${WORK}/d2" checkout --quiet -b feature-d2
echo "feature edits this too" >> "${WORK}/d2/AGENTS.md"
git -C "${WORK}/d2" commit --quiet -am "feature edits AGENTS.md"
status=0
run_guard "${WORK}/d2" || status=$?
check "#2108: differently-cased cohort URL still wins over the fork" 0 "${status}"

# --- #2108: BRANCH_SKEW_BASE overrides the remote search ------------------------
# Reuses the convention-A3 shape (behind with overlap, would exit 1) and proves
# an explicit base short-circuits the search entirely.
new_bare_cohort_repo cohort-e
seed "${WORK}/cohort-e.git"
rm -rf "${WORK}/e"
git clone --quiet "${WORK}/cohort-e.git" "${WORK}/e"
configure "${WORK}/e"
git -C "${WORK}/e" checkout --quiet -b feature-e
echo "feature branch also edits this" >> "${WORK}/e/AGENTS.md"
git -C "${WORK}/e" commit --quiet -am "feature branch edits AGENTS.md"
rm -rf "${WORK}/e-upstream"
git clone --quiet "${WORK}/cohort-e.git" "${WORK}/e-upstream"
configure "${WORK}/e-upstream"
echo "upstream also edits this" >> "${WORK}/e-upstream/AGENTS.md"
git -C "${WORK}/e-upstream" commit --quiet -am "upstream edits AGENTS.md too"
git -C "${WORK}/e-upstream" push --quiet origin HEAD:launchpad
status=0
run_guard "${WORK}/e" || status=$?
check "#2108 control: the override fixture blocks without the override" 1 "${status}"
status=0
(cd "${WORK}/e" && BRANCH_SKEW_BASE=HEAD bash "${GUARD}") || status=$?
check "#2108: BRANCH_SKEW_BASE=HEAD short-circuits the remote search" 0 "${status}"

# --- #2108: an unresolvable BRANCH_SKEW_BASE blocks, never silently un-gates ----
# Deliberately uses a fixture that passes by default (branch current with its
# cohort remote), so an exit 1 can only come from the override validation
# actually running — on a fixture that already blocks, this assertion would
# stay green even with the whole override feature deleted (review finding).
new_bare_cohort_repo cohort-f
seed "${WORK}/cohort-f.git"
rm -rf "${WORK}/f"
git clone --quiet "${WORK}/cohort-f.git" "${WORK}/f"
configure "${WORK}/f"
git -C "${WORK}/f" checkout --quiet -b feature-f
status=0
run_guard "${WORK}/f" || status=$?
check "#2108 control: the unresolvable-override fixture passes without it" 0 "${status}"
status=0
(cd "${WORK}/f" && BRANCH_SKEW_BASE=no-such-ref-zzy987 bash "${GUARD}") || status=$?
check "#2108: unresolvable BRANCH_SKEW_BASE exits 1" 1 "${status}"

# --- #2108: sibling repo URL (…/buzz-infrastructure) must NOT count as cohort ---
# aaa-infra sorts first and the branch is current with IT; origin is the real
# cohort repo and the branch is behind it with overlap. If the URL match ever
# loosens to a plain substring (the regression the code comment warns against),
# aaa-infra gets picked and this exits 0 instead of 1.
mkdir -p "${WORK}/g-remotes/launchpad-26"
git init --bare --initial-branch=launchpad --quiet "${WORK}/g-remotes/launchpad-26/buzz.git"
seed "${WORK}/g-remotes/launchpad-26/buzz.git"
git init --bare --initial-branch=launchpad --quiet "${WORK}/g-remotes/launchpad-26/buzz-infrastructure.git"
rm -rf "${WORK}/g"
git clone --quiet "${WORK}/g-remotes/launchpad-26/buzz.git" "${WORK}/g"
configure "${WORK}/g"
git -C "${WORK}/g" remote add aaa-infra "${WORK}/g-remotes/launchpad-26/buzz-infrastructure.git"
git -C "${WORK}/g" checkout --quiet -b feature-g
echo "feature edits this too" >> "${WORK}/g/AGENTS.md"
git -C "${WORK}/g" commit --quiet -am "feature edits AGENTS.md"
git -C "${WORK}/g" push --quiet aaa-infra HEAD:launchpad
rm -rf "${WORK}/g-upstream"
git clone --quiet "${WORK}/g-remotes/launchpad-26/buzz.git" "${WORK}/g-upstream"
configure "${WORK}/g-upstream"
echo "upstream also edits this" >> "${WORK}/g-upstream/AGENTS.md"
git -C "${WORK}/g-upstream" commit --quiet -am "upstream edits AGENTS.md too"
git -C "${WORK}/g-upstream" push --quiet origin HEAD:launchpad
status=0
run_guard "${WORK}/g" || status=$?
check "#2108: sibling buzz-infrastructure URL is not treated as the cohort repo" 1 "${status}"

# --- #2108: is_cohort_remote URL-shape pins, unit-level --------------------------
# Extracts the function from the guard and stubs `git remote get-url`, pinning
# the string-normalization edges the code comments name as real past failures
# (scp-style colon separator, trailing slash, .git, case). A failed extraction
# is loud: is_cohort_remote is then undefined and every case exits 127.
url_case() {
  # The variable holding the URL under test must NOT be named `url`:
  # is_cohort_remote declares `local url`, and bash's dynamic scoping makes that
  # shadow ours inside the git() stub it calls, so the stub would echo the
  # half-initialized inner variable instead of the test input.
  local label=$1 test_url=$2 expected=$3 got
  got=0
  (
    eval "$(sed -n '/^is_cohort_remote() {/,/^}/p' "${GUARD}")"
    git() {
      if [ "$1" = "remote" ] && [ "$2" = "get-url" ]; then echo "${test_url}"; return 0; fi
      command git "$@"
    }
    is_cohort_remote stub
  ) || got=$?
  check "url shape: ${label}" "${expected}" "${got}"
}
url_case "scp-style ssh URL matches" "git@github.com:launchpad-26/buzz.git" 0
url_case "https with trailing slash matches" "https://github.com/launchpad-26/buzz/" 0
url_case ".git plus trailing slash matches" "https://github.com/launchpad-26/buzz.git/" 0
url_case "mixed case matches" "git@github.com:Launchpad-26/Buzz.git" 0
url_case "sibling buzz-infrastructure does not match" "git@github.com:launchpad-26/buzz-infrastructure.git" 1
url_case "prefix collision mylaunchpad-26/buzz does not match" "https://github.com/mylaunchpad-26/buzz.git" 1

# --- no remote has a `launchpad` ref at all: must not block --------------------
rm -rf "${WORK}/c.git" "${WORK}/c"
git init --bare --initial-branch=main --quiet "${WORK}/c.git"
git clone --quiet "${WORK}/c.git" "${WORK}/c"
configure "${WORK}/c"
echo "x" > "${WORK}/c/f.txt"
git -C "${WORK}/c" add f.txt
git -C "${WORK}/c" commit --quiet -m "seed"
git -C "${WORK}/c" push --quiet origin HEAD:main
git -C "${WORK}/c" checkout --quiet -b feature-c
status=0
run_guard "${WORK}/c" || status=$?
check "no remote has a launchpad ref: does not block" 0 "${status}"

echo ""
echo "==================================================="
echo "${PASS} passed, ${FAIL} failed"
[ "${FAIL}" -eq 0 ]
