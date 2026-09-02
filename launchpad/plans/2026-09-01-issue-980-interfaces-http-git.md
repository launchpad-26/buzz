Issue: launchpad-26/buzz#980 — interfaces/http/git corpus node (Feature #616)

Stated size: issue #980 carries no explicit Size label; the dispatching task instructions say this is a small single-document task -> cap: 5 steps

ALREADY TRUE

- `launchpad/docs/corpus/interfaces/http/git.md` does not exist (confirmed:
  `ls` on that path fails with "No such file or directory" at HEAD
  650354eab8d41ab6ce1a71de079a6c6d95c69052 in this worktree).
- `node.schema.json`'s `type` enum has `interfaces-events` as the single
  combined value for interface/event-kind-shaped nodes (confirmed by reading
  the schema and by `launchpad/docs/corpus/templates/interface.md`'s own
  "A note on `type`" section) — this is the value to use, not an invented one.
- `launchpad/docs/corpus/templates/interface.md` exists and defines the
  required body sections for an interface node: Interface description,
  Operations, Contract and stability, Boundary statement, Relationships,
  Scope and omissions.
- `launchpad/docs/corpus/architecture/flows/git-push.md`
  (id `architecture-flows-git-push`, status `draft`) already exists in this
  worktree's checkout of `origin/launchpad` and documents the push
  authentication/authorization/CAS flow in deep, verified detail. This node
  must not duplicate that content — it should `references` it and stay at
  the interface-boundary level (routes, auth mechanism, contract), leaving
  ordered-interaction detail to the flow node.
- The git smart-HTTP route table is fixed and small:
  `crates/buzz-relay/src/api/git/transport.rs::git_router` registers exactly
  three routes (`GET .../info/refs`, `POST .../git-upload-pack`,
  `POST .../git-receive-pack`); `crates/buzz-relay/src/api/git/mod.rs`
  additionally registers `POST /internal/git/policy` (loopback-only,
  internal hook callback, not part of the client-facing contract).
- Client-side auth tooling already has README-documented contracts:
  `crates/git-credential-nostr/README.md` (NIP-98 credential helper) and
  `crates/git-sign-nostr/README.md` (NIP-GS commit/tag signing, a separate
  concern from transport auth).
- No other corpus node under `interfaces/` exists yet — this will be the
  first instance of the interface template, matching that template's own
  "first sibling" expectation.

STEP 1 [independent]

