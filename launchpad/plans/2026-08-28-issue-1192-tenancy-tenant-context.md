# Issue #1192 — layers/tenancy/tenant-context.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md`,
and `launchpad/docs/corpus/architecture/principles/host-selects-community.md` (id
`architecture-principles-host-selects-community`) are merged on `origin/launchpad`.
`launchpad/docs/corpus/layers/tenancy/tenant-context.md` does not exist yet, and neither does
the `layers/tenancy/` directory. Per-type templates exist under `launchpad/docs/corpus/templates/`
but none is named for the `layers` type, matching the pattern the sibling
`layers/tenancy/host-resolution.md` node (issue #1189, open PR #1839, not yet merged) already
used: write directly against `node.schema.json`. Sibling tenancy docs #1189/#1190/#1191 are all
still open, unmerged PRs (#1839, #1840, #1838) — their node ids are not valid `relationships`
targets from this node per AGENTS.md step 9.

STEP 1  Gather and verify evidence directly (not by report alone): read
`crates/buzz-core/src/tenant.rs` in full for `CommunityId`/`TenantContext`'s definitions,
derives, doc comments, and unit tests; read `crates/buzz-relay/src/tenant.rs` for
`bind_community`/`bind_deployment_community` construction and the `redteam_attack2` fail-closed
tests; grep and open the threading call sites across `router.rs`/`connection.rs` (WebSocket,
owned struct field), `api/bridge.rs` (REST, re-derived per handler), `api/git/transport.rs`
(`GitAuth` extractor), and `api/media.rs` (`AuthenticatedUpload`/`MediaReadAuth` extractors) to
confirm the threading pattern is not uniform across surfaces. Record
`git rev-parse HEAD`. ← RUNS HERE

STEP 2  [needs 1] Write front matter (schema-valid: id `layers-tenancy-tenant-context`, type
`layers`, status `draft`, origin `launchpad`, audiences `[agent, developer, reviewer]`, one
`references` relationship to `architecture-principles-host-selects-community`, confirmed present
on `origin/launchpad`) and the body: one-sentence definition, boundaries/non-goals (not host
resolution itself — that is the sibling node's subject — and not authorization/authentication
inside a bound request), the struct's shape and construction path, how it threads through each
surface (naming the non-uniformity honestly), representative read call sites, and its
relationship to `CommunityId`. One evidence entry per substantive claim, each opened in STEP 1.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and
re-run until exit 0.

STEP 4  [needs 3] Re-read the diff against every DoD checklist item in issue #1192 and against
`AGENTS.md`'s "Creating a node" procedure. Confirm every FACT citation was actually opened, no
second canonical document was created, and the scope section names both non-goals and the one
known gap (no relationship to the still-unmerged `host-resolution` sibling node).

STEP 5  [needs 4] Run the corpus unittest suite as the sole prior command to earn the
verification stamp, then commit the plan + document in a separate call, push, and open a draft
PR.

PARALLEL: none — single file, single task, evidence gathering feeds directly into the one body.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. No
`check-plan.sh` was found in this worktree (searched `launchpad/scripts/` and repo root);
proceeding without it per the task's own fallback. Verification here is self-review only — no
`review-code` skill invoked; `review-adjudicate` and the cross-model final review pass are
deferred to the batch owner's review before merge.

BUDGET: small — one document, no code changes; evidence gathering is bounded to two source files
(`buzz-core/src/tenant.rs`, `buzz-relay/src/tenant.rs`) plus roughly half a dozen call sites
across four HTTP/WS surfaces.

OPEN: Whether to add a `references` relationship to the sibling `host-resolution` node. Resolved
as **no** — its PR (#1839) is open, not merged, so its id does not resolve on `origin/launchpad`
and adding the edge now would be exactly the trap AGENTS.md step 9 names. This is named as a
follow-up in the body's scope section instead, once #1839 merges.

LEFT OUT: A `relationships` edge to the sibling tenancy nodes (`host-resolution`,
`multi-community-mode`, `single-community-mode`) — none exist on `origin/launchpad` yet. Any
change to `crates/buzz-core` or `crates/buzz-relay` source — this is a documentation-only task.
Restating `host-selects-community`'s full row-zero enforcement enumeration — linked, not
duplicated. A full per-surface conformance audit of every call site in the repo — the four
surfaces read here (WebSocket, REST/bridge, git-http, media) are representative, not exhaustive;
that gap is named in the body.
