Issue #933 — implementation/crates/buzz-pubsub.md
Parent Feature #615, parent PRD #602. Single-document task; no `Size` line on the issue.
Stated size: no Size line on issue #933 -> cap: 5 steps

ALREADY TRUE
  `launchpad/docs/corpus/templates/implementation-reference.md`,
  `launchpad/docs/corpus/schema/node.schema.json`, and
  `launchpad/docs/corpus/architecture/containers/redis.md`
  (`architecture-containers-redis`) are merged on `origin/launchpad`.
  `launchpad/docs/corpus/architecture/flows/live-fanout.md`
  (`architecture-flows-live-fanout`) is also merged.
  `launchpad/docs/corpus/implementation/crates/buzz-pubsub.md` does not exist yet, and no
  `implementation/` node has been authored yet anywhere in this corpus.

STEP 1  [independent]  Gather evidence: read every source file under
        `crates/buzz-pubsub/src/` (`lib.rs`, `topic.rs`, `publisher.rs`, `subscriber.rs`,
        `presence.rs`, `cache_invalidation.rs`, `conn_control.rs`, `nip98_replay.rs`,
        `rate_limiter.rs`, `error.rs`) plus `Cargo.toml`, cross-checked against
        `architecture-containers-redis.md`'s existing claims to find what is genuinely one
        layer deeper: the dynamic `retain_topic`/`release_topic` refcounted subscription
        mechanism, the reconnect-backoff subscriber loops, `EventTopicKey` parse/format,
        the `PubSubError` taxonomy, and two documentation divergences (the dangling
        "Typing indicator tracking" doc comment above `pub use error::PubSubError;` with no
        `typing` module anywhere in the crate, and `conn_control.rs`'s doc link to
        `crate::ConnectionManager`, a type that does not exist in this crate but is defined
        in `buzz-relay/src/state.rs`). Confirm wiring into `buzz-relay` (`main.rs`,
        `state.rs`) and the `retain_topic`/`release_topic` call sites (`handlers/req.rs`,
        `connection.rs`, `handlers/close.rs`, `handlers/side_effects.rs`,
        `handlers/event.rs`). Record `git rev-parse HEAD`.
        done when: every file listed above has been opened and its role in the six-job
        table (`architecture-containers-redis.md`) is either confirmed or shown deeper;
        `cargo test -p buzz-pubsub --lib` (Hermit-activated) has been run once and its
        pass/ignore counts recorded for the Verification section.

STEP 2  [needs 1]  ← RUNS HERE  Write
        `launchpad/docs/corpus/implementation/crates/buzz-pubsub.md` following
        `implementation-reference.md`'s required sections (Realization statement, Target,
        Implementation surface, Divergences, Verification, Relationships, Scope and
        omissions). Front matter: id `implementation-crates-buzz-pubsub`, type
        `implementation`, status `draft`, origin `launchpad`, audiences
        `[agent, developer, reviewer]`. Declare `implements` -> `architecture-containers-redis`
        (buzz-pubsub is the concrete code realizing that node's stated responsibility
        table) and `references` -> `architecture-flows-live-fanout` (supporting context for
        where `publish_event` sits in the dispatch pipeline). Every implementation-surface
        row cites the module actually opened in STEP 1; the divergence section reports both
        real findings rather than an empty "checked and clean" claim.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.

STEP 3  [needs 2]  Self-audit the finished node against issue #933's DoD checklist line by
        line, confirming every evidence entry supports its statement, no second canonical
        document was created, and no claim restates `architecture-containers-redis.md`'s
        canonical prose rather than citing it.
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        reports `OK` and `validate.py` still exits 0.

STEP 4  [needs 3]  Commit the plan and the document together, signed off. Do not push and
        do not open a PR — this batch integrates all 37 documents into one Feature-level
        draft PR later, in a separate integration phase.
        done when: `git log -1 --format=%H` on the branch names a commit containing both
        `launchpad/docs/corpus/implementation/crates/buzz-pubsub.md` and
        `launchpad/plans/2026-09-01-issue-933-buzz-pubsub.md`.

PARALLEL  None — one file, four sequential steps, no code changes.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 for the
          new node. The corpus unittest suite (STEP 3) must report `OK` before commit.
          `review-adjudicate` and the cross-model final review pass are deferred to the
          batch owner's later integration review — not run here.

BUDGET    STEP 1 and STEP 2 carry the weight — ten source files plus a handful of
          `buzz-relay` call sites to read, then a single document to write. STEP 3/4 are
          mechanical.

OPEN      `architecture-containers-redis.md` already carries many of the same FACT claims
          (module responsibility table, key formats, wiring into `buzz-relay`) at the
          architecture-container grain. This node's job is to go one layer deeper —
          concrete symbols, the refcounted subscription mechanism, and the two code-level
          divergences the container node did not surface — without re-deriving or
          contradicting the container node's canonical claims. Where the same fact is
          needed for this node's own body (e.g. the Redis key formats), it is re-verified
          against the same source rather than cited from the other corpus node, per
          `AGENTS.md`'s evidence rule that a `FACT` requires opening the source, not
          another corpus document.

LEFT OUT  No claim about `buzz-relay`'s own internals beyond the call sites that establish
          how `buzz-pubsub`'s public API is used (no implementation-reference node for
          `buzz-relay` itself — out of scope, a separate task). No resolution of the
          typing-indicator or `ConnectionManager` doc-link divergences — reported as
          findings, not fixed, since this is a docs-only corpus task with no linked
          implementation issue authorizing a source change. No new `references`/`part-of`
          edges beyond `architecture-containers-redis` and `architecture-flows-live-fanout`
          — no other merged corpus node is a legitimate target for this crate's subject
          matter. No `git push`, no `gh pr create` — integration is a separate later phase.
