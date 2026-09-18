#!/usr/bin/env bash
# Fail if the committed packaged corpus is stale relative to the corpus nodes.
#
# WHY THIS EXISTS. `launchpad/docs/corpus/**` is the source; two generated files
# embed it:
#
#     launchpad/crates/knowledge/generated/corpus.json
#     desktop/public/knowledge-corpus.json
#
# Edit a node without repackaging and both go stale. CI catches it
# (`test_package.py::DriftGuardTest`), and it has caught it for real: repairing
# one `standards/` node left the packaged copies carrying the old text, and the
# `validate` lane went red on a PR that looked like a pure documentation change.
# This runs the same check before the push, so the red arrives sooner.
#
# WHY IT PACKAGES TO A TEMP FILE INSTEAD OF RUNNING `just knowledge-package`.
# That recipe WRITES both outputs in place. Doing that inside a pre-push hook
# would modify tracked files in the middle of a push — leaving the working tree
# dirty, or worse, writing content that differs from the commits being pushed
# while git is already reading them. A check that mutates what it is checking is
# not a check.
#
# `package.py --out` takes an explicit destination, so the packaging happens
# entirely in a temp directory and the comparison is read-only. Verified: the
# working tree is untouched afterwards (`git status --porcelain` stays empty).
#
# WHAT A FAILURE MEANS. Not that the corpus is wrong — that the committed
# derivative no longer matches it. The fix is always the same: run
# `just knowledge-package` and commit both outputs.

set -euo pipefail

root="$(git rev-parse --show-toplevel)"
cd "$root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

packaged="$tmp/packaged.json"

# Both default outputs are byte-identical (verified), so one packaging run
# serves both comparisons. If that ever stops being true this script would
# report a false failure rather than a false pass, which is the right direction
# to be wrong in.
python3 launchpad/project-intelligence/corpus/package.py --out "$packaged" >/dev/null

stale=()
for out in launchpad/crates/knowledge/generated/corpus.json \
           desktop/public/knowledge-corpus.json; do
  if [[ ! -f "$out" ]]; then
    stale+=("$out (missing)")
  elif ! cmp -s "$packaged" "$out"; then
    stale+=("$out")
  fi
done

if (( ${#stale[@]} )); then
  echo "corpus package drift — the committed output no longer matches the corpus:" >&2
  for s in "${stale[@]}"; do
    echo "  $s" >&2
  done
  echo >&2
  echo "Run 'just knowledge-package' and commit both outputs." >&2
  exit 1
fi

echo "corpus package is current (both outputs match a fresh packaging run)"
