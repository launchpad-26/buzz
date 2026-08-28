# Plan: issue #677 -- corpus doc `architecture-flows-git-push`

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and
`launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad`
(confirmed by reading both at HEAD `a44cf52fc740ebebbdd671427480d14f0bce0115`);
`launchpad/docs/corpus/architecture/flows/git-push.md` does not exist yet
(confirmed with `test -f`).

STEP 1: Gather evidence -- read the git smart-HTTP push path in
`crates/buzz-relay/src/api/git/{transport,policy,binding,cas_publish,hook}.rs`,
the permission model in `crates/buzz-core/src/git_perms.rs`, and the client-side
credential helper (`crates/git-credential-nostr/README.md`). Identify the
representative e2e coverage (`crates/buzz-test-client/tests/e2e_git.rs`).

STEP 2: Write front matter (id `architecture-flows-git-push`, type
`architecture`, status `draft`, origin `launchpad`) and a body covering: trigger
and preconditions, ordered interactions (auth -> hydrate -> hook install ->
receive-pack -> pre-receive policy callback -> CAS publish -> derived
kind:30618), the NIP-98 trust-boundary crossing and the localhost-only
HMAC-bound hook callback, and failure/abort/rollback behavior (denied push
publishes nothing; CAS conflict; resource-limit and manifest-invalid paths),
each linked to `e2e_git.rs`'s two representative tests. No `relationships` --
no other flow/architecture node is confirmed merged on `origin/launchpad` at
this revision.

STEP 3 (RUNS HERE): Run
`python3 launchpad/project-intelligence/corpus/validate.py` until it exits 0
against the full tree including the new file.

STEP 4: Run the corpus unittest suite as the sole prior command to earn the
verification stamp, then commit the plan + document in a separate call, push,
and open a draft PR.

PARALLEL: none -- single hand-authored file, single worktree.

GATES: `validate.py` must exit 0 locally before commit. The corpus unittest
suite (`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
-p "test_*.py"`) is run once, alone, to earn the commit's verification stamp.
`review-adjudicate` and the cross-model final-review pass are explicitly
deferred to the batch owner's morning review -- not run in this task.

BUDGET: single document, one focused RepoQL exploration pass plus direct file
reads of the git push transport/policy/permission code -- no multi-step build,
no code changes.

OPEN: the issue's DoD asks for "typed relationships appropriate to the node."
At this revision no sibling flow/architecture corpus node is confirmed merged
on `origin/launchpad` (the batch's 47 other nodes are being authored in
parallel worktrees and are not yet on the target branch), so no relationship
target can be confirmed to resolve. The document declares no `relationships`
and states this explicitly as a real ambiguity rather than guessing at an edge
that might not exist when this PR lands. There is also no NIP-GS
(`git-sign-nostr`) corpus node yet to link from "related concepts" -- object
signing is a related but separate concern from the push-transport flow this
node documents, and is named as an explicit non-goal rather than folded in.

LEFT OUT: no runtime commands are executed (no relay/Postgres/Redis started);
all claims are sourced from reading the current source tree and its own unit/
e2e test files, not from running them. No second canonical document is
created. No template is invented -- the body is written directly against
`node.schema.json` per `AGENTS.md`'s explicit instruction.
