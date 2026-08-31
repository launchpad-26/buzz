Issue #797 — task: document capabilities/onboarding/first-community.md
No `Size` line on the issue -> cap: 5 steps (single-documentation-file task,
capped per batch dispatch brief).

ALREADY TRUE (verified against git and the worktree, not notes)
  - Worktree exists at __worktrees/task-797-first-community, branch
    task/797-first-community, HEAD == origin/launchpad ==
    cad6c375fdcc590158c1456c9fc7875f0f84a844 (git rev-parse confirms).
  - launchpad/docs/corpus/capabilities/ does not exist yet on origin/launchpad
    (git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus lists
    AGENTS.md, README.md, architecture/**, standards/**, schema/** only) --
    the target file is genuinely new, and there are no merged capability-shaped
    nodes yet to relate to.
  - launchpad/docs/corpus/templates/capability.md exists and is the template
    to follow (required sections: capability statement, maturity, boundary,
    relationships, scope and omissions). AGENTS.md and node.schema.json read
    in full this session.
  - Sibling tasks #796 (first-channel), #798 (first-identity), #799 (the
    overall onboarding capability) are separate, unmerged, hand-authored
    documents -- this task scopes strictly to the "which community/relay to
    join or create" step, not identity creation, not channel landing, not the
    onboarding capability as a whole.
  - Desktop code read this session: WelcomeSetup.tsx (the "Join or create a
    community" choice screen), communityOnboarding.tsx (the
    CommunityOnboardingTransaction state machine, FirstCommunityPage type),
    App.tsx (wires WelcomeSetup behind `community.needsSetup`),
    useCommunityInit.ts (needsSetup discriminated union, and the
    auto-connect-default-relay bypass for shared-identity/internal builds),
    HostedCommunityOnboarding.tsx (Builderlab-hosted community create/select),
    InviteRedeemForm.tsx, JoinPolicyNotice.tsx, MembershipDenied.tsx (join and
    denial-recovery surfaces). CommunityOnboardingFlow.tsx (profile/team-intro
    stages) was read to confirm it continues the *same* transaction after a
    community is chosen -- referenced as continuation, not re-described.

STEP 1 [independent] Confirm the front-matter contract choices: `type:
        capabilities` (node.schema.json's dedicated enum value, matching the
        capability.md template's own note on type), `status: draft` (no
        capability instance node exists yet to compare shipped-vs-draft
        against), `origin: launchpad`, `audiences: [agent, developer,
        reviewer]`. Confirm no `relationships` entry is legal: no
        architecture/interface/flow node id exists on origin/launchpad's
        corpus tree today for this capability to reference.
        done when: the decision is written directly into the front matter
        (no separate scratch file needed for a single-file task).

STEP 2 [needs 1] Write the body against the capability.md template's five
        required sections, scoped to first-community only: capability
        statement (join-or-create-first-community, stated as a product
        stakeholder would recognize it), maturity (shipped, cited to
        WelcomeSetup.tsx + App.tsx wiring), boundary (excludes identity
        creation/#798, channel landing/#796, the onboarding capability as a
        whole/#799, and post-first-run community management), relationships
        (declared: none, with the reasoning), scope and omissions (including
        the "Expected but not verified" list: no dedicated WelcomeSetup.tsx
        test file exists, and the hosted-community Builderlab sign-in path
        was read but not runtime-exercised).
        done when: launchpad/docs/corpus/capabilities/onboarding/first-community.md
        exists with complete front matter and body, every FACT citing a
        source opened this session.

STEP 3 [needs 2] Run the corpus validator.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py`
        exits 0 with zero NEW FAIL entries beyond the 21 pre-existing ones
        tracked in issue #1951 (confirmed by diffing the FAIL count/messages
        against a baseline run on origin/launchpad before this file existed).

STEP 4 [needs 3] Earn the commit gate:
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        as the sole command in its own call, confirm OK, then commit
        (git commit -s) the new document plus this plan file.
        done when: the commit exists locally with a signed-off message
        referencing #797; nothing pushed, no PR opened.

STEP 5 [needs 4] Self-review substitute (review-code/review-adjudicate
        deferred per batch mode): re-read the diff against #797's DoD
        checklist line by line, re-open every cited source to confirm it
        says what the statement claims, confirm no second canonical document
        was created, confirm validate.py's FAIL count did not grow.
        done when: findings are resolved in the file itself or explicitly
        noted as an "Expected but not verified" gap in the node's own body.

PARALLEL  None -- single-file task, all steps sequential (each edits or
          depends on the same target file).
GATES     Corpus validator (Step 3) and the unittest discover commit gate
          (Step 4) are the only automated gates for this batch mode;
          review-code/review-tests/review-adjudicate/review-final are
          explicitly deferred per the batch dispatch brief, replaced by the
          Step 5 self-review.
BUDGET    Step 2 (the body) is the highest-cost step -- the boundary section
          against three sibling capabilities needs precise, non-overlapping
          language so a future reader is not sent to the wrong document.
OPEN      Whether `status: draft` should later move to `active` once sibling
          capability nodes (#796/#798/#799) merge and the corpus has more than
          one capability instance to cross-check shape against -- not this
          task's call.
LEFT OUT  Documenting the profile/avatar/team-intro stages of
        CommunityOnboardingFlow.tsx in depth (belongs to #798/#799's
        territory, referenced here only as "what happens after the community
        is chosen"). Documenting the Builderlab hosted-account backend
        (hostedCommunityApi.ts) as its own architecture/interface node --
        out of scope, this capability only cites it as evidence of the
        "create a community" path's existence.
