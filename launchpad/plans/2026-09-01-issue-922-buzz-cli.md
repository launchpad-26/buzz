# Issue #922 — implementation/crates/buzz-cli.md

Stated size: not stated in issue #922's body -> cap: 5 steps (per batch dispatch brief).

ALREADY TRUE: `launchpad/docs/corpus/templates/implementation-reference.md`,
`launchpad/docs/corpus/schema/node.schema.json`, and
`launchpad/docs/corpus/architecture/containers/cli.md` (id
`architecture-containers-cli`) are merged on `origin/launchpad`.
`launchpad/docs/corpus/implementation/crates/buzz-cli.md` does not exist yet.
`architecture-containers-cli`'s own Scope table already delegates "full
per-subcommand behavior" to "Implementation-reference nodes for individual
capabilities, not this container-level node" — this task fills exactly that
gap.

STEP 1  [independent] Gather evidence: read `crates/buzz-cli/src/main.rs`,
`lib.rs` (`Cli` struct, `--format` flag, `Cmd` enum, dispatch match block),
`error.rs` (exit-code mapping), `client.rs` (retry/timeout constants,
`BuzzClient`), `links.rs` (deep-link parse/build), `README.md`, `TESTING.md`,
and cross-check CLAUDE.md's documented buzz-cli contract (env-var
auto-injection, `--format compact` as a global flag, exit codes 0-5,
deep-link resolution) against that code and against `buzz-acp/src/lib.rs`'s
env-injection call sites. Record `git rev-parse HEAD`. ← RUNS HERE
done when: every claim intended for the evidence ledger has been opened
directly (not assumed from CLAUDE.md's prose), and two concrete divergences
are confirmed against code: (a) `--format` is a global `Cli` flag but only 5
of the 21 dispatched command groups (`messages`, `channels`, `users`,
`feed`, `moderation`) actually read `&cli.format`; (b) `messages thread
--link` accepts a raw `buzz://message` deep link directly, which CLAUDE.md's
own deep-link section does not mention as an alternative to its documented
manual-extraction workflow.

STEP 2  [needs 1] Write `launchpad/docs/corpus/implementation/crates/buzz-cli.md`
following `templates/implementation-reference.md`'s required sections
verbatim (Realization statement, Target, Implementation surface,
Divergences, Verification, Relationships, Scope and omissions), with
schema-valid front matter: `id: implementation-crates-buzz-cli`, `type:
implementation`, `status: draft`, `origin: launchpad`, `audiences: [agent,
developer, reviewer]`, an `evidence` ledger classifying every claim
FACT/INFERENCE/TEAM_KNOWLEDGE per STEP 1's citations, and `relationships:
[{type: part-of, target: architecture-containers-cli}]` (verified to resolve
against `origin/launchpad`'s corpus tree). No `implements` edge — the
target this node traces (CLAUDE.md's documented buzz-cli contract) carries
no corpus node id yet, and the template forbids inventing one.
done when: the file exists, every Definition-of-Done bullet from issue #922
is addressed in the body, and no claim in the evidence ledger rests on a
source that was not actually opened in STEP 1.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`;
fix and re-run until it exits 0 for this node. If exit status is nonzero,
confirm via `git stash` / diff against `origin/launchpad` whether the
failures are the pre-existing ~21-failure baseline unrelated to this change,
rather than assuming that baseline without checking.
done when: the validator run shows zero FAIL entries naming
`implementation-crates-buzz-cli`, and any other reported failures are
confirmed pre-existing on `origin/launchpad`.

STEP 4  [needs 3] Run `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole
command in its own tool call to earn the commit gate stamp. In a separate
call, `git add` the plan and the document and `git commit -s` them. Do not
push or open a PR — this batch integrates into one Feature-level PR later.
done when: the unittest run reports `OK`, and `git log -1` on
`task/922-buzz-cli` shows the new commit containing exactly the plan and the
corpus document.

PARALLEL: none — single file, single task, no other agent or process touches
`launchpad/docs/corpus/implementation/crates/buzz-cli.md` or this plan file.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must show
zero FAIL entries for this node before commit. `python3 -m unittest discover
-s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report
`OK` immediately before the commit, as the sole command in its call, per the
commit-gate contract. No push, no `gh pr create` — explicitly out of scope
for this task per the dispatch brief; a later integration phase opens the
single Feature-level PR.

BUDGET: small — one corpus document (roughly 150-250 lines), no product code
changes. Evidence gathering scoped to ~7 `buzz-cli` source files plus
`CLAUDE.md`, `buzz-acp/src/lib.rs`'s injection call sites, and the existing
`architecture-containers-cli` node.

OPEN: Whether other implementation-reference nodes written later for crates
that already have an `architecture-containers-*` node should also default to
a `part-of` edge toward it is not settled corpus-wide — this is the first
such pairing to land, so the convention is being set here, not confirmed
against a prior instance. Left for whoever reviews or authors the next
`implementation/crates/*.md` sibling to confirm or contest.

LEFT OUT: Full per-subcommand behavior for all 22 `Cmd` groups — the
Implementation surface table covers representative, verified rows only
(entry point, config surface, `--format` flag, exit codes, retry/timeout
policy, deep links), not an exhaustive command-by-command catalogue; that
remains delegated to future per-capability implementation-reference nodes,
per `architecture-containers-cli`'s own Scope table. `buzz-dev-mcp`'s
non-`buzz` personalities and `buzz-admin` — out of scope, not this crate.
No change to any product code or to CLAUDE.md itself, even though STEP 1
finds two real divergences from CLAUDE.md's prose — those are documented in
the node's Divergences section, not fixed, per this task's own "changing
runtime product behavior" out-of-scope bullet.
