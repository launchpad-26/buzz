# Issue #943 — implementation/crates/git-credential-nostr.md

Stated size: not stated in the issue body (a single-document corpus-authoring task) -> cap: 5 steps.

ALREADY TRUE: `launchpad/docs/corpus/templates/implementation-reference.md`,
`launchpad/docs/corpus/AGENTS.md`, `launchpad/docs/corpus/schema/node.schema.json` and
`launchpad/docs/corpus/architecture/flows/git-push.md` (id `architecture-flows-git-push`)
are merged on `origin/launchpad`;
`launchpad/docs/corpus/implementation/crates/git-credential-nostr.md` does not exist yet.
`crates/git-credential-nostr/{Cargo.toml,src/lib.rs,src/main.rs,README.md,tests/integration.rs}`
and its call sites in `crates/buzz-dev-mcp`, `crates/sprig`, `desktop/src-tauri/src/managed_agents/runtime.rs`,
`desktop/src-tauri/src/commands/project_git_exec.rs` and `crates/buzz-test-client/tests/e2e_git.rs` have
already been read at HEAD `76a0a4ebbe4bc4d852b0d04362ed768620da34b3`.

STEP 1  [independent] Write front matter (schema-valid: id `implementation-crates-git-credential-nostr`,
type `implementation`, status `draft`, origin `launchpad`, audiences `[agent, developer, reviewer]`)
with one evidence entry per substantive claim, classified FACT (crate source/tests/README/call
sites actually opened) or TEAM_KNOWLEDGE where attributed to the issue. Declare one relationship —
`references` → `architecture-flows-git-push` (the only existing merged corpus node whose subject
matter is this crate's consumer flow; verified its id resolves and its own evidence ledger already
names this crate as the client-side signer). No `implements` edge: NIP-98 and NIP-OA are external/
repo-local spec documents, not corpus nodes, so the *Target* section names them by path/URL
instead, per the template's explicit rule against inventing an edge to a nonexistent id. ← RUNS HERE
        done when: front matter block is written to the target file and parses as valid YAML with
        every required node.schema.json field present.

STEP 2  [needs 1] Write the body using the template's required sections (Realization statement,
Target, Implementation surface, Divergences, Verification, Relationships, Scope and omissions).
Implementation surface table cites: `src/main.rs` (binary entry point), `src/lib.rs::run` (protocol
loop: `parse_stdin`, `parse_method`, `load_key`/`check_keyfile_permissions`, `load_auth_tag`, NIP-98
event build+sign via the `nostr` crate), `Cargo.toml` (workspace deps: `nostr`, `serde_json`,
`zeroize`, `base64`). State explicitly what it does NOT own: object-signing (`git-sign-nostr`,
NIP-GS) and server-side verification (`buzz-relay`/`buzz-auth::nip98`, already covered by
`architecture-flows-git-push`). Name both packaging paths found in STEP 1's reading: standalone
`[[bin]]` and library re-export consumed by `buzz-dev-mcp`'s multicall dispatch (`crates/buzz-dev-mcp/src/lib.rs:151`)
under the `sprig` binary, plus desktop's runtime wiring (`resolve_command("git-credential-nostr")`
in `runtime.rs` and `project_git_exec.rs`) and `scripts/bundle-sidecars.sh`.
        done when: all seven required sections are present in the file and every DoD bullet from
        issue #943 is satisfied by some sentence in the body.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo
root; fix and re-run until exit 0. Confirm any pre-existing failures are unrelated by diffing
against `origin/launchpad`'s own baseline (stash-check), not assumed.
        done when: the validator exits 0 and reports zero FAIL entries for this node's id.

STEP 4  [needs 3] Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
-p "test_*.py"` as the sole command in its own tool call to earn the commit-gate stamp; confirm
`OK`. Then, in a separate call, `git add` the doc + this plan and `git commit -s`.
        done when: the unittest run prints `OK` and `git log -1` shows the new commit containing
        both files.

PARALLEL: none — single file, single task, no code changes.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 for this node.
The commit-gate unittest run must report `OK`. `review-adjudicate` and cross-model final review
are deferred to the batch owner's later integration pass — not run here. No push, no PR — this
task stops at the local commit per the batch's integration-phase design.

BUDGET: small — one document, no code changes; evidence gathering already done against ~10 files
(crate source, tests, README, four call-site files, one flow-node citation, one NIP doc).

OPEN: Whether `implementation-crates-git-credential-nostr` should later gain an `implements` edge
toward NIP-98/NIP-OA once (if ever) those specs get their own corpus node ids is left for whoever
authors those nodes — the template explicitly forbids inventing the edge now. Whether
`git-sign-nostr`'s own implementation-reference sibling (a separate task in this same batch) should
declare a `references` edge back to this node is that task's call, not this one's.

LEFT OUT: No relationship to `git-sign-nostr`'s node (does not exist yet in this worktree/batch —
sibling task, unmerged). No claim about the `nostr` crate's own NIP-98 implementation internals
(external dependency, out of this node's ownership). No attempt to run the `#[ignore]`-gated
`e2e_git.rs` live-relay tests — `tests/integration.rs`'s eight subprocess tests are read as the
crate's own representative, non-ignored verification instead.
