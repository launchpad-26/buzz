---
name: review-queue-automation-onboarding
description: First-time setup for review-queue-automation in a repository —
  writes the starter <repo>/.rqa/config.json, or migrates an old-shape config
  in place. Never polls GitHub, never calls a model, never mutates a PR.
---

# Review-queue automation onboarding

Run this once per repository before the first `rqa tick` against it. It only
ever touches one local file.

## Invoke

```bash
python3 -m rqa.cli onboard <repo-path>
python3 -m rqa.cli onboard <repo-path> --migrate
```

`<repo-path>` is the repository's root. Both forms are read-only against
GitHub and against any model; they write exactly one file,
`<repo-path>/.rqa/config.json`.

## Plain mode

Writes the starter document — `rqa.policy.validate.starter_config()` — with
every `authority` entry `false`, no configured `routes`, `external.allowed`
`false`, no `policy.obligations`, and every `budget` axis unconfigured
(`null`). It refuses (`already_exists`, exit 1) if the file already exists;
onboarding never overwrites a config an operator may have started editing.

## Migrate mode (`--migrate`)

Converts an existing config at the same path into the current five-group
shape. **The source document must already carry `routes`, `external`,
`policy` and `budget` in their current shape** — `migrate_config` copies
those four through byte-for-byte unchanged (verified directly: a config
missing them fails validation after conversion exactly as it would have
before). Only `authority` is transformed, and only two other key families
are stripped:

- Drops the notification-transport keys and the retention-window key
  wherever nested (`rqa.policy.onboard._DROPPED_KEYS`).
- Rebuilds `authority`: `review`'s Boolean value carries through unchanged
  under the same key; `fix`'s Boolean value carries through unchanged under
  the renamed key `remediate`; `triage` is discarded with no replacement —
  the lane it gated is not carried forward by any name. Every entry the old
  shape never named at all — `comment`, `approve`, `request_changes`,
  `merge` — is zeroed `false` unconditionally: everything not previously
  live stays off.
- Re-validates the converted result before writing it.

A config from further back than this — one still carrying the pre-cutover
top-level keys (`version`, `login`, `state_dir`, `models.*`, `poll.*`, and
similar) rather than the five-group shape with old-style `authority` — is
**not** a supported migration source: those extra top-level keys survive
`migrate_config` unchanged and then fail `validate()`'s closed key set,
refusing the whole write as `migrated_config_invalid` (verified directly
against a document built with those keys). Reshape to the five groups by
hand first, or start from plain `onboard` and copy values across.

Refuses (exit 1) if there is nothing at that path to migrate
(`no_config_to_migrate`), the existing file is unreadable or not JSON
(`unreadable_existing`), or the converted document itself fails validation
(`migrated_config_invalid`, with the specific errors named).

## Completion condition

Exit `0` and `outcome: "written"` with the path of the file just created. A
refusal is `outcome: "refused"` with a `reason` naming exactly why — fix that
reason before retrying; onboarding never partially writes a config.

## Next step

Once onboarded, add the repository to `<state-dir>/repos.json` (or pass it
explicitly with `rqa tick --repo`) and see [OPERATORS.md](../OPERATORS.md)
for what each config group means and how the six dispositions and five
escalation causes surface once `rqa tick` starts running.
