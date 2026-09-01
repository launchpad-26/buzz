---
id: verification-e2e-git
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "The relay mounts git smart-HTTP hosting at GET /git/{owner}/{repo}/info/refs, POST /git/{owner}/{repo}/git-upload-pack (clone/fetch) and POST /git/{owner}/{repo}/git-receive-pack (push), built by git_router and merged into the main app router alongside the NIP-05/health/media/git-policy routers."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs:2103-2112"
      - "crates/buzz-relay/src/router.rs:49"
      - "crates/buzz-relay/src/router.rs:149-150"
  - statement: "crates/buzz-test-client/tests/e2e_git.rs contains exactly three test functions: one plain #[test] (git_s3_probe_builds_both_addressing_styles, an S3-URL-construction unit test with no relay or git involved) and two #[tokio::test] functions each marked #[ignore = \"requires live relay + MinIO + git\"]: git_clone_push_fetch_force_roundtrip and git_concurrent_push_one_wins_and_repo_recovers. The file's own module doc-comment states 'All tests are #[ignore] so they don't run in CI by default.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_git.rs:1-18"
      - "crates/buzz-test-client/tests/e2e_git.rs:243-269"
      - "crates/buzz-test-client/tests/e2e_git.rs:411-413"
  - statement: "Neither e2e_git #[ignore]d test is invoked anywhere in .github/workflows/ci.yml's --ignored jobs, unlike several sibling e2e suites (e2e_persona, e2e_relay, e2e_media and others) which are explicitly run there with --ignored; a plain `cargo test -p buzz-test-client --test e2e_git` today therefore runs only the S3-addressing unit test and executes zero git-over-HTTP behavior."
    entry_class: FACT
    evidence:
      - "grep_ci_workflow_for_e2e_git('grep -n \"e2e_git\" .github/workflows/ci.yml') -> no matches; contrast .github/workflows/ci.yml:892-894,907, which invoke --ignored for e2e_persona, e2e_team_catalog, e2e_nostr_interop, e2e_project, e2e_relay, e2e_media, e2e_media_extended and e2e_media_video"
  - statement: "git_clone_push_fetch_force_roundtrip generates a fresh owner keypair, announces a repo via a kind:30617 event bound to a channel the owner just created, then: clones the announced (empty) repo; pushes an initial commit and asserts the S3 manifest pointer advanced from its pre-push value; clones a second time and asserts the fresh clone's file content and `main` SHA match what was pushed; pushes a second commit and pulls it into the first clone, asserting the SHA matches; hard-resets and force-pushes a rewritten history, asserting the pointer advanced again and a new clone observes the rewritten (not the discarded) content; and pushes a lightweight tag, asserting the pointer advanced once more and a fourth clone lists the tag."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_git.rs:268-409"
  - statement: "Every git invocation in e2e_git.rs, including in git_clone_push_fetch_force_roundtrip, is run with `-c commit.gpgsign=false -c tag.gpgsign=false`, and git-sign-nostr documents itself as a pluggable signing program invoked only via git's `gpg.x509.program` configuration when signing is requested; with signing explicitly disabled on every commit and tag operation, git-sign-nostr's binary is never invoked by this test."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-test-client/tests/e2e_git.rs:86-113"
      - "crates/git-sign-nostr/src/lib.rs:1-13"
    confidence: 0.8
  - statement: "Every git invocation in e2e_git.rs sets `credential.helper` to the compiled git-credential-nostr binary and `credential.useHttpPath=true`, and git-credential-nostr's own module doc-comment states it answers git's credential-helper protocol by signing a NIP-98 kind:27235 event over the request URL and method and returning it base64-encoded for git to retry the request as `Authorization: Nostr <credential>` -- so this is the authentication path the test actually exercises for every clone, push, fetch, pull and tag operation."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_git.rs:86-113"
      - "crates/git-credential-nostr/src/lib.rs:1-6"
  - statement: "crates/git-credential-nostr/tests/integration.rs is a separate, unconditionally-run (no #[ignore] found in the file) test suite that spawns the compiled git-credential-nostr binary in isolation and asserts on the credential-helper stdin/stdout protocol directly, without a live relay or a real git clone/push; it tests the helper program, not the end-to-end clone/push/fetch obligation this node documents."
    entry_class: FACT
    evidence:
      - "crates/git-credential-nostr/tests/integration.rs:1-4"
  - statement: "git_clone_push_fetch_force_roundtrip uses a single owner keypair for every git operation in the test and contains no case where an unauthenticated or non-member client attempts a clone or push, so the repo's read/write authorization boundary (the buzz-channel-tag-based SEC-005 gate in crates/buzz-relay/src/api/git/binding.rs and transport.rs) is not exercised, positively or negatively, by this test."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_git.rs:268-296"
      - "crates/buzz-relay/src/api/git/binding.rs:1-8"
  - statement: "docs/git-on-object-storage.md, this repository's draft formal specification of the git-over-object-storage protocol, names a different e2e_git test -- git_concurrent_push_one_wins_and_repo_recovers, not the round-trip test this node documents -- as 'the checked-in regression fence' for its no-fork/linearizability theorem (Inv_NoFork), and states that test 'passes against MinIO with no retry layer' as of that document's own writing."
    entry_class: FACT
    evidence:
      - "docs/git-on-object-storage.md:78-84"
      - "docs/git-on-object-storage.md:509-514"
  - statement: "The concurrent-push linearizability guarantee that git_concurrent_push_one_wins_and_repo_recovers verifies is a system-wide invariant with a formal statement (Inv_NoFork, Theorem 3) independent of any one test, per docs/git-on-object-storage.md and its companion TLA+ module, which is a different shape of corpus content from this node's single obligation-plus-test pairing."
    entry_class: FACT
    evidence:
      - "docs/git-on-object-storage.md:68-76"
      - "docs/git-on-object-storage.md:516-522"
  - statement: "architecture-flows-git-push, an existing corpus node, already documents the git push flow's authentication and authorization mechanism -- GitAuth's NIP-98 extraction, host-derived tenant binding before URL verification, and the pre-receive-hook-to-policy-endpoint push authorization callback -- that git_clone_push_fetch_force_roundtrip exercises as a black box; this node does not restate that mechanism."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/git-push.md"
  - statement: "At the recorded revision, origin/launchpad's launchpad/docs/corpus tree carries verification-e2e-git's intended relationship target, architecture-flows-git-push, as a real, loadable node id."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> includes architecture/flows/git-push.md (id: architecture-flows-git-push)"
