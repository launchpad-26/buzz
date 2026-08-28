# PROVENANCE — what is real in this directory

This directory holds #287 STEP 6's fixtures: the real double-block comment
sets from PR #261 and PR #264, named as the production evidence behind the
Option-B decision recorded in `ADJUDICATION.md`'s "PR comment verdict
blocks: refusing more than one (#287)" section.

## What is here, and where it came from

`recordings/pr-261-comments.json` and `recordings/pr-264-comments.json` each
hold exactly the two comments ADJUDICATION.md names for that PR — `id`,
`created_at`, `user.login`, and the full raw `body`, unmodified from what
`gh api repos/launchpad-26/buzz/issues/<n>/comments --paginate --slurp`
returned. No finding text, row, or severity in either file was typed by
hand: both are `gh api` output, filtered down to the two named comment ids
and re-serialised with `json.dumps(..., indent=2)`.

| file | PR | comment ids kept |
|---|---|---|
| `recordings/pr-261-comments.json` | #261 | `5364185647`, `5364261676` |
| `recordings/pr-264-comments.json` | #264 | `5364221899`, `5364504768` |

## How the test suite uses them

`test_verdict_resolution.py` loads these two files directly (no network) and
runs them through `pr_comments.from_items` — the same per-comment tagging
`pr_comments.fetch_and_locate` performs on a live fetch, just without the
`gh api` call — followed by `verdict_resolution.resolve`. The real
`verdict_blocks.locate_verdict_blocks` locator and `verdict_resolution.resolve`
resolver run unmodified against this recorded, real input; nothing about the
resolution logic is faked for the test.

## Regeneration

`python3 generate.py` from this directory re-fetches both PRs live and
reproduces the committed files. It failed the first time this was run only
in the sense that it succeeded identically — `git diff` against the
hand-fetched originals this file's history started from was empty, which is
what makes "wrote pr-261-comments.json (18843 bytes)" a check that the
committed bytes are still exactly what the live API returns, not merely a
claim.

Unlike `fixtures/adjudication/`'s generator, this one has no nonce to pin —
these are raw comment bodies, not a document built from a seeded pipeline —
so reproducibility here means the *filtered comment set* is stable, not that
every byte is deterministic across different points in time: if either
comment were ever edited on GitHub, a re-run would pick up the edit. That
has not happened as of this recording (2026-08-27); if it ever does, a
re-run and re-commit is the correct response, not a workaround.
