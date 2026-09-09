# Plan: issue #1235 — document platforms/cli/authentication.md

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/cli/authentication.md` does not exist yet
  (confirmed by `test -f`).
- No `platforms/**` node is merged on `origin/launchpad` at the recorded
  revision (`cad6c375fdcc590158c1456c9fc7875f0f84a844`); sibling
  `platforms/agents/*` nodes exist only as local, unmerged commits from the
  same batch (e.g. `platforms-agents-kubernetes-backend`), establishing the
  `type: implementation`, `id: platforms-<path>` convention this node follows.
- `architecture-containers-cli` and `architecture-flows-websocket-authentication`
  (and `architecture-flows-http-event-submission`) already exist and resolve
  on `origin/launchpad`'s corpus tree, so `relationships` targeting them are
  safe to declare.
- `launchpad/docs/corpus/templates/component.md` is the fitting merged
  template (responsibility / public interface / dependencies / boundary /
  relationships / scope-and-omissions), already used by the sibling
  `platforms/agents/*` nodes for a single-crate or single-surface subject.

## STEP 1 — Draft front matter and body

Write `launchpad/docs/corpus/platforms/cli/authentication.md`:
`id: platforms-cli-authentication`, `type: implementation`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, reviewer]`. Cover
`buzz-cli`'s own authentication surface only (not the generic NIP-42/NIP-98
protocol mechanics, which the two `architecture/flows/*` nodes already own):
env vars (`BUZZ_PRIVATE_KEY`, `BUZZ_AUTH_TAG`, `BUZZ_RELAY_URL`), the
NIP-98-signed-HTTP-request path (`sign_nip98`), the NIP-42 WebSocket path
(`publish_ephemeral_event` → `buzz_ws_client::publish_event`), the NIP-OA
auth-tag injection/verification path, and the CLI's own auth error/exit-code
contract.

## STEP 2 — Evidence ledger

One evidence entry per substantive claim, each opened directly:
`crates/buzz-cli/src/lib.rs` (Cli struct, `run()`'s auth setup,
`normalize_auth_tag_input`, `secret_env_args_hide_their_values_in_help`),
`crates/buzz-cli/src/client.rs` (`sign_nip98`, `BuzzClient::sign_event`,
`with_auth_tag`, `publish_ephemeral_event`, retry-re-signs-per-attempt test),
`crates/buzz-cli/src/error.rs` (`CliError::Auth`/`Key`, `exit_code`,
`print_error`), `crates/buzz-cli/README.md`, `crates/buzz-cli/TESTING.md`,
`crates/buzz-sdk/src/nip_oa.rs` (`parse_auth_tag`/`verify_auth_tag`
doc comments). Record the recorded revision as a commit citation.

## STEP 3 — Relationships

Declare `part-of` → `architecture-containers-cli` (this node is a narrower
behavioral slice of that container) and `references` →
`architecture-flows-websocket-authentication` and
`architecture-flows-http-event-submission` (the generic protocol mechanics
this crate's two auth paths realize, without restating them).

## STEP 4 — Validate in isolation

Stash the new file, run `validate.py`, confirm the pre-existing 21-FAIL set
is unchanged, then restore the file and run it again to see only expected
`UNVERIFIED` notices (no new FAILs).

## STEP 5 — Commit

Run the corpus unit-test suite as the sole content of one Bash call, then
`git add` + `git commit -s` as a separate call.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` — zero new FAILs.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` — OK.
- Every DoD bullet in issue #1235 satisfied.

## OPEN

- Whether `architecture-containers-cli`'s existing claim that NIP-98 is
  "the CLI's sole authentication mode today" should be revised now that this
  node documents the WebSocket/NIP-42 path too — left as a disclosed
  discrepancy in this node's Boundary section rather than edited there,
  since editing a second canonical document is out of this issue's scope.

## LEFT OUT

- Full per-subcommand behavior of all 22 command groups (owned by future
  implementation-reference nodes, not this one).
- Restating the generic NIP-42/NIP-98 protocol mechanics already owned by
  the two `architecture/flows/*` nodes.
- Editing `architecture-containers-cli` to fix the "sole authentication mode"
  phrasing — out of scope for this task.
