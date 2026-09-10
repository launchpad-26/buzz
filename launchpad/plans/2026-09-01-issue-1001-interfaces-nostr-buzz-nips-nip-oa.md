Issue #1001 — corpus node: interfaces/nostr/buzz-nips/nip-oa.md
Stated size: no Size line in the issue body → cap: 5 steps (per dispatch instructions)

ALREADY TRUE  (verified against git, not notes)
`launchpad/docs/corpus/interfaces/` does not exist anywhere in this worktree or on
`origin/launchpad` — this is a new subtree, not an update. `docs/nips/NIP-OA.md`
(150 lines) is the authoritative spec and defines an optional `auth` tag proving an
owner key authorized an agent key, without reassigning event authorship. The
canonical implementation is `crates/buzz-sdk/src/nip_oa.rs` (`compute_auth_tag`,
`verify_auth_tag`, `parse_auth_tag`). `node.schema.json`'s `type` enum has no
`interface` value; the correct value for an interface-shaped node is the combined
`interfaces-events` member, confirmed both in the schema file and in
`launchpad/docs/corpus/templates/interface.md`'s own "A note on `type`" section.
`git ls-tree -r origin/launchpad -- launchpad/docs/corpus` (schema/ excluded) shows
~90 nodes, none under `interfaces/` and none documenting NIP-OA; one existing node,
`architecture-flows-websocket-authentication` (id), documents the NIP-42
challenge/response flow that NIP-OA's `auth` tag rides inside of on the WebSocket
path — a valid `references` target.

STEP 1 — Gather and record evidence for every claim the node will make.  [independent]
Read `docs/nips/NIP-OA.md` in full; `crates/buzz-sdk/src/nip_oa.rs` (compute/verify/
parse + its test vectors); the call sites that consume it: `crates/buzz-relay/src/
handlers/auth.rs` (WebSocket NIP-42 AUTH path — tag extracted from the signed event,
ban cascades to a proven owner), `crates/buzz-relay/src/api/mod.rs`'s
`relay_members` module (`check_relay_membership`, `enforce_relay_membership`,
`extract_nip_oa_owner`, `materialize_nip_oa_owner`), `crates/buzz-relay/src/
config.rs` (`allow_nip_oa_auth` / `BUZZ_ALLOW_NIP_OA_AUTH`, default `false`),
`crates/buzz-relay/src/api/bridge.rs`, `media.rs`, `gifs.rs`, `workflows.rs` (the
`x-auth-tag` HTTP header path), `crates/buzz-relay/src/api/git/transport.rs` (git
smart HTTP — tag riding the signed NIP-98 event since git cannot carry a bare
header through the credential-helper protocol) and `crates/buzz-relay/src/handlers/
identity_archive.rs` (owner-consent verification reusing `verify_auth_tag`);
`crates/buzz-cli/src/lib.rs` (`BUZZ_AUTH_TAG` parse/verify + shorthand
normalization) and `crates/buzz-cli/src/client.rs` (`x-auth-tag` header attachment);
`crates/buzz-acp/src/relay.rs`, `lib.rs`, `setup_mode.rs`, `pool.rs` (ACP harness
attach/verify/detect); `crates/git-credential-nostr/tests/integration.rs` (NIP-OA
tag included in signed git-push events, malformed tag fails closed).
done when: every file above has been opened in this session and the specific
line(s)/symbol backing each planned evidence entry is noted.

STEP 2 — Draft the corpus node.  [needs 1] ← RUNS HERE
Create `launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-oa.md` with schema-valid
front matter (`id: interfaces-nostr-buzz-nips-nip-oa`, `type: interfaces-events`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`, one
`evidence` entry per claim classified FACT/INFERENCE/TEAM_KNOWLEDGE per
`node.schema.json`'s conditional rules, one `relationships` entry —
`references` → `architecture-flows-websocket-authentication`, confirmed present on
`origin/launchpad`). Body follows `templates/interface.md`'s required sections
(interface description, operations table, contract and stability, boundary
statement, relationships, scope and omissions) and separately satisfies every
Definition-of-done bullet from issue #1001: inputs/messages, outputs/responses,
error/rejection behavior, authentication/authorization, versioning/compatibility,
ordering/idempotency, a link to the authoritative spec (`docs/nips/NIP-OA.md`), and
at least one valid + one failure example (the spec's own test vectors).
done when: the file exists, every required section is present, and no evidence
entry cites a source that was not opened in Step 1.

STEP 3 — Validate the node against the corpus schema.  [needs 2]
Run `python3 launchpad/project-intelligence/corpus/validate.py` from the worktree
root. Fix any `FAIL` line the new node itself causes and re-run; a `FAIL` on an
unrelated pre-existing node is reported as a finding, not silently patched.
done when: the command exits `0`.

STEP 4 — Earn the commit gate.  [needs 3]
Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` as the sole command in its own tool call.
done when: the command prints `OK` and exits `0`.

STEP 5 — Commit.  [needs 4]
In a separate tool call from Step 4, `git add` the node and this plan file, then
`git commit -s -m "docs(corpus): document Buzz NIP-OA interface (#1001)"`. Do not
push, open a PR, or use `--no-verify`.
done when: `git log -1 --format=%H` shows a new commit on
`task/1001-interfaces-nostr-buzz-nips-nip-oa` containing exactly those two files.

PARALLEL: none of these steps can run as separate subagents — each depends on the
previous step's output (evidence feeds the draft, the draft must exist before
validation, validation must pass before the test gate, the gate must print `OK`
before commit) and all touch the same worktree. Step 1 is internally
`[independent]` only in the sense that no earlier step in this plan produces it.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit `0`
(Step 3) — this is the only automated corpus-content check. `python3 -m unittest
discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print
`OK` before the commit gate accepts it (Step 4). No `review-*` skill runs in this
session — per this corpus batch's established convention (see e.g. the #690
corpus-doc plan), adjudication and cross-model final review are deferred to the
batch owner. `qa` explore mode does not apply — this is a documentation-only
change with no runtime interface to exercise.

BUDGET: Step 2 is the step most likely to eat the budget — NIP-OA's `auth` tag is
consumed by seven-plus call sites across `buzz-relay`, `buzz-cli`, `buzz-acp` and
`git-credential-nostr`, and reconciling all of it into one non-duplicating interface
node (versus restating each call site) is the actual difficulty, not the front
matter.

OPEN: the issue does not say whether the node should scope to the SDK's
compute/verify/parse contract alone or to the full relay/CLI/ACP delegation surface
built on top of it. This plan scopes to the full delegation surface, because
`docs/nips/NIP-OA.md` itself defines owner, agent, relay and client behavior
together as one NIP, and splitting the SDK functions out as their own node would
leave the relay-membership-delegation and ban-cascade behavior — which is where
most of the interesting contract and stability claims live — undocumented or
duplicated elsewhere. Flagged here rather than narrowed silently.

LEFT OUT: no relationship to any other Nostr NIP the spec cites (NIP-26 prior art,
NIP-42 challenge/response, NIP-98 HTTP auth) beyond the one concrete `references`
edge identified above — none of those has its own corpus node yet, and the
Definition of done directs any newly discovered second concept to its own task
rather than folding it in. No attempt to also create sibling `buzz-nips` nodes for
other NIPs under `docs/nips/` (NIP-AA, NIP-FI, etc.) — issue #1001 scopes to NIP-OA
only, per its own Objective line naming this one file.
