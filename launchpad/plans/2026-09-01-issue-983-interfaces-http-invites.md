Issue #983 — interfaces-events corpus node: HTTP invites

Stated size: issue body carries no explicit Size line; task instructions cap this at 5 steps as a small single-document task -> cap: 5 steps

RUNS HERE: /home/serina/Launchpad/buzz/__worktrees/task-983-interfaces-http-invites

ALREADY TRUE

- `launchpad/docs/corpus/interfaces/http/invites.md` does not exist yet (`find launchpad/docs/corpus -name invites.md` -> no match; the `interfaces/` directory itself does not exist under `launchpad/docs/corpus/`).
- `node.schema.json`'s `type` enum has 13 members and the only interface-shaped value is `interfaces-events` (there is no `interfaces-http` or plain `interfaces` value) — confirmed by reading `launchpad/docs/corpus/schema/node.schema.json` directly.
- `launchpad/docs/corpus/templates/interface.md` (id `corpus-template-interface`) is the concrete authoring template for interface-shaped nodes: required sections are Interface description, Operations, Contract and stability, Boundary, Relationships, Scope and omissions. It states this template's own node carries `type: governance` (it documents corpus authoring rules) while an *instance* node built from it carries `type: interfaces-events`.
- At `origin/launchpad` HEAD `650354eab8d41ab6ce1a71de079a6c6d95c69052`, no `interfaces-events`-typed instance node exists anywhere in the corpus (only `templates/interface.md`, itself `type: governance`, and unrelated architecture/standards nodes). So there are zero valid `relationships[].target` ids for any interface-shaped or event-kind-shaped subject — this node will declare no `relationships`.
- A dedicated HTTP invites route group exists in code — it is not "invites are Nostr events only, no HTTP surface." Routes registered in `crates/buzz-relay/src/router.rs`: `POST /api/invites` (mint), `GET /api/join-policy`, `GET /api/join-policy/terms`, `GET /api/join-policy/privacy`, `POST /api/invites/accept-policy`, `POST /api/invites/claim`, plus `GET /invite/{code}` served as the SPA landing page (`is_invite_landing_path` in `router.rs`). Handlers live in `crates/buzz-relay/src/api/invites.rs`; token format/derivation lives in `crates/buzz-relay/src/invite_token.rs`; protocol constants (TTL bounds, v2 code shape) live in `crates/buzz-core/src/invite.rs`.
- Successful invite claims trigger NIP-43 side effects (`publish_nip43_member_added`, `publish_nip43_membership_list` in `crates/buzz-relay/src/api/invites.rs`), publishing `KIND_NIP43_MEMBER_ADDED` (8000) and `KIND_NIP43_MEMBERSHIP_LIST` (13534) events defined in `crates/buzz-core/src/kind.rs` — this interface spans those event kinds without owning their wire contract, so it may only `references` an event-kind node for them once one exists (none does yet).
- Both `/api/invites` and `/api/invites/claim` require NIP-98 signed auth (`authenticate()` in `invites.rs`, calling `bridge::verify_bridge_auth_with_options` + `bridge::check_nip98_replay`), tenant-bound via `crate::tenant::bind_community` on the `Host` header. This is Buzz-specific HTTP + NIP-98 (an existing NIP already implemented elsewhere in this repo), not a new invite-specific NIP — there is no NIP number for "invites" to link to.
- `python3 launchpad/project-intelligence/corpus/validate.py` and `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` are both runnable from repo root today (scripts exist per `launchpad/docs/corpus/AGENTS.md`).

STEP 1 [independent]

Draft `launchpad/docs/corpus/interfaces/http/invites.md` following `corpus-template-interface`'s required sections (Interface description, Operations, Contract and stability, Boundary, Relationships, Scope and omissions), front matter `id: interfaces-http-invites`, `type: interfaces-events`, `status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`, one `evidence` entry per substantive claim (commit citation for provenance; FACT entries citing opened source files/lines for mint/claim/accept-policy/join-policy/landing-page behavior, auth, rate limiting, NIP-43 side effects, error codes; no `relationships` per the ALREADY TRUE finding). Include at least one valid mint+claim example and one failure example (e.g. non-admin mint -> 403, invalid code claim -> 403 `invite_invalid`), sourced from the existing test assertions in `crates/buzz-relay/src/api/invites.rs`'s `#[cfg(test)]` module rather than invented.

