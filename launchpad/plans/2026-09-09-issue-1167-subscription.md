# Plan — issue #1167: document the subscription (corpus node)

**Issue:** launchpad-26/buzz#1167 (parent Feature #609)
**Target:** `launchpad/docs/corpus/layers/protocol/subscription.md`
**Node id:** `layers-protocol-subscription`
**Template:** `launchpad/docs/corpus/templates/concept.md`
**Worktree:** `__worktrees/task-1167-subscription`, branch `task/1167-subscription`
**Provenance revision:** `29ca9b189bd3f639ba09c972b57c70538c0860c6` (`git rev-parse HEAD`
in the worktree; confirmed with `git cat-file -e`, exit 0)

## Subject and boundary

The **subscription** as a living object: its identity (per-connection, client-supplied
`sub_id`), the two maps that hold it, its per-connection cap and replacement semantics,
the Redis topic retain/release refcount it drives, and what ends it — `CLOSE`, channel
revocation, or the connection dropping.

Owned by siblings, not this node: `REQ` (#1165), `CLOSE` (#1146), `EOSE` (#1150),
filters (#1157), `CLOSED` (#1147). None of those are merged, so **no relationship may
target them**.

Adjacent and merged — link, do not restate: `architecture-flows-live-fanout`,
`architecture-flows-historical-query`, `architecture-flows-websocket-connection`.

## Steps

### Step 1 — Establish the evidence (done before drafting)

Open and read, recording only what backs a claim:
`crates/buzz-relay/src/subscription.rs`, `crates/buzz-relay/src/handlers/req.rs`,
`crates/buzz-relay/src/handlers/close.rs`, `crates/buzz-relay/src/connection.rs`,
`crates/buzz-pubsub/src/lib.rs`, `crates/buzz-pubsub/src/subscriber.rs`,
`crates/buzz-relay/src/nip11.rs`, `crates/buzz-test-client/tests/e2e_relay.rs`.

**Done when:** each of the four dispatch-listed claims (per-connection identity;
replacement not charged against the cap; the cap value and its `CLOSED` rejection;
topic retain/release refcount) is either confirmed against an opened file or recorded
as refuted, and the disconnect-cleanup mechanism is named.

### Step 2 — Confirm relationship targets exist on `origin/launchpad`

Grep the merged-id list for every candidate target; write down only ids that appear.

**Done when:** every id in `relationships` is present in
`corpus-merged-ids.txt`, and no #609 sibling id appears.

### Step 3 — Write the node

Front matter: `id: layers-protocol-subscription`, `type: layers`, `status: draft`,
`origin: launchpad`, `audiences`, one commit-only provenance FACT, one evidence entry
per substantive claim, classified honestly. Body follows `templates/concept.md`'s
required sections, with a `Scope and omissions` section carrying both the boundary and
the expected-but-unverified disclosure.

**Done when:** the file exists, every FACT cites a file that was opened and that
supports its statement, and the ledger has exactly one commit-only FACT.

### Step 4 — Validate

`python3 launchpad/project-intelligence/corpus/validate.py`

**Done when:** exit status 0.

### Step 5 — Self-review, stamp, commit

Re-read every evidence entry against its source and every DoD bullet in #1167 **before**
stamping. Then run the corpus test suite as the sole foreground command
(`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`,
timeout 600000), confirm `OK`, and commit with `git commit -s`.

**Done when:** the suite ends `OK` and one signed-off commit exists. Do not push; do not
open a PR.
