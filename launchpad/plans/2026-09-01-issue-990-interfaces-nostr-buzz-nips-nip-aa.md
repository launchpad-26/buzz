Issue: launchpad-26/buzz#990 (parent: Feature #616)
Stated size: issue has no explicit Size line; task dispatch instructions cap this at 5 steps as a small single-document task -> cap: 5 steps

# Plan: interfaces/nostr/buzz-nips/nip-aa corpus node

ALREADY TRUE

- Target file `launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-aa.md` does not
  exist anywhere in this worktree or on `origin/launchpad` — confirmed via
  `find launchpad/docs/corpus -maxdepth 3 -type d` (no `interfaces/` directory at
  all) and `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`
  (94 files, none under `interfaces/`). This is a creation, not an update.
- `docs/nips/NIP-AA.md` exists at repo root and is the authoritative spec text
  (draft/optional/relay, depends on NIP-OA, NIP-43, NIP-42).
- `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum has 13 members;
  the correct value for an interface-shaped node is the single combined token
  `interfaces-events` (confirmed by `launchpad/docs/corpus/templates/interface.md`'s
  own "A note on `type`" section, which every interface-shaped node in this corpus
  is expected to follow).
- `launchpad/docs/corpus/templates/interface.md` exists and specifies required
  sections (Interface description, Operations, Contract and stability, Boundary,
  Relationships, Scope and omissions) — no separate template needs inventing.
- The relay-side implementation of NIP-AA's connection-admission algorithm is
  real and was read in full: `crates/buzz-relay/src/handlers/auth.rs` (NIP-42 AUTH
  handler, `extract_auth_tag_json`), `crates/buzz-relay/src/api/mod.rs`'s
  `pub mod relay_members` (`check_relay_membership`, `enforce_relay_membership`,
  `extract_nip_oa_owner`, `materialize_nip_oa_owner`), `crates/buzz-sdk/src/nip_oa.rs`
  (`compute_auth_tag`/`verify_auth_tag`/`parse_auth_tag`), `crates/buzz-auth/src/nip42.rs`
  (`verify_nip42_event`, ±60s freshness), and `crates/buzz-relay/src/config.rs`
  (`require_relay_membership`, `allow_nip_oa_auth` config flags).
- No source in this repository labels that code "NIP-AA" by name (grep for
  `NIP-AA` across `*.rs`/`*.md` hits only `docs/nips/NIP-AA.md` itself,
  `docs/remote-agents.md:53` and `launchpad/docs/corpus/templates/specification.md`,
  none of which name the implementing symbols) — the match between spec and code
  is this task's own inference, to be recorded as `INFERENCE` with `confidence`,
  not `FACT`.
- A closely related corpus node already exists and was read in full:
  `launchpad/docs/corpus/architecture/flows/websocket-authentication.md`
  (id `architecture-flows-websocket-authentication`, type `architecture`). It
  documents the same `handle_auth` code path end-to-end and explicitly lists
  "NIP-OA's full owner-delegation and attestation format... Not yet in this
  corpus" as a named gap — the new node fits that gap without duplicating the
  flow node's step-by-step mechanics; it `references` that node instead.
- Two concrete divergences between spec text and code were found and must be
  recorded honestly rather than smoothed over: (1) `buzz_sdk::nip_oa::verify_auth_tag`
  validates `conditions` syntax only and never evaluates `created_at<`/`created_at>`
  clauses against the AUTH event's `created_at` (spec Step 4.9) — no caller in
  `crates/buzz-relay` or `crates/buzz-auth` does this evaluation either; (2) spec
  Step 1 failures are supposed to get an `"invalid: <reason>"` OK-false prefix, but
  `handle_auth`'s crypto/challenge failure path sends `"auth-required: verification
  failed"` instead — only the membership-gate failure path actually uses the
  `"restricted: <reason>"` prefix the spec specifies for Steps 3-5.

STEP 1 — Draft the corpus node <- RUNS HERE [independent]

Write `launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-aa.md` following
`templates/interface.md`'s required sections, with:
- Front matter: `id: interfaces-nostr-buzz-nips-nip-aa`, `type: interfaces-events`,
  `status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`,
  a commit-citation evidence entry for the recorded revision, and one evidence
  entry per substantive claim (spec content as `FACT` citing `docs/nips/NIP-AA.md`
  line ranges; code behavior as `FACT` citing the specific `.rs` files/lines read
  in ALREADY TRUE; the spec-to-code correspondence itself as `INFERENCE` with
  `confidence`; the two named divergences as `FACT`, since both were directly
  observed by reading the cited code).
