# Issue #937: docs(corpus) — implementation/crates/buzz-sdk.md

Stated size: issue #937 has no explicit Size line; it matches the single-canonical-document shape every other corpus-doc task in this batch uses (e.g. #697, #698).  ->  cap: 4 steps.

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`,
`launchpad/docs/corpus/AGENTS.md`, and `launchpad/docs/corpus/templates/implementation-reference.md`
are merged on `origin/launchpad` (`76a0a4ebbe4bc4d852b0d04362ed768620da34b3`); the target file
`launchpad/docs/corpus/implementation/crates/buzz-sdk.md` does not exist yet, and no
`launchpad/docs/corpus/implementation/**` node exists yet either — this is the first node in
that subtree. `crates/buzz-sdk/Cargo.toml` names it "Typed Nostr event builders for Buzz
operations"; its `src/lib.rs` module doc states the mental model (`caller params -> builder fn
-> validates -> EventBuilder -> caller signs -> Event`, no keys held, no network calls).
Consumers confirmed by grep: `buzz-cli`, `buzz-acp`, `buzz-relay`, `buzz-test-client` (test-only)
all depend on it in their `Cargo.toml`.

STEP 1 [independent] — gather evidence: read `crates/buzz-sdk/src/lib.rs`, `builders.rs` (38
builders, 189 inline tests), `mentions.rs` (51 tests), `nip_oa.rs` (22 tests, cross-checked
against `docs/nips/NIP-OA.md`'s tag format/preimage), and the `broker/` submodule (`mod.rs`,
`actions/{mod,args,outcomes}.rs`, `client.rs`, `wire.rs`, `correlate.rs`, 39 tests in
`tests.rs`) — an unshipped agent<->host wire contract, confirmed to have zero consumers
anywhere else in `crates/` via `grep -rl buzz_sdk::broker`. Confirm `docs/agent-broker.md`,
cited by `broker/mod.rs`'s own doc comment as the English spec, does not exist anywhere in
the repo (`find . -iname '*agent-broker*'` — no hits) — a real divergence. Confirm the
crate re-exports `buzz_core::kind` and `buzz_core::channel::*` rather than owning them, and
does not itself verify general event signatures (only NIP-OA `auth`-tag verification, a
narrower capability) — the boundary against `buzz-core`. Record `git rev-parse HEAD`.
done when: every module listed above has been opened and its public surface and test count
confirmed by direct read/grep, and the `docs/agent-broker.md` absence and zero-consumer
broker facts are each independently re-run and produce the same result.

STEP 2 [needs 1] — write front matter (id `implementation-crates-buzz-sdk`, type
`implementation`, status `draft`, origin `launchpad`, audiences `agent`/`developer`/
`reviewer`) with one evidence entry per substantive claim, `FACT` for everything directly
opened, and body sections exactly matching the template skeleton: Realization statement,
Target, Implementation surface (table: module/symbol -> what it realizes), Divergences (the
missing `docs/agent-broker.md` target, and the broker module's zero-consumer status),
Verification (`cargo test -p buzz-sdk`, ~300 inline unit tests, no integration/E2E test
found exercising the crate through a real relay round-trip), Relationships (see OPEN below),
Scope and omissions. RUNS HERE.
done when: `launchpad/docs/corpus/implementation/crates/buzz-sdk.md` exists, contains every
required template section, and every evidence entry's citation was a source actually opened
in STEP 1.

STEP 3 [needs 2] — validate: `python3 launchpad/project-intelligence/corpus/validate.py`
must exit 0 against the full corpus tree including the new file. If nonzero, diff against a
`git stash` baseline to confirm any failures are the pre-existing ~21 unrelated ones, not
new.
done when: the validator exits 0, or exits nonzero with only the pre-existing baseline
failures confirmed present on `origin/launchpad` before this change.

STEP 4 [needs 3] — commit: run the corpus unittest suite as the sole command in its own tool
call to earn the verification stamp, then in a separate call stage and commit the plan file
and the new document with `git commit -s`.
done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` reports OK, and `git log -1` shows a signed-off commit containing exactly the
plan file and the new corpus document.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
must report OK to earn the commit hook's verification stamp. review-adjudicate and the
cross-model review pass are deferred to the batch owner's later integration review — not run
here.

BUDGET: single document, ~1-2 hours of agent time; no code changes, no test changes.

OPEN: no `implementation`-typed sibling node is merged yet on `origin/launchpad` at this
revision (checked via `git ls-tree -r --name-only HEAD -- launchpad/docs/corpus`), so there
is no existing implementation node id this could sit `part-of`. The two candidate
architecture-principle targets (`architecture-principles-nostr-first`,
`architecture-principles-signed-events`) are both explicitly scoped to `buzz-relay`
behavior in their own front matter (nostr-first: "design and code-review decisions...
adding new backend capability to `buzz-relay`"; signed-events: relay-side verification of
already-signed events) — `buzz-sdk` is a client-side unsigned-event builder library, not
`buzz-relay`, so declaring `implements` toward either would misstate what those nodes
actually govern. `docs/nips/NIP-OA.md` and `docs/agent-broker.md` (missing) are real
targets but have no corpus node id yet. This node therefore ships with no `relationships`
entries, naming targets by real path in prose instead, per the template's own instruction
not to invent an edge to a nonexistent id.

LEFT OUT: no runtime/product code change; no second canonical document; no `relationships`
edges (see OPEN); no new test coverage for the noted broker wire-protocol / E2E gap — the
gap is recorded in the document, not closed; no decision on whether `docs/agent-broker.md`
should be written or the reference removed — flagged as a divergence, not resolved here.
