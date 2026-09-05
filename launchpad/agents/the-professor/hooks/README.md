# Scheduled scanning

Two mechanisms for triggering `scan-repo` on an interval, not a new scheduler — see
`launchpad/Research/the-professor-skill-suite-redesign.md` §7 for the full reasoning.
Pick based on where the target repo runs, not on preference: the two aren't
interchangeable defaults, they cover different situations.

## Primary: GitHub Actions cron, in the target repo

`scheduled-scan.workflow.yml.template` in this directory is a **template**, meant to
be copied into the *target* repo's own `.github/workflows/` — it is not a workflow
that runs against this fork (`block/buzz`/`launchpad`). The Professor is meant to be
pointed at arbitrary repos, and most of them are not this one.

Copy it, rename it to whatever this fork's own convention would suggest for that
repo, and adjust:

- The `cron` expression — the template defaults to daily; capability 5 asks for
  "daily (or configurable-interval)," so the interval is the one line a target repo's
  maintainers are expected to change for their own needs.
- The checkout/auth steps — the template assumes the workflow runs inside the repo it
  scans (the common case) and needs no cross-repo credential; adjust only if this
  suite's pack itself needs to be fetched from elsewhere as part of the job.

This is the portable default specifically because it requires no live session or
account to keep firing — unlike the alternative below, a GitHub Actions cron trigger
keeps running whether or not anyone is watching.

## Alternative: an interactive harness's own scheduler

For a target repo with no CI, or while developing against this fork itself, the same
`scan-repo` invocation can be scheduled through whatever recurring-task mechanism the
harness in use already provides (a cron-scheduled agent run, or a session-level
interval loop), instead of standing up a GitHub Actions workflow for it. This requires
a live session or account to keep the schedule alive — it is the fallback, not the
default, for exactly that reason.

## Optional fast-path: a target repo's own post-commit hook

Not required, and never a replacement for either mechanism above — a hook only fires
for commits made through it, so it misses rebases, force-pushes, and any commit made
before the hook was installed. For a target repo that already runs a git-hooks
manager, a post-commit hook calling `scan-repo --since <the commit just made>` gives
near-real-time gap detection between scheduled sweeps. Purely additive.