- Body sections per the template: Interface description (NIP-42 AUTH extended by
  NIP-OA owner delegation), Operations (the AUTH event as the sole operation,
  pointing at `handlers/auth.rs::handle_auth` and the relay-membership helpers),
  Contract and stability (the config flags, the OK-prefix behavior including the
  two divergences, freshness window, self-attestation rejection, no persistent
  membership record), Boundary (excludes NIP-OA's own credential format/minting —
  that belongs to a future NIP-OA node — and excludes NIP-42's own generic
  challenge/response mechanics, which `architecture-flows-websocket-authentication`
  already owns), Relationships (`references` toward
  `architecture-flows-websocket-authentication`; no relationship toward any NIP-OA
  or NIP-43 corpus node since none exists yet on `origin/launchpad`), Scope and
  omissions (per-event `kind=` enforcement not found in code; session-revalidation
  and session-enumeration-by-owner not found in code — name both as gaps, not
  silently dropped).
- At least one valid-auth example and one rejection example, grounded in the
  spec's own Verification Examples section and cross-checked against what the
  code actually does at each step (not copied from the spec unchecked).
done when: the file exists at the exact path, `head -40` shows valid YAML front
matter with `type: interfaces-events`, and every one of the issue's Definition-of-done
bullets (inputs/messages, outputs/responses, error/rejection, auth/authz,
versioning/compatibility, ordering/idempotency where applicable, spec link, one
valid + one failure example) has a corresponding section in the body.

STEP 2 — Validate the corpus [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo
root of this worktree.
done when: the command exits 0, and any printed `FAIL` line names a node other
than the new one (a `FAIL` on the new node means STEP 1 is not actually done and
must be fixed before proceeding — this is not a step that tolerates a red run).

STEP 3 — Earn the commit gate and commit [needs 2]

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
-p "test_*.py"` alone in its own shell call and confirm it prints `OK`. Then, in a
separate call, `git add` the new corpus node and this plan file, and
`git commit -s -m "docs(corpus): document Buzz NIP-AA interface (#990)"`.
done when: the test command prints `OK`, and `git log -1 --format=%H` after the
commit differs from the pre-commit `HEAD` (i.e. the commit was created, not
rejected by the pre-commit/pre-push gate). If the commit is rejected for a
missing gate stamp, that is a finding to report, not a reason to touch the stamp
file or pass `--no-verify`.

STEP 4 — Self-review against the issue's own checklist [needs 3]

Re-read the committed diff line by line against issue #990's Definition-of-done
checklist and re-open every cited source to confirm the evidence entry it
supports actually says what the statement claims (not merely that the path
resolves).
done when: every DoD bullet has been checked off against the actual file content
(not assumed), every `FACT`/`INFERENCE` evidence entry's cited source was
re-opened during this step, and `validate.py` still exits 0 after re-running it.

PARALLEL

None. This is a single-document task with one file to write, validate and
commit; every step needs the previous one's output (the plan cap is 5 and only
4 are used, so there is no batch of independent steps to parallelize).

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before
  committing (STEP 2).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
  "test_*.py"` must print `OK` before committing (STEP 3) — this is the commit
  gate the repo's own hooks/tooling expect; it is not optional and is never
  bypassed with `--no-verify`.
- The commit itself must carry `-s` (DCO sign-off), per this fork's root
  `CLAUDE.md`/AGENTS.md convention.

BUDGET

One corpus Markdown file (`nip-aa.md`) plus this plan file. No code changes,
no second hand-authored corpus document, no changes to generated indexes (none
exist to regenerate for this addition). Expected total: 2 files touched, 1
commit.

OPEN

- Whether the two spec/code divergences found (created_at-clause evaluation
  never happening; Step-1 failures using the generic NIP-42 `"auth-required"`
  prefix instead of the spec's `"invalid:"` prefix) warrant a follow-up
  implementation issue is **not** this task's call — the issue's own "Out of
  scope" explicitly excludes "changing runtime product behavior unless a
  separately linked implementation issue owns that change." This plan records
  them as documented facts in the node's evidence ledger and, if still
  unaddressed after STEP 4, as a candidate for a separately filed issue, but
  does not fix them.
- Whether a future dedicated NIP-OA corpus node should be the `references`
  target once it exists (it does not exist on `origin/launchpad` today) is left
  for whoever authors that node.

LEFT OUT

- Re-implementing or correcting the relay's created_at-clause enforcement gap —
  explicitly out of scope per the issue body ("Out of scope: Changing runtime
  product behavior unless a separately linked implementation issue owns that
  change").
- Adding a `relationships[].target` to any NIP-OA/NIP-43/NIP-IA corpus node —
  none of those exist yet on `origin/launchpad`'s corpus tree, so per
  `AGENTS.md`'s own rule ("check against the merge base... None is a valid
  answer") no such edge is added.
- A second template or standards document for interface-shaped nodes — one
  already exists (`templates/interface.md`) and is used as-is.