Draft `launchpad/docs/corpus/interfaces/http/git.md` with schema-valid front
matter (`id: interfaces-http-git`, `type: interfaces-events`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer,
operator, reviewer]`) and a body following `templates/interface.md`'s
required sections:
- Interface description naming the boundary (git client <-> relay, HTTP +
  git smart-HTTP protocol + NIP-98 bearer auth).
- Operations table citing `transport.rs::info_refs`, `::upload_pack`,
  `::receive_pack`, each with its route and HTTP method, plus a note that
  `/internal/git/policy` is an internal-only callback, not a client-facing
  operation.
- Contract and stability: NIP-98 auth requirement (401 +
  `WWW-Authenticate: Nostr`), NIP-43 relay-membership gate, the read gate's
  fail-closed 404 semantics (`authorize_git_read`), 400/503/413/500 error
  codes from `transport.rs`, no-public-repos-for-v1 statement, and the
  gzip-decode/body-limit behavior.
- Authentication/authorization section covering the NIP-98 credential flow
  (`git-credential-nostr`), the repo-root URL scoping and method-skip
  rationale, and NIP-GS (`git-sign-nostr`) as a distinct, out-of-scope
  concern (object signing, not transport auth) — citing both crate READMEs.
- Boundary statement naming: not the git-push authorization/CAS flow's
  ordered interactions (owned by `architecture-flows-git-push`); not the
  object-store CAS internals; not the NIP-GS signing wire format.
- Relationships: `references: architecture-flows-git-push` (that id is
  present in this worktree's `origin/launchpad`-based checkout, so it
  resolves).
- At least one valid example (a successful `info/refs` + `git-upload-pack`
  clone, or a successful push) and one failure example (401 missing auth,
  or 404 fail-closed read denial), both citing the exact code path.
- Evidence ledger with one entry per claim, classes chosen honestly
  (FACT for opened sources, TEAM_KNOWLEDGE for issue-only claims), plus the
  mandatory commit-citation provenance entry for
  `650354eab8d41ab6ce1a71de079a6c6d95c69052` (recorded as of the start of
  this task; re-verify against `git rev-parse HEAD` at commit time and use
  the actual value if it has moved).

done when: `launchpad/docs/corpus/interfaces/http/git.md` exists, is valid
YAML+Markdown, and every bullet of issue #980's Definition-of-done checklist
has a corresponding section or evidence entry in the file (checked by
re-reading the file against the checklist line by line).

STEP 2 [needs 1]  <- RUNS HERE

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
repository root and fix every FAIL it reports (UNVERIFIED notices are
acceptable and expected for commit-citation and issue-attributed entries;
FAIL lines are not). Iterate until it exits 0.

done when: the command exits 0 and its output contains no line reporting a
schema violation, broken node id, invalid source path, or duplicate id for
`interfaces-http-git` or any other loaded node.

STEP 3 [needs 2]

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in its own tool call and confirm it prints `OK`. This is the commit gate; do not touch any stamp file and do not use `--no-verify` if the subsequent commit is rejected — that is a finding to report, not to route around.

done when: the unittest command's output contains the literal string `OK` on
its own status line, with zero failures/errors reported.

STEP 4 [needs 3]

Stage exactly the two files this task authored
(`launchpad/docs/corpus/interfaces/http/git.md` and this plan file) and
commit with `git commit -s -m "docs(corpus): document HTTP git
smart-transport interface (#980)"`.

done when: `git log -1 --format=%H` returns a new commit whose
`git show --stat` lists only those two files, and `git log -1` shows a
`Signed-off-by:` trailer.

STEP 5 [needs 4]

Self-review: re-read the committed diff against issue #980's
Definition-of-done checklist line by line, confirm every evidence entry's
cited source was actually opened during Step 1 (re-open any doubtful
citation), confirm no second hand-authored canonical corpus document was
created, and re-run `python3 launchpad/project-intelligence/corpus/validate.py`
to confirm it still exits 0 after the commit.

done when: every Definition-of-done bullet has been checked off against the
committed file's actual content, and `validate.py` exits 0 on the
post-commit tree.

PARALLEL

None. This is a single-document task with a strictly linear dependency
chain (draft -> validate -> gate -> commit -> review); nothing here is
independent of Step 1's draft.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
  (Step 2), the standard corpus-content gate that also runs in CI on any
  change under `launchpad/docs/corpus/`.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print `OK` (Step 3) — the commit gate named explicitly
  in the dispatching task instructions. If the subsequent `git commit -s`
  is rejected for a missing gate stamp, that is reported as a finding, not
  bypassed with `--no-verify` or a hand-edited stamp file.

BUDGET

Single document, five steps, no code changes, no test infrastructure to
stand up. Expected total effort: well under an hour of agent time —
evidence-gathering (already done during planning) plus one drafting pass,
one validation-fix loop, and one commit.

OPEN

- Whether `architecture-flows-git-push`'s `status: draft` (not `active`)
  affects the legality or wisdom of a `references` edge from this new node
  — `AGENTS.md`'s only stated rule is that the *target id* must resolve in
  the corpus at merge time, not that its status must be non-draft, so this
  plan proceeds on that reading; a reviewer may decide otherwise.
- Whether the exact wording of the "at least one failure example" bullet is
  best served by the 401-missing-auth path or the 404 fail-closed-read path
  — left to Step 1's author to choose whichever is more concretely citable
  once drafting starts.

LEFT OUT

- Documenting `/internal/git/policy`'s full HMAC/policy contract as a
  client-facing operation — it is loopback-only and internal to the push
  flow, already covered in depth by `architecture-flows-git-push`; this
  node only notes its existence and boundary, per the interface template's
  instruction not to duplicate a flow node's canonical content.
- Documenting NIP-GS (`git-sign-nostr`) commit/tag signing as a full
  contract in this node — it is an orthogonal, optional concern (signs git
  objects, not the HTTP transport), explicitly named as out-of-scope by
  `architecture-flows-git-push`'s own evidence ledger; this node cites it
  only to draw the same boundary, not to re-describe it.
- Filing any new GitHub issue for a second concept — none was discovered;
  the git smart-HTTP interface is one coherent boundary and fits one node.
- Opening a PR, pushing, or merging — issue #980's instructions are
  explicit that this task stops at a local commit on the worktree branch.