relationships:
  - type: references
    target: architecture-flows-git-push
---

# Git smart-HTTP end-to-end round trip — test contract

## Purpose and boundary

This node documents one obligation: that a real `git` client, authenticated through
the `git-credential-nostr` credential helper, can perform a full clone / commit /
push / fetch / force-push / tag lifecycle against the relay's git smart-HTTP hosting
endpoints, with every write immediately visible to a fresh clone. It covers that
obligation and its verifying test only. It does not cover the relay's git
push-authorization mechanism in depth (see `architecture-flows-git-push`), the
concurrent-push linearizability guarantee (see *Scope and omissions*), or
`git-sign-nostr`'s commit/tag signing (out of scope for the reason given below).

## Obligation

> An announced git repository (created by a signed kind:30617 event) supports a
> full clone → push → fetch/pull → force-push → tag lifecycle through the relay's
> `GET /git/{owner}/{repo}/info/refs`, `POST /git/{owner}/{repo}/git-upload-pack`
> and `POST /git/{owner}/{repo}/git-receive-pack` smart-HTTP endpoints, using
> `git-credential-nostr` for authentication, with every push's content and exact
> commit SHA immediately observable, byte-for-byte, by a fresh clone.

## Verifying test(s)

- `crates/buzz-test-client/tests/e2e_git.rs` — `git_clone_push_fetch_force_roundtrip`
  (a `#[tokio::test]`, `#[ignore]`d). Covers, in order: cloning an announced empty
  repo; pushing an initial commit and observing the S3 manifest pointer advance; a
  second, independent clone observing the exact pushed content and SHA; a second
  commit pushed and pulled into the first clone; a hard-reset force-push of
  rewritten history observed correctly (not the discarded commits) by a new clone;
  and a tag push observed by a fourth clone.

No other test in this repository exercises this obligation end-to-end.
`crates/git-credential-nostr/tests/integration.rs` tests the credential helper
binary in isolation (stdin/stdout protocol, no relay, no real git operation) and
does not verify this obligation; it is named here only to distinguish it, per
*Scope and omissions*.

## How to run it

Requires: a relay reachable at `$RELAY_HTTP_URL` (default `http://localhost:3000`)
built with git hosting enabled and backed by a real or MinIO S3-compatible object
store, `git` on `PATH`, and a release build of `git-credential-nostr`:

```bash
cargo build --release -p git-credential-nostr
GIT_CREDENTIAL_NOSTR_BIN=$PWD/target/release/git-credential-nostr \
  cargo test -p buzz-test-client --test e2e_git \
  git_clone_push_fetch_force_roundtrip -- --ignored --nocapture
```

The test's `GitS3Probe` inspects the relay's own backing bucket directly (to assert
the manifest pointer advances), so it additionally needs the same S3 endpoint,
credentials, bucket and addressing style the relay itself is configured with:
`BUZZ_S3_ENDPOINT`, `BUZZ_S3_ACCESS_KEY`, `BUZZ_S3_SECRET_KEY`, `BUZZ_S3_BUCKET`,
`BUZZ_S3_REGION`, `BUZZ_S3_ADDRESSING_STYLE` (each has a MinIO-shaped local default
if unset). A community-scoped deployment additionally needs
`BUZZ_E2E_GIT_COMMUNITY_ID` set to match the pointer key's community prefix.

## Current enforcement status

