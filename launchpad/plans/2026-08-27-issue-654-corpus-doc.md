# Plan: issue #654 — corpus node architecture-containers-desktop

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and
`launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad`
(commit a44cf52fc740ebebbdd671427480d14f0bce0115); no
`architecture` node exists in the merged corpus yet; the target file
`launchpad/docs/corpus/architecture/containers/desktop.md` does not exist.

STEP 1 (RUNS HERE): Gather evidence — read `desktop/src-tauri/src/lib.rs`
(`run()` builder: plugins, invoke_handler, setup), `Cargo.toml` (Tauri 2,
buzz-core/persona/sdk/agent/voice crate deps, keyring), `tauri.conf.json`
(identifier, deep-link scheme, externalBin, CSP), `relay.rs` (relay URL
resolution/override), `app_state.rs` (in-memory key custody),
`secret_store.rs` / `identity_storage.rs` (OS keyring vs 0o600 file vs env
fallback), `managed_agents/runtime.rs` (BUZZ_PRIVATE_KEY injection into
spawned subprocesses), `media_proxy.rs` (localhost proxy, origin check),
`RELEASING.md` (desktop release lane) and `AGENTS.md`'s ecosystem table
(buzz-releases pipeline).

STEP 2: Write front matter (id `architecture-containers-desktop`, type
`architecture`, status `draft`, origin `launchpad`, audiences
`developer`/`operator`/`reviewer`/`agent` as warranted) and body against
`node.schema.json`, covering: container responsibility, technology and
ownership boundary; inbound/outbound interfaces and directly connected
containers/systems; deployment/data/security implications; links to
implementation paths without duplicating their detail. No `relationships`
— no sibling `architecture` node exists yet in the merged corpus at this
task's merge base.

STEP 3: Run `python3 launchpad/project-intelligence/corpus/validate.py`
from repo root; fix and re-run until exit 0.

STEP 4: Earn the verification stamp with
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole prior command, then commit the plan + target file in a separate
tool call.

PARALLEL: none — single hand-authored file, no fan-out.

GATES: `validate.py` must exit 0 locally before commit. The corpus
unittest suite above must report OK to earn the commit's verification
stamp. `review-adjudicate` and the cross-model review pass are deferred to
the batch owner's morning review — not run in this session.

BUDGET: single document, one sitting — no iteration expected beyond
validator fix-up cycles.

OPEN: the issue's DoD asks for "typed relationships appropriate to the
node" but also requires that a `relationships[].target` resolve to an
id already merged; today's merged corpus carries no other `architecture`
node, so appropriate here means none, per `AGENTS.md`'s explicit warning
against copying an "always none" justification forward without checking.
Whether a later `architecture/layers` or `architecture/containers/relay`
node should link back here is left for that node's own author.

LEFT OUT: no second canonical document; no changes to
`desktop/src-tauri` or any runtime behavior; no template invented (none
exists yet per `AGENTS.md`); no generated index files touched.
