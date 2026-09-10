# Issue #917 — implementation/crates/buzz-admin.md

Stated size: dispatch brief caps this task at one hand-authored document -> cap: 5 steps.

ALREADY TRUE: `launchpad/docs/corpus/templates/implementation-reference.md`,
`launchpad/docs/corpus/AGENTS.md`, `launchpad/docs/corpus/schema/node.schema.json`, and
`launchpad/docs/corpus/schema/relationships.schema.json` are merged on `origin/launchpad`.
`launchpad/docs/corpus/implementation/crates/buzz-admin.md` does not exist yet. This is the
FIRST node authored from the `implementation-reference` template — no worked example
exists to imitate, so the template's own required-sections list is the spec. Two merged
`architecture-context-*` nodes (`architecture-context-buzz-platform`,
`architecture-context-relay-operator`) already independently cite `buzz-admin`'s
subcommand surface as supporting context; they are candidate `references` targets, already
verified to resolve on `origin/launchpad`.

STEP 1  [independent] Gather evidence: read `crates/buzz-admin/Cargo.toml`, `src/main.rs`,
and `src/deletions.rs` in full (already done in the investigation preceding this plan — no
further reading needed here). Confirm: 7 subcommands (`add-member`, `remove-member`,
`list-members`, `generate-key`, `migrate`, `product-feedback list`, `reconcile-channels`,
plus the `deletions` subcommand group delegating to `buzz-deletion`); dependencies on
`buzz-db`, `buzz-pubsub`, `buzz-deletion`, `buzz-core`, `buzz-auth`, `buzz-search`,
`buzz-audit`, `buzz-workflow`, `buzz-media`; the one existing automated test
(`deletions.rs::continuous_worker_command_is_not_exposed`); and the still-unresolved BL1
finding (`launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md`) that
`reconcile-channels --relay-key` puts the relay's signing key in argv — confirmed present
in current `main.rs` (lines ~102-106), not yet fixed. ← RUNS HERE
done when: the subcommand list, dependency list, test inventory, and BL1 status above are
each traced to a real file/line already opened in this session (no further reads needed to
proceed to STEP 2).

STEP 2  [needs 1] Write front matter: id `implementation-crates-buzz-admin`, type
`implementation`, status `draft`, origin `launchpad`, audiences `[agent, developer,
operator, reviewer]`, one commit-citation FACT for the recorded revision (`git rev-parse
HEAD` in this worktree), one evidence entry per substantive claim (FACT for everything
opened directly: `Cargo.toml`, `main.rs`, `deletions.rs`, `ARCHITECTURE.md`,
`NOSTR.md`, `docker-compose.yml`/`run.sh`, `Dockerfile`, `TESTING.md`, `Justfile`, the
coverage/audit docs; INFERENCE only where reasoning bridges evidence, e.g. "no CI
workflow invokes `scripts/e2e-large-channel-roster.sh`" from a negative grep). Declare
`relationships: [{type: references, target: architecture-context-buzz-platform},
{type: references, target: architecture-context-relay-operator}]` — both already merged,
already cite `buzz-admin` as supporting context, no `implements`/`part-of` edge is
declared because no target spec/decision/contract or container node for `buzz-admin`
itself carries a corpus node id yet (`architecture-containers-cli.md`'s own Scope table
says so explicitly).
done when: front matter validates against `node.schema.json`'s shape by inspection (every
evidence entry has the fields its `entry_class` requires; both `references` targets are ids
confirmed present in STEP-0's `git ls-tree` of `origin/launchpad`).

STEP 3  [needs 2] Write the body against the template's seven required sections
(Realization statement, Target, Implementation surface, Divergences, Verification,
Relationships, Scope and omissions). Target section states honestly that `buzz-admin` has
no single spec/ADR/NIP document target — it operationally mirrors event-kind and
tenant-resolution contracts defined in code (`buzz-core/src/kind.rs`'s NIP-43 constants,
`buzz-relay`'s community-resolution logic via `relay_url_authority`) rather than realizing
one documented target, and says so rather than inventing an `implements` edge. Divergences
section names the confirmed-still-present BL1 argv-exposure finding as a real, evidenced
gap. Verification section states plainly: one automated unit test, one manual smoke
sequence (`TESTING.md`), one standalone (not CI-wired) scripted check
(`scripts/e2e-large-channel-roster.sh`), and two `launchpad/docs/Observability` coverage
rows (T04/T05) marked "Pending assessment" against issues #476/#468 — no dedicated
integration suite exists. Scope and omissions distinguishes `buzz-admin` (this crate) from
the unrelated `docs/admin/README.md` moderation web dashboard, which despite the naming
collision is a different, relay-hosted surface this node does not cover.
done when: all seven required sections exist in the file, each DoD bullet from issue #917's
body has a corresponding sentence/section satisfying it, and every citation in the body's
prose names a source actually opened in STEP 1's investigation.

STEP 4  [needs 3] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and
re-run until exit 0.
done when: the command exits 0 on a run after the STEP 3 edit.

STEP 5  [needs 4] Run the corpus unittest suite
(`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"`) as the sole command in its own call to earn the verification stamp, confirm
`OK`, then commit the plan + document together in a separate call. No push, no PR — this
batch integrates into one Feature-level draft PR later.
done when: the unittest command prints `OK` and the subsequent `git commit -s` succeeds
(or, if the commit gate refuses with no stamp found, that refusal is reported verbatim as
BLOCKED rather than worked around).

PARALLEL: none — single file, single task, no code changes.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before
commit. The corpus unittest suite must print `OK` immediately before the commit, as its
own isolated command. `review-code`/cross-model final review are deferred to the batch
owner's later integration pass, not run per-node here.

BUDGET: small-to-medium — one document, no code changes; evidence gathering already
completed across ~12 files (crate source, `ARCHITECTURE.md`, `NOSTR.md`, `Dockerfile`,
`Justfile`, `TESTING.md`, `deploy/compose/run.sh`, two audit/coverage docs, two existing
corpus nodes).

OPEN: Whether `type: implementation` or `type: interfaces-events` is the better fit was
considered and resolved in favor of `implementation` — `buzz-admin` is fundamentally an
operational CLI over several existing subsystems (membership, channel discovery,
migrations, deletions, feedback inspection), not a single protocol/wire-level contract
the way `interfaces-events` implies; the NIP-43-shaped event kinds it emits are a part of
its surface, not its whole nature. No `implements` edge is declared because no
spec/decision/contract this crate realizes carries a corpus node id yet — this mirrors
`architecture-containers-relay.md` and `-postgres.md`'s own precedent of omitting
`implements` for the identical reason at their own recorded revisions.

LEFT OUT: No claim about whether Block's internal deployment pipelines
(`squareup/block-coder-tf-stacks`, `sprout-oss`) invoke `buzz-admin migrate` or
`add-member`/`remove-member` in practice — those are private repositories this task does
not open, same boundary `architecture-containers-postgres.md` already draws. No attempt to
fix the BL1 argv-exposure finding or file a new issue for it — it is already tracked in
`launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md` and this task only cites it, per
the Out of Scope section of issue #917 ("Changing runtime product behavior unless a
separately linked implementation issue owns that change"). No `part-of` edge to
`architecture-containers-relay` or `-cli` — `buzz-admin` is a separate binary/crate from
both, not a constituent section of either, and `-cli.md`'s own Scope table already states
`buzz-admin` needs its own, not-yet-written container node.