done when: the file exists at that path, is the only new hand-authored `.md` file under `launchpad/docs/corpus/`, and every Definition-of-done bullet from issue #983 is addressed in its body (inputs/outputs/errors, auth/authz, versioning/ordering/idempotency, machine-spec link or explicit note that none exists beyond NIP-98, one valid + one failure example).

STEP 2 [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root. Fix any FAIL line attributable to the new node (schema violation, bad citation path, broken relationship). A FAIL not caused by this node's own content is treated as a discrepancy to report, not silently patched around.

done when: the command exits 0, with only UNVERIFIED notices (if any) printed — no FAIL lines.

STEP 3 [needs 2]

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in its own tool call and confirm it prints `OK`.

done when: the command's output ends with `OK` and a non-error exit status.

STEP 4 [needs 3]

Stage exactly `launchpad/docs/corpus/interfaces/http/invites.md` and this plan file, then commit with `git commit -s -m "docs(corpus): document HTTP invites interface (#983)"`. If the commit is rejected for a missing gate stamp, stop and report it as a finding rather than touching any stamp file or using `--no-verify`.

done when: `git log -1 --format=%H` on the current branch shows a new commit whose diff (`git show --stat HEAD`) touches only those two files, and `git rev-parse HEAD` differs from the branch's starting SHA `650354eab8d41ab6ce1a71de079a6c6d95c69052`.

STEP 5 [needs 4]

Self-review: re-read the committed diff against issue #983's Definition-of-done checklist line by line, re-open every cited file to confirm each evidence entry's `statement` is actually supported, confirm no second hand-authored canonical corpus document was created, and re-run `validate.py` to confirm it still exits 0.

done when: every DoD bullet is checked off against the actual diff text (not recalled from memory) and `validate.py` exits 0 on the final committed state.

PARALLEL

None of these steps are parallelizable against each other in practice (each STEP after 1 depends on the previous artifact existing), but STEP 1 is tagged `[independent]` because it depends on no other step in this plan — only on the research already captured in ALREADY TRUE.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before committing (STEP 2).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print `OK` before committing (STEP 3), run as the sole command in its own tool call per the task's explicit instruction.
- The repo's commit-time gate (whatever stamp/hook mechanism `git commit -s` triggers) must accept the commit in STEP 4; a rejection for a missing stamp is reported, not routed around.

BUDGET

One corpus Markdown file (~150-250 lines) plus this plan file. No code changes, no second corpus document, no PR opened, no push.

OPEN

- Whether a future `interfaces-events` node for kind:8000 (`KIND_NIP43_MEMBER_ADDED`) or kind:13534 (`KIND_NIP43_MEMBERSHIP_LIST`) should later `references` this node, or vice versa, is left for whichever task drafts that node — not decided here, since neither exists yet.
- Whether `/invite/{code}` (the SPA landing-page route, static-file serving rather than a JSON API) belongs inside this same interface node or is a distinct "invite landing page" concern is resolved in favor of including it as one operation of the same interface, since it is part of the same mint-then-claim invite flow and registered in the same route table; a reviewer disagreeing with that scoping call is free to say so.

LEFT OUT

- No second corpus document is created (e.g. a separate event-kind node for the NIP-43 side-effect kinds) — issue #983 scopes exactly one node, and any newly discovered second concept is explicitly out of scope per the issue's own "Out of scope" section.
- No runtime/product code changes — this is documentation only.
- No PR is opened, no push to origin, per the task's explicit instructions.
- No resolution of the corpus-wide "may a recorded revision stay put across edits" question (#1321) — not applicable, this is a brand-new node, not an update.
