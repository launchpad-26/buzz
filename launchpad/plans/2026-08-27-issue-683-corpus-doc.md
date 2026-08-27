# Plan: issue #683 — corpus doc `architecture/flows/media-upload.md`

ALREADY TRUE: node.schema.json and launchpad/docs/corpus/AGENTS.md are merged on
origin/launchpad (confirmed at a44cf52fc740ebebbdd671427480d14f0bce0115); target file
`launchpad/docs/corpus/architecture/flows/media-upload.md` does not exist yet.

STEP 1 — Gather evidence: read the upload handler (`upload_blob`), the auth extractor
(`AuthenticatedUpload::from_request_parts`), Blossom auth verification
(`verify_blossom_auth_event_for_verb`, `verify_blossom_upload_auth`), the buffered
upload pipeline (`process_buffered_upload`), the video streaming pipeline
(`process_video_upload`), the serving-write deletion fence (`ServingWriteGuard`), the
error-to-status mapping (`MediaError::into_response`), and the e2e/unit tests that
exercise this flow. RUNS HERE.

STEP 2 — Write front matter (id `architecture-flows-media-upload`, type
`architecture`, status `draft`, origin `launchpad`, audiences `agent`+`developer`) and
body: trigger/preconditions/termination, ordered interactions with data/state
movement, auth/trust-boundary crossings, failure/abort/rollback behavior with linked
verification, and a scope-and-omissions section naming what was expected but not
verified (no relationships — no sibling flow/architecture node is merged on
origin/launchpad to point at).

STEP 3 — Validate: `python3 launchpad/project-intelligence/corpus/validate.py` must
exit 0.

STEP 4 — Commit: run the corpus unittest suite as the sole prior command to earn the
verification stamp, then stage and commit the plan + doc in a separate call.

PARALLEL: none — single file, single task in this worktree.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` (must exit 0) and
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` (must report OK) before commit. review-adjudicate and the cross-model
final-review pass are deferred to the batch owner's morning review — not run here.

BUDGET: single sitting, ~30-45 minutes of agent time — one document, no code changes.

OPEN: the issue's DoD asks for "typed relationships appropriate to the node," but
AGENTS.md is explicit that a relationship target must already exist as a merged node
on the branch being merged into. At the moment this node was written, two sibling
`architecture/flows/*` nodes (`architecture-flows-http-event-submission`,
`architecture-flows-huddle-audio`) exist as files on disk from sibling batch tasks but
had not been confirmed merged to `origin/launchpad` at this worktree's base revision —
checked directly (`git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus`) rather than assumed, per AGENTS.md's "check before you
justify it" rule. This document declares no relationships and states the check result
in its own scope section rather than silently resolving the ambiguity.

LEFT OUT: no per-type template exists (0/26 merged per the issue); this document is
authored directly against node.schema.json, as AGENTS.md instructs, and is expected to
be reshaped by a later templating task. No runtime/product behavior is changed.
