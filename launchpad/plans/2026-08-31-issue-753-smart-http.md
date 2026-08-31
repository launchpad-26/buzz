# Issue #753 — document capabilities/git/smart-http.md

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/git/` does not exist yet — this is the first
  node in that subtree.
- `launchpad/docs/corpus/templates/capability.md` (`corpus-template-capability`) is
  merged on `origin/launchpad` at `cad6c375fdcc590158c1456c9fc7875f0f84a844` and
  defines the required body shape (Capability statement, Maturity, Boundary,
  Relationships, Scope and omissions) plus `type: capabilities`.
- `launchpad/docs/corpus/architecture/flows/git-push.md`
  (`architecture-flows-git-push`) is already merged and documents the full push
  transport end-to-end (auth, policy callback, CAS publish) at the flow level —
  this capability node must not duplicate that content, only cite it as the
  representative flow.
- Sibling tasks #745 (`git-hosting`) and #748 (`nostr-git-authentication`) are both
  still OPEN, unmerged — no `relationships` target can resolve to either yet.
- `crates/buzz-relay/src/api/git/transport.rs` (3745 lines) and `mod.rs` (67 lines)
  are the primary source for the smart-HTTP protocol mechanics: `git_router` mounts
  three routes (`info/refs` GET, `git-upload-pack` POST, `git-receive-pack` POST),
  pkt-line encoding, the `info_refs` fast-path vs. subprocess advertisement, gzip
  request decoding, and the `application/x-git-*` content types.
- VISION_PROJECTS.md's Status table (line 256) already marks "Git hosting (smart
  HTTP + NIP-34)" as "✅ Ships today" — usable as a maturity citation.

## STEP 1 — Gather evidence from transport.rs/mod.rs

Read `info_refs`, `build_upload_pack_advertisement`, `pkt_line`,
`fast_path_eligible`, `decode_git_request_body`, `upload_pack`, `receive_pack`,
`build_git_response`, and `git_router` to ground every claim in code actually
read, not paraphrased. Record repository revision
(`cad6c375fdcc590158c1456c9fc7875f0f84a844`).

## STEP 2 — Draft `launchpad/docs/corpus/capabilities/git/smart-http.md`

Front matter: `id: capabilities-git-smart-http`, `type: capabilities`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer, operator]`.
Body follows the capability template's required sections: Capability statement
(any standard git client can clone/fetch/push a Buzz-hosted repo via git's native
smart-HTTP protocol — no bespoke client needed), Maturity (ships today, cited to
`VISION_PROJECTS.md` + the routed handlers), Boundary (not auth mechanics — #748;
not the full hosting/authorization/CAS capability — #745; not the step-by-step
push flow — already `architecture-flows-git-push`), Relationships (none — targets
unresolved), Scope and omissions.

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root.
Confirm the new node introduces zero new FAIL entries against the known 21
pre-existing baseline (#1951).

## STEP 4 — Earn the commit gate and commit

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
-p "test_*.py"` as the sole command in its own call; confirm `OK`. Then `git add`
+ `git commit -s`.

## GATES

- `validate.py` exits 0, adds zero new FAIL entries vs. the 21-error baseline.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
  "test_*.py"` passes (`OK`).
- Every FACT cites an opened source; no relationship targets an unresolved id.

## BUDGET

Single node, ~1 file changed (plus this plan). No code changes.

## OPEN

- Whether #745/#748 will land before or after this task — irrelevant to this
  node, since it declares no relationships either way.

## LEFT OUT

- No changes to `crates/buzz-relay` or any runtime code.
- No second canonical document.
- No relationships block populated (targets don't resolve on `origin/launchpad`).
