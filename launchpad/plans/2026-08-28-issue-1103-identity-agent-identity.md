# Plan: issue #1103 — document layers/identity/agent-identity.md

## ALREADY TRUE

- Confirmed `launchpad/docs/corpus/layers/identity/agent-identity.md` does not exist
  (`launchpad/docs/corpus/layers/` itself does not exist yet on `origin/launchpad`).
- Read `launchpad/docs/corpus/AGENTS.md` in full: one file is one node, `type` names
  the corpus **surface** (not the doc form), no template exists yet for `type: layers`
  (per AGENTS.md's own "no per-type template to follow" gap table), so this node is
  written directly against `node.schema.json` plus the shape borrowed from
  `templates/concept.md` (definition, boundary, related concepts, examples — which
  matches the issue's own DoD bullets almost verbatim).
- Read `launchpad/docs/corpus/architecture/context/ai-agent.md`
  (`architecture-context-ai-agent`, status `draft`) — an existing, merged sibling node
  that already covers the AI-agent actor at system-context altitude, including a claim
  that `KIND_AGENT_PROFILE` "carries... a reference to the agent's human owner."
  Re-verified this claim against current code (see below) and found it does **not**
  hold at the current revision: `KIND_AGENT_PROFILE`'s content is `channel_add_policy`
  only (`crates/buzz-relay/src/handlers/side_effects.rs:handle_agent_profile`); the
  owner is resolved from a NIP-OA `auth` tag (`BUZZ_AUTH_TAG`, verified via
  `buzz_sdk::nip_oa::verify_auth_tag`), falling back to `--agent-owner` config
  (`crates/buzz-acp/src/lib.rs:resolve_agent_owner`). This new node will not repeat
  that unverified claim and will describe the mechanism actually found in code, opened
  directly.
- Evidence gathered from source, opened directly this session:
  - `crates/buzz-acp/README.md` — "Generating Keys" (Nostr keypair = agent identity,
    minted via `buzz-admin generate-key`, registered via `add-member`), "Shared
    Identity" (N agent subprocesses share one Nostr bot identity), "Inbound Author
    Gate" (owner-only default, `agent_owner_pubkey`).
  - `crates/buzz-core/src/kind.rs` — `KIND_AGENT_PROFILE` (10100, replaceable),
    `KIND_MANAGED_AGENT` (30177, owner-authored, explicitly forbids carrying the
    agent's secret key or NIP-OA auth tag since world-readable), `KIND_PERSONA`
    (30175, author-only-unless-shared), `KIND_TEAM` (30176), `KIND_AGENT_ENGRAM`
    (30174, NIP-AE), `KIND_PRIVATE_MANAGED_AGENT` (30179, NIP-PMA, owner-encrypted).
  - `docs/nips/NIP-OA.md` — full text: an optional `auth` tag by which an owner key
    authorizes an agent key to publish under its own authorship (explicitly *not*
    NIP-26-style delegation/impersonation; event stays authored by `event.pubkey`).
  - `crates/buzz-acp/src/lib.rs:resolve_agent_owner` (~line 123) and
    `crates/buzz-relay/src/handlers/side_effects.rs:handle_agent_profile` (~line
    1170) — owner-resolution and profile-ingest code, opened directly.
  - `crates/buzz-persona/PERSONA_PACK_SPEC.md` — persona pack `.persona.md` supplies
    "identity + system prompt," distinct from the agent's Nostr keypair identity.
  - `launchpad/docs/corpus/architecture/containers/agent-runtime.md` (merged sibling)
    — states a live Buzz agent needs "a keypair, a NIP-OA auth tag, and a relay URL."
- Recorded revision for this node's provenance: `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`
  (`git rev-parse HEAD` in the isolated worktree, tip of `origin/launchpad` at fetch time).
- `check-plan.sh` was searched for repo-wide and does not exist at this revision;
  proceeding without it per the task's own fallback instruction.

## STEP 1 — Confirm scope and boundary against the existing `ai-agent` node

Re-read `architecture-context-ai-agent.md` end-to-end (done above) to draw a clean
boundary: that node covers the AI-agent actor at *system-context* altitude (which
external systems talk to Buzz and how); this node covers the *identity* concept
itself — what a Nostr keypair means as an agent's identity, how ownership is
attested (NIP-OA), how it differs from persona/team/human identity, and the kinds
that carry it. No duplication of the context node's diagram or actor table.

**Done when:** the boundary is written down in the new node's own body under a
"Boundary" / "Not this" section, naming the context node by relative path (no
`relationships` edge yet — its `id` is not confirmed present on `origin/launchpad`'s
loaded corpus at merge time until checked in Step 3).

## STEP 2 — Draft `launchpad/docs/corpus/layers/identity/agent-identity.md`

Front matter: `id: layers-identity-agent-identity`, `type: layers`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, reviewer]`. Evidence ledger:
one FACT per source opened above, each cited to the real file/line; the correction
about `KIND_AGENT_PROFILE` framed as its own FACT (what the content actually is)
plus an explicit note rather than silently dropping the earlier node's claim (that
node stays draft/unedited — out of scope for this task; correcting it is not this
task's job, only not repeating the error here).

Body sections (concept.md shape, since AGENTS.md provides no `layers`-specific
template): title + intro, **Definition** (one sentence: an AI agent's identity in
Buzz is its own Nostr keypair, indistinguishable on the wire from a human's),
boundary/non-goals (not persona, not team, not the ACP session, not human identity),
**Use cases** (why a reader needs this: understanding owner attestation, shared
multi-process identity, profile vs. private-managed-agent visibility), a short
**Comparison** table (keypair identity vs. `KIND_MANAGED_AGENT` public projection vs.
`KIND_PRIVATE_MANAGED_AGENT` owner-encrypted aggregate vs. `KIND_PERSONA`), links to
related implementation/spec files (prose links, since no sibling corpus node's `id`
is confirmed mergeable yet — see Step 3), and the required **Scope and omissions**
section.

**Done when:** the file exists, is non-empty, and every substantive sentence in the
body has a corresponding evidence-ledger entry.

## STEP 3 — Relationships check, then local validation

Check `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` for
which node ids are actually merged (not just present in this worktree) before
deciding on `relationships`. Add a `references` edge only to an id confirmed merged
there. Then run:

```
python3 launchpad/project-intelligence/corpus/validate.py
```

**Done when:** exit code 0, confirmed by checking `$?` explicitly, not just reading
stdout.

## STEP 4 — Test suite, then commit

Run, as the sole command in its own tool call:

```
python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"
```

Confirm `OK`. In a separate tool call, `git commit -s`. If a required commit-gate
stamp is missing, stop and report it as a finding rather than bypassing it.

**Done when:** commit created with `-s`, `git log -1` shows the `Signed-off-by`
trailer.

## STEP 5 — Verify, push, open draft PR

Re-read the committed diff against every DoD bullet in issue #1103 one by one.
Re-open every cited source once more to confirm the citation supports its
statement. Confirm no second hand-authored `.md` was created (only
`agent-identity.md`, plus this plan file). Re-run `validate.py`. Push the branch
and open the PR as a draft per the task's exact `gh pr create` invocation, body
stating `Closes #1103`, that `validate.py` and the corpus unittest suite passed,
that verification was self-review, and the deferred-review line.

**Done when:** PR URL is returned by `gh pr create` and printed in the final report.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 (Steps 3 and 5).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK` (Step 4), run as the sole command in its own tool call, before committing.
- `git commit -s` succeeds with the repo's real commit-gate stamp — no `--no-verify`, no touching the stamp file.

## OPEN

- Whether the existing `architecture-context-ai-agent` node's `KIND_AGENT_PROFILE`
  claim should itself be corrected is out of scope for #1103 (that node belongs to a
  different task/issue); this plan only avoids repeating the error in the new node.

## LEFT OUT

- No edit to `architecture-context-ai-agent.md` or any other existing corpus node.
- No `relationships` edge unless Step 3's `git ls-tree` check against
  `origin/launchpad` confirms the target id is actually merged there.
- No second hand-authored canonical document; any generated index changes (if the
  tooling produces them) are mechanical only.
