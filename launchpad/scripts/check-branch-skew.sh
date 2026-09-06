#!/usr/bin/env bash
# Pre-push guard, cohort variant of scripts/check-branch-skew.sh (#15).
#
# The upstream script assumes `origin` is the project and `main` is the PR base —
# both true in block/buzz, neither true here. This fork's PR base is `launchpad`,
# and which remote name resolves to the cohort repo varies by contributor: some
# have `origin` pointing straight at launchpad-26/buzz (so `origin/launchpad`
# exists), others keep `origin` as a personal fork and add a separate `launchpad`
# remote (so it's `launchpad/launchpad` that exists, and `origin/launchpad` does
# not). Hardcoding either shape blocks the other contributor's valid pushes, so
# this searches every configured remote for a ref literally named `launchpad`.
#
# Among the remotes that have one, a remote whose URL actually names the cohort
# repo (…/launchpad-26/buzz) wins over any other (#2108): "first remote
# alphabetically" once selected a personal-fork remote that happened to sort
# before `origin`, and the gate then compared the branch against a trunk 349
# commits behind the real one — failing a push that was fully current with the
# actual PR base, with advice (`git merge <fork>/launchpad`) that would have
# contaminated a cohort PR with fork-only commits. First-match survives only as
# the fallback when no remote's URL names the cohort repo, preserving the
# contributor-naming flexibility above. BRANCH_SKEW_BASE overrides the search
# entirely (same shape as CHECK_FILE_SIZES_BASE); an override that does not
# resolve is a config error and blocks rather than silently un-gating the push.
#
# Lives under launchpad/ rather than editing scripts/check-branch-skew.sh directly
# (see launchpad/AGENTS.md §3): the upstream script is unmodified and still
# reusable, and this file carries no upstream merge-conflict risk. lefthook.yml's
# own `run:` line for pre-push.branch-skew points here instead of at the
# upstream path — that's the only edit made to an upstream-owned file.
set -euo pipefail

branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$branch" = "launchpad" ] || [ "$branch" = "HEAD" ]; then
  exit 0
fi

# The URL suffix match tolerates every clone shape while never matching sibling
# repos like launchpad-26/buzz-infrastructure, whose URL does not END with the
# pattern. The separator before the org is `[/:]`, not `/` alone: scp-like SSH
# URLs (git@github.com:launchpad-26/buzz.git) put a COLON there, and a
# slash-only pattern silently failed to match the real origin on first test —
# falling back to first-match, the exact bug being fixed.
is_cohort_remote() {
  local url
  url=$(git remote get-url "$1" 2>/dev/null) || return 1
  # Lowercase before matching: GitHub treats org/repo names case-insensitively,
  # so git@github.com:Launchpad-26/Buzz.git is the same functioning repo and
  # must not silently fall back to first-match (review finding on this fix).
  url="${url,,}"
  while [ "${url%/}" != "$url" ]; do url="${url%/}"; done
  url="${url%.git}"
  while [ "${url%/}" != "$url" ]; do url="${url%/}"; done
  case "$url" in
    *[/:]launchpad-26/buzz) return 0 ;;
  esac
  return 1
}

base_ref=""
if [ -n "${BRANCH_SKEW_BASE:-}" ]; then
  if ! git rev-parse --verify --quiet "${BRANCH_SKEW_BASE}^{commit}" >/dev/null; then
    echo "BRANCH_SKEW_BASE is set to '${BRANCH_SKEW_BASE}' but that does not resolve to a commit." >&2
    exit 1
  fi
  base_ref="${BRANCH_SKEW_BASE}"
else
  fallback_ref=""
  for remote in $(git remote); do
    git fetch --quiet "$remote" launchpad 2>/dev/null || continue
    git rev-parse --verify --quiet "${remote}/launchpad" >/dev/null || continue
    if is_cohort_remote "$remote"; then
      base_ref="${remote}/launchpad"
      break
    fi
    if [ -z "$fallback_ref" ]; then
      fallback_ref="${remote}/launchpad"
    fi
  done
  if [ -z "$base_ref" ]; then
    base_ref="$fallback_ref"
  fi
fi

if [ -z "$base_ref" ]; then
  # No remote has a `launchpad` ref at all — cannot compare, so do not block.
  # Matches the upstream script's own fallback when origin/main is unresolvable.
  exit 0
fi

base=$(git merge-base HEAD "$base_ref")
if [ "$base" = "$(git rev-parse "$base_ref")" ]; then
  exit 0
fi

overlap=$(comm -12 \
  <(git diff --name-only "$base" "$base_ref" -- | sort) \
  <(git diff --name-only "$base" HEAD -- | sort))

if [ -z "$overlap" ]; then
  exit 0
fi

{
  echo "Branch is behind ${base_ref}, and launchpad changed files this branch also touches:"
  echo "$overlap" | sed 's/^/  /'
  echo "Local checks ran on a tree CI will never test. Run 'git merge ${base_ref}',"
  echo "resolve, re-run checks, then push."
} >&2
exit 1
