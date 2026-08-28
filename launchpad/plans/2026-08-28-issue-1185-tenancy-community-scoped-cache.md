# Plan: issue #1185 — document layers/tenancy/community-scoped-cache.md

Parent PRD: #607. Corpus manifest alias: `DOC:layers/tenancy/community-scoped-cache.md`.

## ALREADY TRUE

- `launchpad/docs/corpus/layers/tenancy/community-scoped-cache.md` does not exist on
  `origin/launchpad` or in this worktree (checked with `test -f`).
- No open PR targets `task/1185-tenancy-community-scoped-cache` (fresh branch, just cut
  from `origin/launchpad` at `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`).
- `launchpad/docs/corpus/templates/concept.md` is merged and present on `origin/launchpad`.
  Its DoD-style shape (one-sentence definition, boundaries/non-goals, links to related
  concepts, examples that don't smuggle in a second concept) matches issue #1185's own
  Definition-of-Done checklist bullets almost verbatim, so `concept` is the template.
- Real source evidence already located: `crates/buzz-pubsub/src/{topic,publisher,
  presence,cache_invalidation,rate_limiter}.rs`, `crates/buzz-relay/src/state.rs`
  (moka caches + `invalidate_*`/`apply_cache_invalidation`), and `crates/buzz-core/src/
  tenant.rs` (`CommunityId`, `TenantContext`, the "fence" invariant).
- Related existing corpus nodes on `origin/launchpad` to link via `references`:
  `architecture-principles-community-is-security-boundary`,
  `architecture-principles-host-selects-community`, `architecture-containers-redis`,
  `architecture-deployment-multi-community`.

## STEP 1 — Build the node

Hand-author `launchpad/docs/corpus/layers/tenancy/community-scoped-cache.md` against
`node.schema.json` directly (no `scaffold.py` run available in this environment; write
front matter by hand following the schema and `concept.md`'s required-sections shape).

- Front matter: `id: layers-tenancy-community-scoped-cache`, `type: layers`,
  `status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`,
  evidence ledger with FACT entries citing the files above, `relationships` (all
  `references`) to the four ids listed above.
- Body: definition (one sentence up front), the two caching mechanisms (Redis
  key-namespacing for pub/sub + presence + rate limits; process-local moka caches keyed
  by `CommunityId` plus the Redis-broadcast cross-pod invalidation), boundary section
  distinguishing this from `architecture-deployment-multi-community` (deployment
  topology) and from the desktop's `resetCommunityState()` (client-side, out of scope —
  name it explicitly as a non-goal so a reader doesn't conflate the two), scope/omissions
  section per `AGENTS.md` step 8.

Done-when: file exists, front matter parses as YAML, every evidence statement is
supported by a citation I actually re-opened in this session.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the worktree root.
Done-when: exit 0.

## STEP 3 — Verify against DoD

Re-read the issue's Definition-of-Done checklist bullet by bullet against the drafted
file. Re-open every cited source file to confirm the citation supports its claim.
Confirm only one hand-authored corpus file was created.
Done-when: every DoD bullet is satisfiable by pointing at a specific section of the doc.

## STEP 4 — Test suite and commit

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` as the sole command in its own tool call. Confirm `OK`. Then, in a separate
call, `git add` the new file and the plan file, and `git commit -s`.
Done-when: commit created, working tree clean apart from expected files.

## STEP 5 — PR

Push the branch and open a draft PR against `launchpad` with `gh pr create --draft`,
stating `Closes #1185`, that `validate.py` and the unittest suite both passed, that
verification was self-review (no `review-code` skill invoked), and the deferred
cross-model/adjudication note.
Done-when: PR URL returned.

## GATES

- `validate.py` exit 0 (STEP 2, re-confirmed in STEP 3).
- Corpus unittest suite `OK` (STEP 4), run as the sole command in its own tool call,
  never combined with other commands.
- Every FACT/INFERENCE evidence entry cites a file actually opened this session.

## OPEN

- No corpus-plan manifest JSON is checked into the repo (it's an ephemeral input to
  `issue_plan.py`), so the task's `template`/`purpose`/`audiences` row fields are
  inferred from the issue body and `AGENTS.md`/`concept.md` rather than read from a
  ledger file. This is the same situation `AGENTS.md`'s "Absent altogether" template
  path anticipates, except here the template *is* merged — only the manifest row itself
  isn't retrievable. Documented as an inference, not silently assumed.

## LEFT OUT

- No second corpus document. Desktop's `resetCommunityState()` mechanism is explicitly
  named as out-of-scope/non-goal prose inside this node, not a second document and not a
  `relationships` edge (no corpus node for it exists on `origin/launchpad`).
- No changes to runtime product behavior.
- No broad corpus cleanup beyond this one file.
