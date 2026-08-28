Issue #1182 — task: document layers/security/trust-model.md

ALREADY TRUE  node.schema.json, launchpad/docs/corpus/AGENTS.md, and the threat-model
  template are merged on origin/launchpad (HEAD at 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5);
  no "trust-model" template exists (the templates directory has threat-model.md and
  concept.md but nothing scoped to WHO/WHAT is trusted); two topically related nodes
  already exist on disk in this worktree —
  architecture-principles-community-is-security-boundary and
  architecture-flows-websocket-authentication; and
  launchpad/docs/corpus/layers/security/trust-model.md does not exist.

STEP 1  Gather evidence for each trust level named in the issue (relay operator,
        community admin, community member, agent, external provider): read
        crates/buzz-relay/src/api/operator.rs (RELAY_OPERATOR_PUBKEYS allowlist,
        provision/archive/transfer_community, deployment-root control plane),
        crates/buzz-relay/src/handlers/moderation_authz.rs (ModerationAction,
        ModerationAuthority::{CommunityOwner,CommunityAdmin,ChannelRole}, admin
        guard rails against actioning the owner/fellow admins), crates/buzz-relay/
        src/handlers/auth.rs + crates/buzz-auth/src/nip42.rs (NIP-42 identity proof,
        NIP-OA owner-delegation cascade), crates/buzz-core/src/private_managed_agent.rs
        (NIP-PMA owner-encrypted agent config, kind gated off until CAS lands),
        crates/buzz-acp/README.md's Security guarantees + Tier-1/2/3 harness sections
        (BUZZ_MANAGED_AGENT identity key stripped/unoverridable, no install shell
        commands, can_auto_install always false), crates/buzz-media/src/auth.rs
        (verify_blossom_auth_event) and crates/buzz-core/src/network.rs (is_private_ip
        SSRF guard) for the external-provider/media boundary, and AGENTS.md's own
        camo-proxy note about third-party image hosts. Read the two existing
        architecture nodes above in full so this document can `references` them
        without duplicating their claims.
        done when: every claim in the finished document has a citation to a file
        actually opened above.

STEP 2  Write the front matter (id: layers-security-trust-model, type: layers,
        status: draft, origin: launchpad, audiences: [agent, developer, operator,
        reviewer], relationships: references toward the two existing on-disk
        architecture nodes only) and the body: scope/purpose (WHO/WHAT is trusted at
        each level, distinct from #1181's trust-boundaries process-boundary map and
        #1180's threat-model attack-surface analysis), a trust-level table (relay
        operator, community owner, community admin, community member, agent, external
        provider) naming what each is trusted to do and its enforcement point, and a
        scope-and-omissions section per AGENTS.md step 8.
        done when: the file exists and is schema-shaped.                [RUNS HERE]

STEP 3  Validate: `python3 launchpad/project-intelligence/corpus/validate.py` must
        exit 0 against the full corpus tree including the new file.
        done when: exit 0.

STEP 4  Earn the commit-verification stamp with
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        (run alone, in its own tool call), then commit the plan and the document
        together and open a draft PR against launchpad.
        done when: unittest reports OK, commit succeeds, PR is opened as draft.

PARALLEL  None — one document, one plan file, strictly sequential.

GATES     python3 launchpad/project-intelligence/corpus/validate.py (must exit 0).
          review-adjudicate and the cross-model final pass are explicitly deferred to
          the batch owner's review — not run here.

BUDGET    Evidence-gathering (STEP 1) is the step most likely to take the most time:
          five distinct trust levels span five different crates, and every FACT needs
          an opened source rather than a plausible-sounding one.

OPEN      Whether a sixth trust level (e.g. a git-object provider, distinct from
          Blossom media) deserves its own row is left to a future document rather than
          decided here — the issue names five levels explicitly and this document
          does not invent a sixth without evidence it is materially distinct.

LEFT OUT  Documenting the process/data-flow boundaries themselves (#1181's job) or an
          attack-surface/STRIDE analysis (#1180's job) — this document is scoped to
          WHO/WHAT is trusted, not where the boundaries sit or what could go wrong.
          Any second hand-authored corpus document. Editing AGENTS.md or the schema.
