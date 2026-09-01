Issue #1194 — task: document operations/administration/membership-management.md
Stated size: no `Size` line  →  cap: 5 steps (set by the shared batch brief for feature
  #618's document tasks: single documents against conventions already settled by #636)

Repo: launchpad-26/buzz · Branch: task/1194-administration-membership-management
Base: origin/launchpad
Worktree: /home/serina/Launchpad/buzz/__worktrees/task-1194-administration-membership-management

ALREADY TRUE  (verified against git and the filesystem at 473205a7457b208455f188847bfb27b01aa83cac)
  `git rev-parse HEAD` = 473205a7457b208455f188847bfb27b01aa83cac; working tree clean;
    branch tracks `origin/launchpad`.
  `launchpad/docs/corpus/operations/` does not exist yet — confirmed with `ls`. No
    `administration/` subdirectory and no `membership-management.md` file anywhere in the
    corpus (`find launchpad/docs/corpus -iname "*membership-management*"` → empty).
  `launchpad/docs/corpus/templates/procedure.md` (id `corpus-template-procedure`) is
    merged on `origin/launchpad` and prescribes: Overview, optional Before-you-start, one
    numbered task sequence per logical goal (≤8-10 steps, action-verb, fork with lettered
    sub-sequences when the task genuinely branches), See also, an explicit Boundary
    paragraph, Relationships, and Scope-and-omissions (per `AGENTS.md` step 8: what the
    node excludes + what was expected but unverifiable).
  Two capability nodes already canonically document the *design* of membership and must
    be linked, not restated: `capabilities-communities-community-members` (relay-wide
    membership: `relay_members`, NIP-43 kinds 9030-9032/13534/8000/8001/28936, invites)
    and `capabilities-channels-channel-membership` (per-channel membership:
    `channel_members`, NIP-29 kinds 9000/9001/9021/9022/39000-39002). A third,
    `capabilities-communities-community-roles`, documents the role model and explicitly
    names the `buzz-admin` CLI's `validate_role` rejection of "owner" as one of its own
    FACT citations — but only as *evidence for the role-authorization design*, not as an
    executed, step-by-step operator procedure. `capabilities-communities-community-
    provisioning` explicitly excludes the `/operator/communities/transfer` HTTP route
    from its own scope ("a future interface- or flow-shaped node, not yet drafted"),
    naming it as unclaimed territory this node may occupy. `layers-configuration-relay-
    configuration` already documents `RELAY_OWNER_PUBKEY`/`RELAY_OPERATOR_PUBKEYS`/
    `RELAY_OPERATOR_API_ORIGIN` validation semantics in full — this node links it rather
    than re-deriving the parse rules. All five ids are present in
    `<SCRATCH>/existing-node-ids.txt` (the merge-target snapshot), so all five are legal
    `references` targets.
  `crates/buzz-admin/src/main.rs` builds cleanly (`cargo build -p buzz-admin`) and its
    `add-member`/`remove-member`/`list-members`/`reconcile-channels` subcommands, their
    `--help` text, and two validation error paths (`--role owner` → exit 1 with the exact
    "role 'owner' cannot be set via CLI" message; an invalid pubkey → exit 1) were
    executed directly against the built binary — no live Postgres/Redis required for
    those code paths since they fail before `connect_member_services()`.
  `crates/buzz-cli` builds cleanly (`cargo build -p buzz-cli`) and `buzz channels
    {add-member,remove-member,members,join,leave} --help` were executed directly,
    confirming flag names against `crates/buzz-cli/src/lib.rs`'s `ChannelsCmd` enum.
  `crates/buzz-relay/src/api/operator.rs`'s `transfer_community` handler
    (`POST /operator/communities/transfer`) is real, wired code — NIP-98-signed via
    `buzz_auth`-backed `bridge::verify_bridge_auth_with_options`, gated on
    `RELAY_OPERATOR_PUBKEYS`, calling `buzz-db`'s `transfer_ownership` — and is the
    concrete crates/buzz-auth tie-in the batch brief pointed at for this subject matter.
  `NOSTR.md`, `ARCHITECTURE.md`, `deploy/compose/run.sh` and `.env.example` document the
    Docker Compose operator path (`./run.sh add-member|remove-member|list-members`,
    wrapping `docker compose exec relay buzz-admin ...`) and the required env vars
    (`DATABASE_URL`, `REDIS_URL`, `BUZZ_RELAY_PRIVATE_KEY`). `deploy/charts/buzz/README.md`
    documents `buzz-admin migrate` as a Helm-chart Job pattern but names no equivalent
    `kubectl exec` pattern for `add-member`/`remove-member`/`list-members` — a genuine gap
    to name in scope-and-omissions, not to paper over.
  `launchpad/AGENTS.md` is the governing contributor guide for this workspace; agents may
    write code and docs here (`/home/serina/Launchpad/CLAUDE.md`). Review gates available
    as skills: review-plan, review-code, review-tests, review-adjudicate, review-final, qa.

STEP 1  Record the evidence base and confirm the target is unclaimed          [independent]
        Re-confirm (already done above, restated here for the record) that
        `launchpad/docs/corpus/operations/administration/membership-management.md` does
        not exist, list every source path this node will cite, and note anything expected
        but not verifiable (no live Postgres/Redis in this environment, so the DB-backed
        halves of `buzz-admin add-member`/`remove-member`/the `/operator/communities/
        transfer` endpoint are read-and-executed-to-the-validation-boundary, not run
        end-to-end against a live database).
        done when: notes exist (scratchpad, not committed) listing the HEAD sha, every
        cited path, and the DB-execution gap; `git cat-file -e
        473205a7457b208455f188847bfb27b01aa83cac` exits 0.

STEP 2  Create the node with complete front matter and a skeleton body      [needs 1]  ← RUNS HERE
        `launchpad/docs/corpus/operations/administration/membership-management.md`, id
        `operations-administration-membership-management`, type `operations`, status
        `draft`, origin `launchpad`, audiences `operator` + `agent` + `reviewer`, one
        `evidence` entry per intended substantive claim (commit-only FACT for the
        revision, tool-result FACTs for the executed `--help`/error-path checks, code-path
        FACTs for `run.sh`/`operator.rs`/config validation, a TEAM_KNOWLEDGE entry for
        #1194's own DoD), and the five `references`/`implements` relationships named above.
        done when: `cd <worktree> && python3 launchpad/project-intelligence/corpus/
        validate.py` exits 0 and names the new node.

STEP 3  Write the community-membership and channel-membership task sequences [needs 2]
        Two numbered how-to task sequences following `corpus-template-procedure`'s
        skeleton: (a) add/remove/list a relay-wide (community) member via `buzz-admin`
        (Docker Compose `./run.sh` path, direct `docker compose exec` path, and the
        WebSocket NIP-43 kind:9030/9031 alternative for a live-signing operator), each
        step's evidence citing the executed command or the handler code; (b) add/remove/
        list a channel member via `buzz-cli channels {add-member,remove-member,members}`,
        naming the `BUZZ_PRIVATE_KEY`/`BUZZ_RELAY_URL` prerequisites and the elevated-role
        precondition the linked capability node already establishes. Each sequence states
        its own verification (re-run `list-members`/`members` and check the roster) and
        rollback (the inverse command; note the "wait ~1s between bulk adds" same-second
        collision caveat from `buzz-admin`'s own module doc).
        done when: validator exits 0; both sequences are present with numbered,
        action-verb steps ≤10 per sequence; every step's evidence entry names an executed
        command, a `--help` transcript, or an opened source file.

STEP 4  Write ownership transfer, See-also/Boundary/Relationships, Scope-and-omissions [needs 3]
        A third, shorter task sequence for `POST /operator/communities/transfer`
        (`RELAY_OPERATOR_PUBKEYS`/`RELAY_OPERATOR_API_ORIGIN` prerequisites, NIP-98
        signing, no CLI equivalent exists). Then the template's required Boundary
        paragraph (not the community-members/channel-membership/community-roles
        capability design, which this node links rather than restates; not a tutorial;
        not moderation/bans; not the undocumented Kubernetes exec path), the See-also
        list linking the five referenced nodes in prose, and Scope-and-omissions naming
        both the deliberate exclusions and the DB-execution/Kubernetes-path gaps from
        Step 1.
        done when: validator exits 0; the Boundary section names all three template-
        required exclusions plus the node-specific ones; the scope-and-omissions table's
        "expected but not verified" list matches Step 1's notes; no prose link points at
        an `operations/**` sibling path this Feature has not created.

STEP 5  Re-verify every FACT, run the corpus test suite as its own command, commit [needs 4]
        Re-open every cited source at the recorded revision and confirm it still supports
        its statement; re-run the validator; run the corpus unittest suite as the sole
        command in its own Bash call (earns the commit-gate stamp); commit with `-s`.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0;
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
        "test_*.py"` reports `OK` as the last segment of its own command; `git log -1
        --format=%B` shows a `Signed-off-by` trailer; `git status` is clean afterward.

PARALLEL  None. Steps 2-5 all edit the same single file in sequence, and step 1's notes
          are consumed by every later step. No subagent fan-out for this single-document
          task.

GATES     After STEP 5: this is a batch-authored corpus document produced by one agent in
          isolation, per the dispatch brief — no reviewer pass is run inside this task;
          the orchestrator's later integration PR is where `review-code`/`review-
          adjudicate`/cross-model review land, per the brief's own step 8 (report, don't
          self-merge or open a PR).

BUDGET    STEP 3 is most likely to overrun: three genuinely different operator surfaces
          (buzz-admin/run.sh, WebSocket NIP-43 admin events, buzz-cli channel commands)
          each have their own env-var prerequisites and exit-code conventions, and the
          template's 8-10-step-per-sequence guidance is a real constraint against
          reference-style completeness creeping in. The risk is drifting into restating
          the capability nodes' design content instead of the bare executable sequence —
          the settled boundary is procedure = ordered commands + verification + rollback,
          capability = why the authorization rule exists.

OPEN      1. **Whether the Kubernetes/Helm path deserves its own numbered task sequence
             or only a named gap.** No chart-documented `kubectl exec` equivalent to
             `run.sh add-member` was found (`deploy/charts/buzz/README.md` only calls out
             `buzz-admin migrate`). This plan treats it as a named gap in
             scope-and-omissions rather than inventing an unverified procedure, per the
             brief's explicit instruction not to fabricate operational steps the
             repository does not support.
          2. **Audiences.** `operator` is certain; whether `developer` also belongs
             (a developer running `buzz-cli channels add-member` locally against a dev
             relay is a real use of this same procedure) is left to drafting — leaning
             toward operator + agent + reviewer only, since the capability nodes already
             carry `developer` for the design-level audience.

LEFT OUT  - Restating the `relay_members`/`channel_members` schema, the NIP-43/NIP-29
            kind tables, or the authorization matrix (owner/admin/member permission
            rules). Owned by the three linked capability nodes.
          - The `buzz-admin deletions` whole-community-deletion control plane. A
            different concept (community lifecycle, not membership) — out of scope by
            the issue and by `AGENTS.md`'s "one node, one idea" rule. If this surfaces as
            worth its own procedure node, it is filed as a separate task, not folded in.
          - Moderation (bans/timeouts/reports) — a separate capability family
            (`capabilities/moderation/**`), out of scope here.
          - Any architecture/interface/flow-family node for these surfaces. None exists
            yet in this corpus for membership; this procedure links the capability layer
            only.
          - Building or exercising the Helm/Kubernetes deployment path end-to-end. Named
            as a gap (OPEN #1), not attempted.
