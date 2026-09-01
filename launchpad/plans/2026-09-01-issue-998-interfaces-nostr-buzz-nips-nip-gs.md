Issue #998 — task: document interfaces/nostr/buzz-nips/nip-gs.md
Stated size: single hand-authored document, dispatch instructions cap at 5 steps -> cap: 5 steps

ALREADY TRUE
- `docs/nips/NIP-GS.md` exists at this worktree's HEAD (650354eab8d41ab6ce1a71de079a6c6d95c69052)
  and is the authoritative NIP-GS spec text: signature format, signing/verification
  procedure, status-line formats, key loading, CLI interface, test vectors, invalid
  cases, and security considerations.
- `crates/git-sign-nostr/src/lib.rs` (2508 lines) implements the spec: `parse_args`
  (CLI arg parsing incl. `--status-fd`, `-bsau`, `--verify`), `compute_signing_hash`,
  `do_sign`/`do_verify`, `parse_envelope`/`validate_hex_field` (envelope validation),
  `load_key`/`load_auth_tag` (key + NIP-OA auth tag loading), `verify_oa` (NIP-OA
  verification), `determine_trust`, and `run()` (exit code 0 on success, 1 on any
  `Error::Fatal` or `Error::VerifyFailed`). 56 `#[test]` functions include
  `test_signing_hash_matches_spec` and `test_signing_hash_with_oa_matches_spec`,
  which assert against the exact hex values published in NIP-GS.md's Test Vectors
  section.
- `crates/git-sign-nostr/README.md` documents the git config wiring
  (`gpg.format x509`, `gpg.x509.program`, `user.signingkey`) and the two invocation
  shapes (`-bsau` for sign, `--verify ... -` for verify), consistent with the spec's
  CLI Interface section.
- `launchpad/docs/corpus/interfaces/` does not exist yet on this worktree (branched
  from `origin/launchpad`) — confirmed by `find launchpad/docs/corpus/interfaces`
  returning "No such file or directory". No corpus node for nip-gs or any sibling
  buzz-nip exists on `origin/launchpad`.
- `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum has no `interface`
  value; `interfaces-events` is the correct enum member for an interface-shaped node
  (confirmed against the enum list and against
  `launchpad/docs/corpus/templates/interface.md`, which states the same node type
  for its own instance nodes).
- The sibling node `interfaces-nostr-buzz-nips-nip-er` (content is actually
  `nip-er.md`, on branch `task/997-interfaces-nostr-buzz-nips-nip-gs`) is unmerged
  and must not be targeted by a `relationships` edge; it will be mentioned by
  filename in prose only, per the dispatch instructions.
- `launchpad/project-intelligence/corpus/validate.py` and
  `launchpad/project-intelligence/corpus/tests/test_*.py` exist and are runnable
  from the repo root with `python3` (no Hermit activation required for the direct
  invocation per `AGENTS.md`'s "Running the check" section).

STEP 1 [independent] Draft the corpus node
done when: `launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-gs.md` exists,
parses as YAML front matter + Markdown body, and every Definition-of-done bullet
in issue #998 has a corresponding section in the body (inputs/outputs/errors,
auth/versioning/ordering, spec link, valid + failure example).

Create `launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-gs.md` with:
- Front matter: `id: interfaces-nostr-buzz-nips-nip-gs`, `type: interfaces-events`,
  `status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`,
  an `evidence` ledger citing (a) the provenance commit
  650354eab8d41ab6ce1a71de079a6c6d95c69052, (b) `docs/nips/NIP-GS.md` for the spec
  claims, (c) `crates/git-sign-nostr/src/lib.rs` symbols/line ranges for each
  implementation claim, (d) `crates/git-sign-nostr/README.md` for the git-config
  wiring claim. No `relationships` array (nothing on `origin/launchpad` resolves).
- Body per the `interfaces-events` shape observed in
  `launchpad/docs/corpus/templates/interface.md`: interface description, an
  Operations table (sign / verify, each pointing at `do_sign`/`do_verify` and the
  NIP-GS spec sections that define them), Contract and stability (versioning via
  the `v` field, error/rejection behavior via `ERRSIG`/`BADSIG`/exit codes,
  ordering/idempotency N/A-and-say-so, auth via key-loading precedence and the
  optional NIP-OA `oa` field), a Boundary statement (does not restate NIP-OA's own
  contract, does not restate NIP-01/NIP-98), one valid example (the deterministic
  signing test vector) and one failure example (an `ERRSIG` invalid case), and a
  Scope and omissions section.
- Prose-mentions (not `relationships` edges) the sibling `nip-er.md` file by name
  where relevant, per the dispatch instructions.

STEP 2 [needs 1] Validate the node
done when: the command exits 0, with no `FAIL` lines (an `UNVERIFIED` notice is
acceptable per `AGENTS.md`).

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo
root of this worktree.

STEP 3 [needs 2] Earn the commit gate
done when: the command's output includes the line `OK` (unittest's success
marker) and no `FAILED` line.

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`

STEP 4 [needs 3] Commit
<!-- RUNS HERE -->
done when: `git log -1 --stat` on this worktree's branch shows a new commit
containing exactly those two files, and `git log -1 --format=%B` shows a
`Signed-off-by` trailer.

Stage exactly `launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-gs.md` and
this plan file, then `git commit -s`.

STEP 5 [needs 4] Self-review
done when: each Definition-of-done bullet is matched to a body section, each
evidence entry has been re-opened and confirmed to support its statement, and
`validate.py` exits 0 on the re-run.

Re-read the committed diff line by line against issue #998's Definition-of-done
checklist, re-open every cited file/line to confirm it supports its evidence
statement, confirm no second hand-authored canonical corpus document was created,
and re-run `python3 launchpad/project-intelligence/corpus/validate.py` to confirm
it still exits 0.

PARALLEL
None of these steps are independent of each other in practice — this is a single
small document task with a linear commit/validate/gate chain. STEP 1 is the only
step tagged [independent] because it depends on nothing already built in this
plan (only on the read-only research already done before this plan was written).

GATES
- `validate.py` exit 0 (STEP 2) gates the commit in STEP 4.
- The unittest discover run printing `OK` (STEP 3) gates the commit in STEP 4 —
  per the dispatch instructions, if this is rejected for a missing gate stamp,
  that is reported as a finding, not routed around with `--no-verify` or a
  hand-edited stamp file.
- STEP 5's re-validation is the final gate before reporting completion.

BUDGET
One file created (~150-250 lines of Markdown), one plan file, one commit. No
code changes, no dependency changes, no second corpus document.

OPEN
- Whether `interfaces-nostr-buzz-nips-nip-er` will exist on `origin/launchpad` by
  the time this node merges is not this task's to resolve — treated as
  unmerged/unresolvable per the dispatch instructions regardless of its actual
  state, so no `relationships` edge is added to it under any circumstance.
- Per-type corpus standards for `interfaces-events` nodes (naming, evidence depth)
  are unlanded per `AGENTS.md`'s own gap table; this node is built against
  `node.schema.json` plus `templates/interface.md`'s worked shape, and may need
  reshaping once a settled standard lands.

LEFT OUT
- No changes to `docs/nips/NIP-GS.md` or `crates/git-sign-nostr/` — this task
  documents existing spec/code, it does not change either.
- No `relationships` edges to any node — nothing on `origin/launchpad`'s corpus
  tree resolves as a valid target at this revision.
- No second corpus document, no generated-index changes, no other corpus node
  touched.
