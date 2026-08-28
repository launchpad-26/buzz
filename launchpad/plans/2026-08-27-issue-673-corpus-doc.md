Issue #673 — task: document architecture/deployment/multi-relay.md
Stated size: no `Size` line -> single-document corpus task, no explicit cap.

ALREADY TRUE  (verified against git, not notes)
  On branch `task/673-corpus-doc`, based on `origin/launchpad` at
    `a44cf52fc` ("Merge pull request #1462 from launchpad-26/task/636-corpus-agents-md"),
    working tree clean.
  `launchpad/docs/corpus/schema/node.schema.json` is merged and authoritative (required:
    id, type, status, origin, audiences, evidence; relationships optional).
  `launchpad/docs/corpus/AGENTS.md` says no per-type template exists yet and instructs
    writing directly against `node.schema.json`.
  `launchpad/docs/corpus/architecture/deployment/multi-relay.md` does NOT exist.
  The only merged corpus nodes today are `corpus-agents`, `corpus-readme`,
    `corpus-standard-confidence`, `corpus-standard-decision-references` -- none is a
    plausible `relationships` target for a deployment-topology node, so
    `relationships` is omitted rather than guessed.
  Repo evidence for "multi-relay" resolves to two distinct, both-real mechanisms:
    (1) horizontal scaling of `buzz-relay` itself (`replicaCount` > 1 in
    `deploy/charts/buzz/`, backed by shared Postgres/Redis/S3, optionally forming an
    inter-relay QUIC mesh via `crates/buzz-relay-mesh` when `BUZZ_MESH=on`), and
    (2) a second, architecturally distinct relay binary (`buzz-pair-relay`, deployed via
    `pairingRelay.*` in the same chart) for NIP-AB device pairing. This document scopes
    to (1) -- the mesh/replica topology -- since that is what "multi-relay deployment"
    names in the mesh crate's own doc comments and the HA testbed script; (2) is noted
    as a related-but-distinct relay process, not documented in depth, to avoid folding a
    second concept into one node.

STEP 1  [independent]  Gather evidence: read `crates/buzz-relay-mesh/src/{lib,wire,
        membership}.rs`, `crates/buzz-relay/src/{config,mesh_boot,router}.rs`,
        `crates/buzz-relay/src/tunnel/directory.rs`, `deploy/charts/buzz/values.yaml`,
        `deploy/charts/buzz/templates/{deployment,hpa,pdb}.yaml`,
        `deploy/local/{quickstart-ha-values.yaml,build-and-deploy.sh}`. Already done in
        this session (this plan is written after gathering, not before) -- STEP 1 is
        recorded as complete at plan-write time.
        done when: every claim in the drafted document cites one of the paths above (or
        another path actually opened) and no claim rests on inference presented as fact.

STEP 2  [needs 1]  ← RUNS HERE  Write
        `launchpad/docs/corpus/architecture/deployment/multi-relay.md`: schema-valid
        front matter (`id: architecture-deployment-multi-relay`, `type: architecture`,
        `status: draft`, `origin: launchpad`, `audiences`, no `relationships`) plus a
        body covering the issue's own DoD checklist and the category tail (topology +
        execution nodes; container/service/data-store mapping; network, persistence and
        trust boundaries without secrets; deployment automation/config as authority;
        failure/recovery implications).
        done when: the file exists, front matter parses, and every category-tail bullet
        has a corresponding section.

STEP 3  [needs 2]  Validate: `python3 launchpad/project-intelligence/corpus/validate.py`
        must exit 0 against the full tree including the new file. Fix and re-run on any
        failure.
        done when: the command exits 0.

STEP 4  [needs 3]  Earn the commit verification stamp by running
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
        "test_*.py"` as the sole prior command, then commit the plan + document with
        `git commit -s`, then push and open a draft PR.
        done when: the unittest run reports OK, the commit carries a
        `Signed-off-by:` trailer, and `gh pr view` resolves the opened draft PR.

PARALLEL  None. Single target file, strictly sequential steps.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` (must exit 0,
          this session). `review-adjudicate` and a cross-model pass are explicitly
          deferred to the batch owner's morning review -- not run in this session, per
          issue #608's batch instructions. No automated `review-code` pass is available
          in this run; the PR body must say so plainly rather than imply one ran.

BUDGET    STEP 2. The hard part is describing the mesh's fencing/trust model precisely
          enough to be useful without exposing secret material or restating the wire
          contract verbatim, and being honest that the Helm chart does not enable
          `BUZZ_MESH` by default (it is opt-in via `relay.extraEnv`).

OPEN      Whether "multi-relay" in the issue title means the mesh/replica topology (1)
          above, the pairing-relay sidecar (2), or a third possibility -- multi-region/
          multi-community federation, where each Buzz community is backed by an
          independently deployed relay (see desktop's community-switching model). The
          issue body gives no further disambiguation. Planned handling: document (1) as
          the primary subject -- it is what `buzz-relay-mesh`'s own module doc and the
          HA deploy tooling call "the relay mesh" / multi-replica topology -- and name
          (2) and the multi-community case explicitly as related-but-out-of-scope so a
          reader is not misled into thinking they were considered and excluded silently.
          This is stated in the issue's own DoD sense (real ambiguity), not resolved by
          silently picking one and hiding the other readings.

LEFT OUT  Editing `launchpad/docs/corpus/AGENTS.md` or any other existing corpus node.
          Any `relationships` edge -- no merged node is a plausible target.
          Deep documentation of `buzz-pair-relay` (the pairing relay) as its own
          topology -- named as related, not documented in depth, to keep this node to
          one concept.
          Live `deploy/local/build-and-deploy.sh` execution against a real cluster --
          this session verifies claims by reading the script and chart, not by standing
          up a docker-desktop k8s testbed.
