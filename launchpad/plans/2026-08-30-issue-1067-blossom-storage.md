Issue: launchpad-26/buzz#1067 — document layers/data/object-storage/blossom-storage.md
Stated size: not labelled in the issue; task brief caps this at 5 steps for one small document -> cap: 5 steps

ALREADY TRUE

- `launchpad/docs/corpus/architecture/containers/object-storage.md` (id
  `architecture-containers-object-storage`, type `architecture`, status
  `draft`) already exists on `origin/launchpad` and documents the shared
  S3-compatible bucket container: `buzz-media`'s ownership of the media half,
  the key taxonomy (blob/thumb/sidecar/auxiliary/unknown), Blossom BUD-11
  auth, content validation, and the git-on-object-storage sibling that shares
  the same bucket. This node is a legal `relationships` target (confirmed via
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`).
- `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum is
  `architecture, layers, capabilities, platforms, implementation,
  interfaces-events, verification, operations, development, release,
  governance, agent, ingestion`. The issue's own target path is
  `layers/data/object-storage/blossom-storage.md`; `layers` is the matching
  enum member — issue #602 (parent PRD) lists `layers` as one of the
  corpus's own in-scope surfaces, distinct from `architecture`.
- `launchpad/docs/corpus/templates/datastore.md` exists and is the shape to
  follow: Purpose & scope, Technology & attachment profile, Schema/namespace
  inventory, Migration/versioning mechanism, Access-pattern summary,
  Operational characteristics, Scope and omissions.
- Target file `launchpad/docs/corpus/layers/data/object-storage/blossom-storage.md`
  does not exist (`test -f` returned false; no `layers/` directory exists yet
  under `launchpad/docs/corpus/`).
- `crates/buzz-media` is the code that owns Blossom media storage:
  `storage.rs` (S3 client wrapper: put/put_file/get/get_range/get_stream/head/
  delete/delete_objects/get_sidecar/put_sidecar/list_page), `config.rs`
  (`MediaConfig`), `auth.rs` (BUD-11 kind:24242 verification), `validation.rs`
  (magic-byte MIME sniffing), `bucket_index.rs` (key-class taxonomy:
  thumb/blob/sidecar/auxiliary/unknown), `upload_record.rs` (optional
  moderation side-channel).
- No SQL migration under `migrations/` mentions media (`grep -rl media
  migrations/*.sql` -> no hits): Blossom storage has no Postgres schema of
  its own; its "schema" is the bucket key-naming convention in
  `bucket_index.rs`.
- `crates/buzz-deletion` ("Durable whole-community deletion engine for Buzz")
  is the only caller of `MediaStorage::delete_objects` outside tests
  (`crates/buzz-deletion/src/lib.rs:1140`), performing bulk, idempotent,
  manifest-driven deletion after a write-drain fence, and treats a non-empty
  `versioned_keys` result (bucket versioning enabled) as a permanent failure
  because it blocks true deletion.

STEP 1 [independent] — Confirm the plan against check-plan.sh <- RUNS HERE
Run `/home/serina/.claude/skills/plan-issue/check-plan.sh` against this file
from the worktree root.
done when: the script exits 0, or its findings are folded back into this
document before drafting begins.

STEP 2 [needs 1] — Draft the corpus document
Create `launchpad/docs/corpus/layers/data/object-storage/blossom-storage.md`.
Front matter: `id: layers-data-object-storage-blossom-storage`,
`type: layers`, `status: draft`, `origin: launchpad`,
`audiences: [agent, developer, operator]`, one `evidence` entry per
substantive claim (FACT for opened sources, INFERENCE with confidence for
reasoned claims). One `relationships` entry: `part-of` ->
`architecture-containers-object-storage`.
Body sections, per the datastore template adapted to the issue's DoD
bullets: Purpose & scope (names the container this zooms into; media-only,
not the git-CAS half); store classification (authoritative — sole durable
copy of blob bytes, not cache/derived/transport); technology & attachment
profile (link, do not repeat, the container node's S3/`BUZZ_S3_*` detail);
key-namespace inventory (the five classes from `bucket_index.rs`);
migration/versioning (no schema tool; key-shape changes are code changes to
`classify_key`); access-pattern summary (`buzz-media`'s client methods, the
storage sweep's read-only listing, `buzz-deletion`'s bulk delete path);
lifecycle/retention (create-only, content-addressed, no TTL, deletion is
whole-community only via `buzz-deletion`); tenancy/security boundaries
(community-scoped keys via `CommunityId`, BUD-11 auth, IAM-only bucket
access); failure behavior (bucket-versioning-blocks-deletion permanent
failure, `BUZZ_STORAGE_METRICS=off` kill switch, fail-closed IP capture);
scope and omissions (defers git-CAS half and protocol detail to the
container node; names unverified gaps, e.g. whether production enables S3
bucket versioning).
done when: the file exists and every Definition of Done bullet in issue
#1067's body is satisfied by some section of it.

STEP 3 [needs 2] — Validate
Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
worktree root. Fix and re-run until it exits 0.
done when: the validator exits 0.

STEP 4 [needs 3] — Earn the commit gate, then commit
Run `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole
command in its own tool call; confirm it reports OK. Only then stage and
commit the plan and the new document with `git commit -s`.
done when: the test run reports OK and the commit exists on
`task/1067-blossom-storage`.

STEP 5 [needs 4] — Self-review
Re-read `git diff origin/launchpad -- .` against issue #1067's Definition of
Done checklist, line by line. Confirm no second hand-authored canonical
document was created, every evidence entry supports its claim, and
`validate.py` still exits 0.
done when: the diff has been checked against every DoD bullet and no gaps
remain unnoted.

PARALLEL

None of the above steps are mutually parallel — each step's `[needs N]` tag
names the one step it depends on, and this is a single-file document with no
independent sub-work to split off.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
  before commit (STEP 3).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
  -p "test_*.py"` must report OK before commit, run as the sole command in
  its own tool call (STEP 4).

BUDGET

One corpus document, one plan file, one commit (a second small commit only if
a post-commit fix is needed and `--amend`/`reset --soft` is blocked by
`git-safety.sh`). No push, no PR — a later orchestration step bundles this
branch with its batch siblings.

OPEN

- Whether `type: layers` (this plan's choice, driven by the issue's own
  target path) or `type: architecture` (the datastore template's own default
  reasoning for a real datastore instance, written before any `layers/`-housed
  node existed) is the corpus's eventual settled convention for a node shaped
  like this one — not resolved by this task. The issue's literal target path
  is treated as authoritative, per the task brief's instruction that the
  issue is the input, not the parent Feature/PRD. A builder must not
  second-guess this by switching to `architecture` on their own judgement.
- Whether production/staging enables S3 bucket versioning (which would block
  `buzz-deletion`'s bulk delete) was not established — named as a gap in the
  document body, the same way the container node already names staging
  provisioning as unverified.

LEFT OUT

- Re-documenting the git-on-object-storage half of the shared bucket —
  owned by the existing container node and `docs/git-on-object-storage.md`;
  out of scope per the issue's own Objective (media/Blossom only).
- Any change to corpus generated indexes beyond what `validate.py` itself
  requires — none expected, since this is a plain content addition.
- A second corpus document — this task authors exactly one, per the issue's
  own Definition of Done.
- Pushing the branch or opening a PR — explicitly reserved for a later
  orchestration step per the task brief.
