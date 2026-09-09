# Issue #1193 — operations/administration/key-management.md

Stated size: issue #1193 carries no explicit Size line -> cap: 5 steps (the
dispatch brief for this batch caps every task in it at 5 steps: "this is one
document").

ALREADY TRUE: worktree `/home/serina/Launchpad/buzz/__worktrees/task-1193-administration-key-management` exists, is on branch `task/1193-administration-key-management`, tracks `origin/launchpad`, clean at HEAD `473205a7457b208455f188847bfb27b01aa83cac`. `launchpad/docs/corpus/operations/administration/key-management.md` does not exist (confirmed with `ls`, exit 2). No `operations/` subtree exists yet under `launchpad/docs/corpus/` at all. `launchpad/docs/corpus/templates/procedure.md` (id `corpus-template-procedure`) and `launchpad/docs/corpus/layers/configuration/secrets.md` (id `layers-configuration-secrets`) are both merged on `origin/launchpad` per `<SCRATCH>/existing-node-ids.txt`.

STEP 1  Gather evidence: read `crates/buzz-admin/src/main.rs` (`GenerateKey`, `AddMember`/`RemoveMember` owner guards), `scripts/ensure-local-relay-key.sh`, `Justfile`'s `bootstrap` recipe, `.env.example`, `crates/buzz-relay/src/config.rs` and `src/main.rs` (`RELAY_OWNER_PUBKEY`, `RELAY_OPERATOR_PUBKEYS`, `BUZZ_RELAY_PRIVATE_KEY`, the one-time `Config::from_env()` call and absence of any reload path), `crates/git-sign-nostr/README.md` + `src/lib.rs`, `crates/git-credential-nostr/README.md` + `src/lib.rs`, `.gitignore`, and `crates/buzz-acp/README.md`/`src/lib.rs` (`!rotate` — confirm it is ACP session rotation, not key rotation). done when: every path above has been opened and its relevant claim noted for the ledger. [independent] ← RUNS HERE

STEP 2  [needs 1] Write `launchpad/docs/corpus/operations/administration/key-management.md`: front matter (`id: operations-administration-key-management`, `type: operations`, `status: draft`, `origin: launchpad`, `audiences: [operator, developer, agent]`) and a body following `corpus-template-procedure`'s required sections — Overview; Before you start; numbered task sequences for provisioning the relay's signing key, generating an agent/CLI identity key, designating the relay owner/operators, and configuring git signing/credential keys; See also; Boundary; Relationships; Scope and omissions (stating plainly that no rotation command exists for any of these keys, and that `!rotate` is unrelated). One evidence entry per substantive claim, classified honestly, exactly one commit-only `FACT`, plus the closing entry naming the template. done when: the file exists with every Required section from the template present and every claim backed by an evidence entry.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repository root; fix whatever it reports and re-run. done when: the command exits 0.

STEP 4  [needs 3] Self-review the diff against every bullet of issue #1193's Definition of Done, including its four procedure-specific tail bullets, and re-open every `FACT` citation once more to confirm it still says what its statement claims. done when: each DoD bullet is checked against a named section of the body and no citation is found unsupported.

STEP 5  [needs 4] Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in its own tool call; confirm `OK`. Then, in a separate call, `git add -A && git commit -s -m "docs(corpus): document key management (#1193)"`. done when: the suite reports `OK` and a signed-off commit exists locally, with no push and no PR.

PARALLEL: none — single document, single task, steps are strictly sequential.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before STEP 5. `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report `OK`, run as its own Bash call, before committing. No push, no PR.

BUDGET: one document, one plan file, one commit. No code changes, no second corpus document.

OPEN: whether DB-managed `relay_operators` roster authorization (via the admin API, not a CLI key operation) belongs in this node or only gets a Boundary mention — resolved during drafting toward a Boundary mention, since it is an authorization concern layered on existing pubkeys rather than a key-generation or key-configuration procedure.

LEFT OUT: rotating or managing `BUZZ_GIT_HOOK_HMAC_SECRET`, `BUZZ_S3_ACCESS_KEY`/`BUZZ_S3_SECRET_KEY`, or `DATABASE_URL` credentials — secrets, but not Nostr keypairs, and already covered by `layers-configuration-secrets`, referenced rather than duplicated. Kubernetes/Helm secret provisioning for a remote-agent deploy — covered by `architecture-deployment-kubernetes` at deployment-topology altitude. Any second hand-authored corpus document.
