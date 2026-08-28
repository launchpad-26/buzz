---
name: review-queue-automation-onboarding
description: First-time setup for review-queue-automation in a repository. Creates
  the git-ignored local config at <repo>/.review-queue-automation/config.json and
  the default "pr review logs" directory, validates ignore rules and permissions,
  and prints the exact next safe command. Never polls GitHub, claims leases,
  invokes models, or mutates a PR.
---

# Review-queue automation onboarding

Sets up one repository to be managed by `review-queue-automation`. Run this once
per repo before any dispatch. It only ever touches local files — no GitHub, no
models, no leases, no PR mutations.

## Invoke

```bash
python3 ~/my-skills-library/prod/review-queue-automation/scripts/onboarding.py init <repo-root> --slug OWNER/REPO --base launchpad
```

`<repo-root>` is the absolute path to the repository. `--slug` and `--base` are
plain config values; if you omit them they default to empty/`launchpad`.

## What it does (in order)

1. Confirms `<repo-root>` is a directory and a git work tree (`git rev-parse`).
2. Loads and validates any existing local config; refuses to overwrite a config
   that is already tracked or not git-ignored.
3. Ensures `.review-queue-automation/` is in `.gitignore` (appends if missing).
4. Defaults the logging directory to `<repo>/pr review logs` and ensures that path
   is also git-ignored.
5. Collects only non-secret settings: repo slug, base branch, root path, optional
   preflight path, logging directory, model defaults, concurrency/canary settings.
   No secrets or tokens are ever written.
6. Creates `<repo>/.review-queue-automation/config.json` and the logging directory.
7. Validates the written config: JSON parses, required keys present, repository root
   exists, log dir writable, ignore rules hold.
8. Prints a concise setup summary and the exact next safe command
   (`dispatcher.py sweep`).

## Completion condition

The printed summary shows `"ok": true` and both `ignored_config_dir` and
`ignored_log_dir` are `true`. The config file exists and is untracked.

## Also available

```bash
# Read-only status check of an existing repo-local config
python3 .../onboarding.py check <repo-root>
```

Never invoke models, poll GitHub, claim a lease, approve a canary, or write to a
PR. If `onboarding` errors, fix the stated reason; do not bypass the ignore or
tracking checks.