**Gated**, and more weakly than several sibling e2e suites. The test exists,
compiles, and is `#[ignore]`d pending live infrastructure — but unlike
`e2e_persona`, `e2e_relay`, `e2e_media` and others, which `.github/workflows/ci.yml`
explicitly runs with `--ignored` in a dedicated job, `e2e_git` is invoked nowhere in
that workflow. As of the recorded revision no CI job runs this test at all; it is
exercised only by whoever runs the command above by hand against a live relay and
MinIO. This node does not assert that the test currently passes: doing so honestly
would require actually running it against live infrastructure, which authoring this
node did not do (see *Scope and omissions*). `docs/git-on-object-storage.md` makes a
passing claim, but about the *other* `#[ignore]`d test in this file
(`git_concurrent_push_one_wins_and_repo_recovers`), not this one.

## Limits

What a passing run of `git_clone_push_fetch_force_roundtrip` would establish, and
what it would not:

- **Proves**, for one repo and one owner identity in one test process: clone of an
  empty announced repo; that a push's content and SHA are visible, unmodified, to an
  independent fresh clone; that a second push's content is fetchable by pull; that a
  force-push's rewritten history — not the discarded commits — is what a later clone
  observes; and that a tag push is visible to a later clone. Each of the four writes
  is also asserted to advance the S3-backed manifest pointer, which is this
  protocol's sole ref-mutation signal per `docs/git-on-object-storage.md`.
- **Does not prove** any authorization boundary: the test never attempts a clone or
  push as anyone other than the repo's own owner, so a non-member's or
  unauthenticated caller's request is not exercised, positively or negatively, by
  this test at all.
- **Does not prove** anything about `git-sign-nostr` or NIP-GS commit/tag signing:
  every git invocation in the test disables `commit.gpgsign` and `tag.gpgsign`, so
  the signing program is never invoked.
- **Does not prove** the concurrent-push linearizability guarantee (exactly one
  winner under a same-ref race) — that is a different obligation, verified by a
  different test, and deliberately not folded into this node; see *Scope and
  omissions*.
- **Does not prove** behavior against any object-store backend other than whatever
  `BUZZ_S3_*` points the run at (MinIO, in the test's own defaults) — it says
  nothing about a different S3-compatible provider's conformance to the same
  protocol.
- **Was not itself run** while authoring this node. The obligation statement and
  test description above come from reading the test's source, not from an observed
  pass/fail, per the honesty rule in `launchpad/docs/corpus/standards/test-references.md`
  MUST 5.

## Scope and omissions

**This node covers** the single obligation above and its one verifying test: what
the test does, how to run it, and its actual (not assumed) enforcement status.

**A second, distinct obligation was found while gathering evidence for this node and
is deliberately not folded in.** `git_concurrent_push_one_wins_and_repo_recovers` (in
the same file) verifies that under an 8-way concurrent push race against one ref,
exactly one push wins, the rest fail cleanly, and a subsequent clone observes
exactly the winner's content. `docs/git-on-object-storage.md` states this
property formally as a system invariant (`Inv_NoFork`, Theorem 3, backed by a
companion TLA+ module) rather than as a single obligation checked by one test in
isolation — which is a different corpus shape (the invariant template, not this
test-contract template, per `launchpad/docs/corpus/templates/test-contract.md`'s own
boundary section). That property, and its test, belong in a future invariant-type
or separate test-contract node, not here.

**Not covered here, and why:**

| Not covered | Where it belongs / why not here |
|---|---|
| The relay's git push authentication and authorization mechanism (`GitAuth`, tenant binding, pre-receive hook → policy callback) | `architecture-flows-git-push` (existing corpus node, referenced above); this node exercises that mechanism as a black box and does not restate it |
| Concurrent-push linearizability / no-fork guarantee | A future invariant or test-contract node; see above |
| `git-sign-nostr` (NIP-GS commit/tag signing) | Not exercised by the verifying test at all (signing is explicitly disabled); a real signing-focused obligation would need its own node and its own test |
| `git-credential-nostr`'s own protocol-conformance tests (`crates/git-credential-nostr/tests/integration.rs`) | A component-level test of the helper binary in isolation, not an end-to-end claim about the relay; named above only to distinguish it from this node's obligation |
| Repository deletion, renaming, or discovery/listing over git | Not exercised by any test read for this node |
| General evidence, confidence and test-citation mechanics | `launchpad/docs/corpus/AGENTS.md`, `launchpad/docs/corpus/standards/evidence.md`, `standards/confidence.md`, `standards/test-references.md` |

**Expected but not verified when this node was written:**

- **Neither `#[ignore]`d test in `e2e_git.rs` was actually executed against a live
  relay and MinIO while authoring this node.** Every claim about what the test does
  is from reading its source; no claim above asserts a current pass/fail observed by
  this node's author. Running the command in *How to run it* against a real
  deployment is the way to close this gap.
- **Whether `GIT_CREDENTIAL_NOSTR_BIN`'s default (`target/release/git-credential-nostr`)
  is kept in sync with the crate's current source by whoever last built it was not
  checked.** A stale release binary would let this test silently exercise old
  credential-helper behavior; nothing in the test enforces freshness.
- **Whether a non-MinIO S3-compatible backend behaves identically was not
  checked**; the test's own defaults (and this node's *How to run it*) target MinIO.
