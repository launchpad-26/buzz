Issue #1048 — task: document layers/compute/remote-agent-compute.md
Stated size: no `Size` line -> cap: 5 steps (single-document corpus task, per #611 batch convention)

ALREADY TRUE  (verified against git, not notes)
  On branch `task/1048-remote-agent-compute`, worktree at
    `/home/serina/Launchpad/buzz/__worktrees/task-1048-remote-agent-compute`, based on
    `origin/launchpad` at `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5` (`git rev-parse HEAD`
    confirmed).
  `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md` and
    `launchpad/docs/corpus/templates/concept.md` are merged on `origin/launchpad`.
  `launchpad/docs/corpus/layers/compute/remote-agent-compute.md` does not exist anywhere in
    the worktree (`test -f` confirmed absent) — no `layers/` directory exists in the corpus
    at all yet (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`
    confirmed).
  `docs/remote-agents.md` (1780 lines, root of this checkout) is the formal specification for
    the provider protocol, the remote lifecycle model, and the Kubernetes binding; read in
    full for this plan.
  Three sibling `architecture`-typed corpus nodes already merged on `origin/launchpad` cite
    `docs/remote-agents.md` directly and are legitimate `relationships` targets:
    `architecture-context-ai-agent`, `architecture-containers-agent-runtime` (which names
    "the remote-agent provider protocol in full" as explicitly not covered there, owned by
    `docs/remote-agents.md`), and `architecture-deployment-kubernetes` (which explicitly
    excludes `buzz-backend-kubernetes` / remote agent compute as out of scope, drawing the
    same boundary line this node sits on the other side of).
  The five sibling `layers/compute/*` documents from issues #1041-#1045 (including
    `kubernetes-provider.md`, #1042) are drafted on other unmerged branches from this same
    batch run and are NOT on `origin/launchpad` — confirmed by the same `git ls-tree` above —
    so none of their ids are valid `relationships` targets for this node.
  `crates/buzz-backend-kubernetes` exists on disk as an in-progress crate; PR #3449
    (`block/buzz`, OPEN) is the live systemd/SSH binding (`buzz-backend-ssh`) referenced by
    `docs/remote-agents.md` as the second conforming provider under development.

STEP 1  [independent]  Gather evidence: `docs/remote-agents.md` in full (Abstract, Scope and
        Non-Goals, System Model, §Launchers, the five Invariants I1-I5, Provider Protocol
        summary-level, Conformance §L1/L2/L3, Known Defects intro, Summary). Cross-read
        `launchpad/docs/corpus/architecture/containers/agent-runtime.md` and
        `launchpad/docs/corpus/architecture/context/ai-agent.md` (both already merged, both
        cite this spec) and `launchpad/docs/corpus/architecture/deployment/kubernetes.md`'s
        explicit out-of-scope statement about `buzz-backend-kubernetes`. Record: what "remote"
        means (any compute substrate other than the local machine, reached through a
        zero-registration provider binary), why it exists (the desktop is "one launcher among
        many"; a provider is one door among several), and the invariants shared across *any*
        binding (I1-I5, and the three-layer conformance split L1/L2/L3) as distinct from the
        Kubernetes binding's own policy (L3). This is evidence-gathering; no corpus file
        changes in this step.
        done when: every claim used in STEP 2's body has a source path/line opened in this
        step, and any DoD-relevant fact not found in the repo is named as a gap for the body's
        scope-and-omissions section rather than guessed.

STEP 2  [needs 1]  ← RUNS HERE  Write `launchpad/docs/corpus/layers/compute/remote-agent-compute.md`
        from `launchpad/docs/corpus/templates/concept.md`: schema-valid front matter
        (`id: layers-compute-remote-agent-compute`, `type: layers`, `status: draft`,
        `origin: launchpad`, `audiences`, an `evidence` ledger with a commit citation for
        `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5` first, one entry per substantive claim,
        `relationships` limited to `references` edges against
        `architecture-context-ai-agent`, `architecture-containers-agent-runtime` and
        `architecture-deployment-kubernetes` only), and a body satisfying both the issue's DoD
        checklist and the concept template's required sections (definition, use cases,
        boundary/non-goals against the Kubernetes-specific #1042 node without linking it,
        scope-and-omissions naming what was expected but not verified).
        done when: the file exists with schema-required keys present, every `##` section the
        concept template requires is present, and no second concept/contract/procedure is
        introduced as a full section (a discovered one is named in OPEN/LEFT OUT instead).

STEP 3  [needs 2]  Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
        repo root and fix anything it reports until it exits 0.
        done when: the command's own exit code is 0, confirmed by reading `$?` after the run,
        not inferred from absence of error text.

STEP 4  [needs 3]  Self-audit the finished node line by line against the issue's DoD checklist:
        confirm exactly one hand-authored document was created; confirm every evidence entry
        supports the claim it sits under and is classified FACT/INFERENCE/TEAM_KNOWLEDGE
        honestly; confirm the boundary section explicitly excludes Kubernetes-binding-specific
        claims (owned by #1042) rather than restating them; confirm the term is defined in one
        sentence; confirm relationships resolve against `origin/launchpad`, not this worktree;
        re-run `validate.py` once more after any fix.
        done when: the audit note maps each DoD bullet to where the body satisfies it, and
        `validate.py` exits 0 on the final version.

STEP 5  [needs 4]  Earn the verification stamp by running
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        as the sole prior command, confirm `OK`, then in a separate call stage and commit the
        plan file and the new document with `git commit -s`. No push, no PR — a separate batch
        integration step cherry-picks this commit.
        done when: the unittest run reports `OK`; the commit succeeds without a "no
        verification stamp" block, confirmed by `git log -1` showing the new commit on
        `task/1048-remote-agent-compute`.

PARALLEL  None. This is one target file
          (`launchpad/docs/corpus/layers/compute/remote-agent-compute.md`) plus the plan file
          that documents it — strictly sequential, single worktree, single agent. Nothing here
          may run concurrently with the sibling #1041-#1047 batch workers, since they may
          independently touch shared generated corpus indexes; this task touches only its own
          target file.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` (STEP 3, re-run in
          STEP 4) is the only automated gate run in this session. `review-code`,
          `review-adjudicate`, and a cross-model final pass are explicitly deferred to the
          batch owner's morning review per the task brief — none of them run here. `qa`
          explore mode does not apply: this is a docs-only change with no runtime interface to
          exercise.

BUDGET    STEP 2. The hard part is scoping the umbrella concept correctly — stating the
          provider-protocol/lifecycle invariants that hold across *any* binding (I1-I5,
          §Launchers' three-layer split) without re-describing the Kubernetes binding's own
          policy (image, pod shape, GC, entrypoint — all L3-specific and #1042's canonical
          territory), while still grounding every claim in the same source document both nodes
          draw from.

OPEN      Whether `relationships` should include a `references` edge toward a future
          `layers-compute-kubernetes-provider` id once #1042 merges. That id does not exist on
          `origin/launchpad` today (confirmed in ALREADY TRUE), so no edge to it can be added
          now without failing validation; recorded here rather than silently omitted forever —
          a later edit, once #1042 lands, is the right place to add it.
          Whether the systemd/SSH binding under active development in PR #3449
          (`buzz-backend-ssh`) deserves a named mention in this umbrella node's body as a
          second concrete binding alongside Kubernetes, or whether naming an unmerged PR's
          provider by name overclaims stability the corpus's evidence discipline would flag.
          This plan's STEP 2 leans toward naming it only as TEAM_KNOWLEDGE (an open PR,
          unmerged) illustrating that the protocol is designed for more than one binding, not
          as a FACT about a shipped feature.

LEFT OUT  Any Kubernetes-binding-specific claim (image pinning, pod shape, entrypoint ABI,
          Secret/GC mechanics, `provider_config` v1 fields) — that is `layers/compute/
          kubernetes-provider.md`'s (#1042) canonical territory, unmerged and out of reach as
          a `relationships` target today, and duplicating its content here is exactly what the
          "one node, one idea" atomicity rule and this task's own DoD checklist forbid.
          Any change to `crates/buzz-backend-kubernetes`, `docs/remote-agents.md`, or any file
          outside the one target document and this plan.
          Filing the found candidate follow-up (the future edge to #1042 once it merges) as a
          new issue — noted in OPEN and in the final report instead, per this task's
          instruction not to self-file discovered follow-ups.
