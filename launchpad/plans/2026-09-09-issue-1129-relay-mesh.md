Issue #1129 — task: document layers/networking/relay-mesh.md
Stated size: none stated  →  cap: 5 steps (set by the Feature #609 batch brief: one
document per issue, against conventions already settled by #636 and the corpus templates)

Target file: `launchpad/docs/corpus/layers/networking/relay-mesh.md`
Node id: `layers-networking-relay-mesh` (assigned by the dispatch brief; permanent)
Template: `launchpad/docs/corpus/templates/concept.md`
Worktree: `/home/serina/Launchpad/buzz/__worktrees/task-1129-relay-mesh`, branch
`task/1129-relay-mesh`, cut from `origin/launchpad`.

ALREADY TRUE  (verified by running the commands in this worktree, not from notes)
  `git rev-parse HEAD` -> `29ca9b189bd3f639ba09c972b57c70538c0860c6`, and
    `git cat-file -e 29ca9b189bd3f639ba09c972b57c70538c0860c6` exits 0. The batch brief
    named `96782d1035f5bcb878edaa4b75b95ccc85ef4ce0` as the base; `git merge-base
    --is-ancestor` confirms that commit IS an ancestor of this HEAD, and `git diff --stat
    96782d10..HEAD -- crates/buzz-relay-mesh crates/buzz-relay/src launchpad/docs/corpus`
    is EMPTY — every source this node cites is byte-identical between the two. The ledger
    records the revision actually checked against (this HEAD), per AGENTS.md's rule that
    the recorded revision is the one the claims were checked at.
  `git status --short` reports nothing. No corpus content is part-built.
  `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 before any edit.
  `launchpad/docs/corpus/layers/` contains `compute`, `configuration`, `data`,
    `lifecycle`, `observability` — there is NO `networking/` directory. This task
    creates it, and `git ls-tree -r --name-only origin/launchpad --
    launchpad/docs/corpus/layers/networking` returns nothing, so no sibling in this
    Feature is merged and none may be a relationship target.
  The three boundary nodes named in the dispatch have been read in full:
    - `implementation-crates-buzz-relay-mesh` owns the CRATE — its module map, its two
      seams, its `MeshError` taxonomy, its 32 `--lib` tests, its file-by-file surface.
    - `architecture-deployment-multi-relay` owns the TOPOLOGY — the Helm chart,
      `replicaCount`/HPA/PDB, the shared data stores, install-time guards, failure and
      recovery.
    - `layers-compute-mesh-compute` is a HOMONYM — MeshLLM shared LLM inference on the
      desktop. It already disambiguates itself against `buzz-relay-mesh` explicitly and
      records "no corpus node for `crates/buzz-relay-mesh` exists yet" as a gap.
    None of the three states what the mesh IS as a network plane: none contrasts it with
    the Redis-mediated east-west plane, and none says what a client sees. That gap is
    this node's subject. Boundary verdict: NOT already fully owned.
  Evidence gathered by opening files, not by search-hit counting:
    `crates/buzz-relay-mesh/src/lib.rs` — "the inter-relay QUIC mesh", one iroh endpoint
      per relay runtime, exactly two consumer seams, "mesh membership is a hint; the
      Redis fenced generation is the arbiter."
    `crates/buzz-relay-mesh/src/wire.rs` — FROZEN surface; `ALPN = b"buzz/mesh/1"`,
      `WIRE_VERSION = 1`, `FencedHeader{session_id, generation, owner_runtime_id}`,
      `Profile::{ReliableStream, RealtimeMedia, HuddleControl}`, `MeshStreamFrame::{Hello,
      Data, Goodbye, Gossip}`; `RuntimeId` is a boot-fresh ed25519 key, deliberately NOT
      the shared secp256k1 relay key.
    `crates/buzz-relay/src/config.rs` — `BUZZ_MESH` resolves only on `on`/`true`/`1`,
      defaults OFF; `BUZZ_MESH_BIND_ADDR` defaults `0.0.0.0:3478`. Adjacent field doc for
      `huddle_audio_available` states the pre-mesh failure in the codebase's own words:
      under horizontal scaling "two peers in the same huddle can land on different pods
      and never hear each other," so operators MUST set it false until the mesh lands.
    `crates/buzz-relay/src/audio/handler.rs` — the live gate: mesh `Some` -> cross-pod
      routing; mesh `None` + `huddle_audio_available=false` -> the client gets a
      `huddle_audio_unavailable` error on join.
    `crates/buzz-relay/src/audio/mesh.rs`, `crates/buzz-relay/src/tunnel/mod.rs`,
      `tunnel/reliable.rs`, `tunnel/directory.rs` — what actually rides the mesh, and
      that the Redis fenced CAS lease (not the mesh) arbitrates ownership.
    `crates/buzz-relay/src/mesh_boot.rs` — `boot_mesh` is the ONLY construction site;
      `None` means "behave exactly like a single-instance relay."
    `crates/buzz-relay/src/router.rs` — `GET /_mesh` reports `{"enabled": false}` when off.
    `crates/buzz-pubsub/src/conn_control.rs` and `crates/buzz-relay/src/state.rs` —
      `disconnect_pubkey_clusterwide` / `disconnect_community_clusterwide` are verified
      first-hand: BOTH fan out over the Redis `buzz:*:conn-control` channel, NOT over the
      mesh. This is the contrast that makes the node a networking-layer concept rather
      than a second copy of the crate node.
  Merged relationship targets confirmed present in `origin/launchpad` (grepped in the
    merged-id list AND read on disk): `implementation-crates-buzz-relay-mesh`,
    `architecture-deployment-multi-relay`, `layers-compute-mesh-compute`,
    `architecture-flows-huddle-audio`, `layers-data-redis-channel-pubsub`.

STEP 1  Create the node with schema-valid front matter and the Definition   [independent]
        Create `launchpad/docs/corpus/layers/networking/relay-mesh.md` (creating the
        `networking/` directory) with front matter per the batch brief: `id:
        layers-networking-relay-mesh`, `type: layers`, `status: draft`, `origin:
        launchpad`, `audiences` chosen honestly, plus the single permitted commit-only
        FACT recording `29ca9b189bd3f639ba09c972b57c70538c0860c6`. Body carries the title,
        the one-sentence definition, and the disambiguation against the MeshLLM homonym.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0
                   with the new file on disk, and `git cat-file -e
                   29ca9b189bd3f639ba09c972b57c70538c0860c6` exits 0 — which is what makes
                   that ledger entry a FACT rather than an unchecked assertion.

STEP 2  Write the concept: the two east-west planes, and what rides which  [needs 1]
        Write the substance — the mesh as the relay's second east-west plane, contrasted
        with the always-on Redis-mediated one; the ALPN-gated QUIC endpoint and attested
        membership that keep it invisible to clients; the three profiles; and the fencing
        law stated as a boundary (the mesh moves bytes, Redis decides who owns a session).
        Include one Mermaid diagram authored inline as text — never a linked image, since
        AGENTS.md records that every non-`.md` file under the corpus root is rejected
        today. Add one `evidence` entry per substantive claim, classified honestly.
        done when: validator exits 0; every claim in the body has a matching ledger entry
                   and every FACT's source was opened in this session (checked by reading
                   the ledger against the body, and listing the pairing in the report);
                   and no claim restates the crate node's module map or the deployment
                   node's chart knobs.

STEP 3  Write Use cases and Boundary/Scope, and declare relationships       [needs 2]
        Write the "Why this matters" section (grounded in the `huddle_audio_unavailable`
        gate — the client-visible capability horizontal scaling breaks without the mesh)
        and the Boundary/Scope section stating the split against all three neighbouring
        mesh nodes plus the pairing relay. Declare `relationships` as `references` edges
        to the five merged ids listed under ALREADY TRUE, and to nothing else.
        done when: validator exits 0; every `relationships[].target` appears in
                   `git ls-tree -r --name-only origin/launchpad --
                   launchpad/docs/corpus` as an id on a merged file (re-checked, not
                   trusted from the ALREADY TRUE list); and no target is a Feature #609
                   sibling.

STEP 4  Write Scope and omissions, both halves                              [needs 3]
        Write the required scope-and-omissions section carrying the two distinct things
        AGENTS.md step 8 demands: (a) what this node does not cover and who owns it, as a
        table; and (b) separately, what was expected to be verified and could not — at
        minimum, that no live multi-pod mesh was exercised, and that the repository has NO
        integration or e2e test for the relay mesh (`crates/buzz-test-client/tests/` holds
        only `e2e_mesh_llm.rs`, which is the unrelated MeshLLM subsystem).
        done when: validator exits 0, and the section names at least one thing looked for
                   and not found, stated as a gap rather than as silence.

STEP 5  Audit the finished node against its own ledger, then stamp and commit [needs 4]
        Re-read the node against `templates/concept.md`'s required sections and against
        the issue's Definition of Done, line by line: exactly one commit-only FACT, every
        FACT opened, every INFERENCE carrying `confidence`, every TEAM_KNOWLEDGE carrying
        `provided_by` and no `confidence`, one idea only, no duplicated canonical content
        from the three neighbouring nodes. Fix what the audit finds.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0;
                   `grep -c '^      - "commit ' launchpad/docs/corpus/layers/networking/relay-mesh.md`
                   PRINTS `1` (read the printed count — `grep -c` exits 1 on a zero count);
                   `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
                   -p "test_*.py"` ends `OK` when run as the SOLE command in its own
                   foreground call with `timeout: 600000` (a backgrounded run prints OK and
                   writes NO stamp); and `git commit -s` succeeds in a SEPARATE call.

PARALLEL  None. All five steps edit the same single file, so they are sequential
          regardless of how unrelated they look. The issue's Definition of Done caps this
          task at exactly one hand-authored document, so there is no second artefact to
          fan out to.

GATES     Self re-read against the Definition of Done after STEP 5 — self-run, therefore
          NOT independent, and the report must say so plainly. `review-tests` does not
          apply: the diff adds one Markdown node and one plan file and modifies no test
          (STEP 5 *runs* the existing corpus suite; it does not change it). `qa` does not
          apply: no runtime interface changes. Per the batch brief this branch is NOT
          pushed and NO PR is opened — the orchestrator integrates the commit.

BUDGET    STEP 2. Three merged nodes already describe this crate from three altitudes, so
          the risk is not getting the facts wrong — it is writing a fourth paraphrase of
          them. The time goes into holding the networking-layer question ("what does a
          client get, and over which plane") and cutting anything that answers the crate
          question or the deployment question instead.

OPEN      Whether `operator` belongs in `audiences`. Resolved here as YES: `BUZZ_MESH`,
          `BUZZ_MESH_BIND_ADDR`, `BUZZ_HUDDLE_AUDIO_AVAILABLE` and `GET /_mesh` are
          operator-facing seams, and whether a deployment forms a mesh at all is an
          operator's decision. `reviewer` is resolved as NO — the three neighbouring mesh
          nodes carry it, but this node states no rule a reviewer holds at a pull request,
          so including it would be padding rather than an addressee. Final audiences:
          `agent`, `developer`, `operator`. A one-line change if a later standard
          disagrees.

LEFT OUT  Any edge to a Feature #609 sibling. None of the other 35 nodes is merged; a
          `relationships[].target` naming an id no loaded node carries validates locally
          off this branch's own tree and is a hard error in CI on `launchpad`.

          The crate's internals (module map, `MeshError` variants, per-file test lists) —
          `implementation-crates-buzz-relay-mesh` owns those and this node links to it.

          The Helm chart, replica counts, HPA/PDB and the install-time Redis guard —
          `architecture-deployment-multi-relay` owns those.

          A second hand-authored corpus document of any kind, including one for the
          Redis-mediated cross-pod connection-control plane that surfaced while gathering
          evidence. That is a candidate follow-up task reported to the orchestrator, not
          folded in here.
