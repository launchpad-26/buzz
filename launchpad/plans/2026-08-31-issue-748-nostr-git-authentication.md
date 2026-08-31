# Plan: issue #748 — document capabilities/git/nostr-git-authentication.md

## ALREADY TRUE

- Target file `launchpad/docs/corpus/capabilities/git/nostr-git-authentication.md` does not
  exist (confirmed by directory listing — no `capabilities/` tree exists under
  `launchpad/docs/corpus/` yet).
- `launchpad/docs/corpus/templates/capability.md` already merged to `origin/launchpad`
  (`type: capabilities`, required sections: Capability statement, Maturity, Boundary,
  Relationships, Scope and omissions).
- The server-side auth mechanism is real, shipped code:
  `crates/buzz-relay/src/api/git/transport.rs` (`GitAuth` extractor, NIP-98 verification,
  relay-membership gate, ban cascade, `authorize_git_read` channel-role gate) and
  `crates/buzz-relay/src/api/git/policy.rs` (pre-receive hook HMAC callback, push
  authorization via `buzz_core::git_perms::evaluate_push`).
- `buzz_auth::nip98::verify_nip98_event` (`crates/buzz-auth/src/nip98.rs`) implements NIP-98
  kind:27235 verification with a ±60s timestamp window.
- Two architecture nodes already merged that this node can `references` without duplicating:
  `architecture-flows-git-push` and `architecture-principles-signed-events`.
- No sibling capability nodes (#744 credential-helper, #745 git-hosting, #747 git-signing,
  #753 smart-http) are merged yet — per `AGENTS.md` step 9, no relationship may target them.

## STEP 1 — Draft the node

Write `launchpad/docs/corpus/capabilities/git/nostr-git-authentication.md` following the
`capability.md` skeleton: capability statement, maturity (shipped, cited to code + the
in-repo unit/e2e tests), boundary (not the push-authorization/protection-rule policy engine
itself — that is `git_perms::evaluate_push`'s own subject and belongs to a future push-policy
node; not credential-helper client tooling `#744`; not git hosting broadly `#745`; not commit
signing `#747`; not the smart-HTTP transport plumbing `#753`), relationships (`references`
`architecture-flows-git-push`, `architecture-principles-signed-events`), scope and omissions.
`id: capabilities-git-nostr-git-authentication`, `type: capabilities`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, operator, reviewer]`.

Done when: file exists, front matter matches `node.schema.json`, every FACT evidence entry
cites a real path I opened.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root. Confirm zero
new FAIL entries beyond the known 21 pre-existing baseline failures (issue #1951).

Done when: exit code and FAIL count confirm no new failures.

## STEP 3 — Earn the commit gate

Run, as the sole command in its own call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.

Done when: output ends `OK`.

## STEP 4 — Commit

`git add` the new doc + this plan file; `git commit -s` with message
`docs(corpus): document capabilities/git/nostr-git-authentication (#748)`.

Done when: commit exists on `task/748-nostr-git-authentication`, local only.

## STEP 5 — Self-review

Re-read the diff against #748's DoD line by line; re-open every cited source; confirm no
second canonical document was created; confirm no new validate.py FAIL entries.

## PARALLEL

None — single-file task, no sibling coordination needed within this task.

## GATES

- `validate.py` — zero new FAIL entries.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  — must print `OK` before commit.

## BUDGET

5 steps, capped per batch-run instructions.

## OPEN

- Whether a future push-authorization/protection-rules capability node (covering
  `git_perms::evaluate_push`, branch protection tags, role hierarchy) is a sibling task under
  #613 or folds into this node later — left as an explicit gap in *Scope and omissions*
  rather than guessed at.

## LEFT OUT

- Any edit to sibling capability files (#744/#745/#747/#753) — out of scope per #748's own
  Out of scope section.
- Any runtime code change — this is documentation only.
