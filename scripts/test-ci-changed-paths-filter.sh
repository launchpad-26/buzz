#!/usr/bin/env bash
set -euo pipefail

# Guards against the bug behind launchpad-26/buzz#181: dorny/paths-filter
# (via picomatch) matches each pattern in a filter's list as an independent
# OR clause. A standalone negated pattern like '!desktop/src-tauri/**',
# mixed into a filter that also has positive patterns, does NOT act as an
# "AND NOT" exclusion the way a .gitignore-style reader would expect -- on
# its own it matches every file outside that directory, which silently
# makes the *entire* filter true for virtually any change in the repo.
# Verified against picomatch directly: an array of
#   ['desktop/**', '!desktop/src-tauri/**']
# matches 'launchpad/plans/foo.md' as true, even though that path isn't
# under desktop/ at all.
#
# The fix is not to mix quantifiers within one filter's pattern list. If a
# filter genuinely needs "under A, but not under B", split B into its own
# filter and OR the two outputs together at the job `if:` condition instead
# (this repo already does exactly that for desktop vs. desktop-rust).
#
# Also guards against the bug behind launchpad-26/buzz#442: dorny/paths-filter
# matches literal path patterns case-sensitively against `git diff
# --name-status`. A pattern like 'justfile' silently never matches a tracked
# `Justfile` -- the filter output for that entry is always false, and a PR
# that changes only that file never trips the jobs the filter gates. This is
# checked for every literal (non-glob) pattern in every filter: it must match
# a tracked file via `git ls-files` with the exact case as written. Glob and
# brace patterns (containing `*`, `?`, `[`, `{`, or `}`) and negated patterns
# (leading `!`, which name an exclusion rather than a real path) are skipped
# -- neither is a claim that a file with that exact name exists.

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
workflow="$repo_root/.github/workflows/ci.yml"

# Pull just the `filters: |` block passed to dorny/paths-filter and walk it
# filter-by-filter (a filter starts at 12-space indent, its patterns at 14).
awk '
  /filters: \|/ { in_block = 1; next }
  in_block && /^ {12}[A-Za-z0-9_-]+:$/ {
    if (name != "") { print name "\t" patterns }
    name = $1
    sub(/:$/, "", name)
    patterns = ""
    next
  }
  in_block && /^ {14}- /  {
    pat = $0
    sub(/^ *- /, "", pat)
    patterns = patterns pat ","
    next
  }
  in_block && name != "" && ! /^ {12,}/ { print name "\t" patterns; in_block = 0 }
  END { if (in_block && name != "") print name "\t" patterns }
' "$workflow" > /tmp/ci-changed-paths-filters.$$

failed=0
while IFS=$'\t' read -r filter_name patterns; do
  has_positive=0
  has_negative=0
  IFS=',' read -ra items <<< "$patterns"
  for item in "${items[@]}"; do
    [ -z "$item" ] && continue
    case "$item" in
      \'!*) has_negative=1 ;;
      *) has_positive=1 ;;
    esac
  done
  if [ "$has_positive" -eq 1 ] && [ "$has_negative" -eq 1 ]; then
    echo "::error::filter '$filter_name' in $workflow mixes a negated pattern with positive patterns -- picomatch treats each entry as an independent OR clause, so the negated pattern alone matches almost every file and the filter silently becomes true for nearly any change (this is exactly launchpad-26/buzz#181). Split the excluded path into its own filter and OR the outputs at the job if: condition instead." >&2
    failed=1
  fi

  # launchpad-26/buzz#442: every literal (non-glob, non-negated) pattern must
  # match a tracked file with the exact case as written.
  for item in "${items[@]}"; do
    [ -z "$item" ] && continue
    # Strip one layer of surrounding quotes, whichever kind wraps this entry
    # -- the YAML in ci.yml is single-quoted today, but a harmless style
    # change to double quotes must not turn into a false #442 citation here.
    raw="$item"
    case "$raw" in
      \'*\') raw="${raw#\'}"; raw="${raw%\'}" ;;
      \"*\") raw="${raw#\"}"; raw="${raw%\"}" ;;
    esac
    case "$raw" in
      !*) continue ;;              # exclusion pattern, not a claim a file exists
    esac
    case "$raw" in
      *[\*\?\[\{\}]*) continue ;;  # glob/brace pattern, not a literal path
    esac
    if ! git -C "$repo_root" ls-files --error-unmatch -- "$raw" > /dev/null 2>&1; then
      echo "::error::filter '$filter_name' in $workflow has entry '$raw' which does not match any tracked file with that exact case -- dorny/paths-filter matches literal patterns case-sensitively against git diff --name-status, so a wrong-case entry silently never fires (this is exactly launchpad-26/buzz#442). Check the tracked file's real casing with 'git ls-files' and correct the pattern." >&2
      failed=1
    fi
  done
done < /tmp/ci-changed-paths-filters.$$

rm -f /tmp/ci-changed-paths-filters.$$

if [ "$failed" -ne 0 ]; then
  exit 1
fi

echo "changed-paths filter contract passed"
