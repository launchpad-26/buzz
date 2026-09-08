Issue #1128 — task: document layers/networking/redis-fanout.md
Stated size: none given — the corpus document-task template has no Size field  ->  cap: 5 steps
(capped further by this batch's dispatch brief, which sets a hard 5-step maximum)

One corpus node, one file. Parent Feature #609 (protocol and networking layer corpus).

ALREADY TRUE  (verified against this worktree, not notes)
  Worktree __worktrees/task-1128-redis-fanout, branch task/1128-redis-fanout,
  created from origin/launchpad. `git rev-parse HEAD` = 29ca9b189bd3f639ba09c972b57c70538c0860c6.
  The brief names 96782d1035f5bcb878edaa4b75b95ccc85ef4ce0 as the base; that
  commit IS an ancestor of HEAD (`git merge-base --is-ancestor` exits 0), so the
  fetch picked up newer launchpad commits. Provenance records the revision this
  node was actually checked against — 29ca9b189b — not the brief's older sha.

  launchpad/docs/corpus/layers/networking/ does not exist yet. The target file
  does not exist.

  FIVE neighbouring nodes are already merged and were read in full or in part
  before drafting:
    architecture/flows/live-fanout.md              (architecture-flows-live-fanout)
    layers/data/redis/channel-pubsub.md            (layers-data-redis-channel-pubsub)
    layers/data/redis/dedicated-pubsub-connection.md
    layers/data/redis/reconnect-behavior.md
    implementation/crates/buzz-pubsub.md

  OVERLAP IS REAL AND MUST BE SCOPED AROUND. architecture-flows-live-fanout
  already narrates the end-to-end accepted-event delivery sequence, including a
  step 3 "Cross-node delivery". It compresses the entire Redis wire hop into one
  sentence ("a background task holding a broadcast::Receiver<ChannelEvent> fed by
  the pod's Redis pub/sub subscriber"). layers-data-redis-channel-pubsub
  describes the same machinery as a *reference* — topic table, command table,
  lifecycle prose — not as an ordered sequence, and does not state the
  subscribe-before-publish precondition as a step at all.

  So the genuinely uncovered subject is: the ordered hop *between* two relay
  instances — what must already have happened on the receiving pod for the hop to
  work, and the six in-crate stages the payload passes through between
  `publish_event` on pod A and `fan_out_pubsub_event` on pod B.

  Legal relationship targets confirmed present in the merged-id list:
  architecture-flows-live-fanout, layers-data-redis-channel-pubsub,
  layers-data-redis-dedicated-pubsub-connection, layers-data-redis-reconnect-behavior,
  implementation-crates-buzz-pubsub, architecture-containers-relay,
  architecture-containers-redis. No #609 sibling may be targeted — none is merged.

STEP 1 — Fix the scope line against architecture-flows-live-fanout.
  Decide, and write down in the node's Boundary section, exactly which segment of
  the fan-out story this node owns and which segment live-fanout keeps.
  Done when: the node's Flow statement names the receiving pod's SUBSCRIBE
  precondition and the in-crate hop as its subject, and the Boundary section
  names live-fanout as the owner of ingress, access filtering and socket
  delivery, by id.

STEP 2 — Write the front matter.
  type: layers (per brief decision 1), id layers-networking-redis-fanout (decision
  2), status draft, origin launchpad, audiences agent/developer/operator.
  Exactly one commit-only FACT: the provenance entry for 29ca9b189b.
  Every other FACT cites a bare repo-relative path that was opened.
  Done when: `python3 -c "import yaml"`-parseable front matter with seven or fewer
  permitted keys, and every entry_class/field combination matches
  node.schema.json's conditional rules.

STEP 3 — Write the body to templates/flow.md's required sections.
  Flow statement; Sequence (every step cited); Diagram (Mermaid sequenceDiagram);
  Outcome (success + at least one real failure path from code); Boundary;
  Relationships; Scope and omissions (two distinct things — what is not covered
  and who owns it, and separately what could not be verified).
  Done when: all seven sections present, and every numbered step in Sequence has
  a corresponding evidence entry in the ledger.

STEP 4 — Validate.
  `python3 launchpad/project-intelligence/corpus/validate.py`
  Done when: exit status 0.

STEP 5 — Stamp, then commit.
  Stamp as the sole command in its own call, foreground, unpiped, timeout 600000:
  `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  Then, in a separate call, `git add` + `git commit -s`.
  Done when: the unittest run's final line is OK and the commit exists.
  Note: `FAIL corpus root does not exist: .../does-not-exist-anywhere` mid-run is
  a negative fixture's own stdout, not a failure.

NOT IN THIS PLAN
  Pushing, or opening a PR — the orchestrator integrates the Feature's commits.
  Any second hand-authored corpus document.
  Any change to runtime product behaviour.
