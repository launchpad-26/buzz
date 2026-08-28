Issue #671 — task: document architecture/deployment/local-development.md

ALREADY TRUE  node.schema.json and launchpad/docs/corpus/AGENTS.md are merged on
  origin/launchpad (confirmed at a44cf52fc740ebebbdd671427480d14f0bce0115); the target
  file launchpad/docs/corpus/architecture/deployment/local-development.md does not exist
  in this worktree.

STEP 1  Gather evidence for local-dev topology, service map, network/persistence/trust
        boundaries, and automation: Justfile (bootstrap/setup/relay/dev/down/reset/
        _ensure-services/_ensure-migrations), docker-compose.yml, .env.example,
        scripts/dev-setup.sh, scripts/dev-reset.sh, CONTRIBUTING.md's "Setting Up the
        Development Environment" section, crates/buzz-relay/src/main.rs (auto-migrate
        gate) and crates/buzz-relay/src/config.rs (bind/health/metrics port defaults).
        done when: every claim the body will make has an opened source noted for its
        evidence entry.

STEP 2  Write front matter (id: architecture-deployment-local-development, type:
        architecture, status: draft, origin: launchpad, audiences: [developer, agent,
        operator], evidence ledger with a commit-pinned provenance FACT plus one entry
        per substantive claim, no relationships — this is the first architecture/
        deployment node, nothing merged to point at) and the body: topology (single dev
        machine as the one execution node), container/service/data-store map, network
        boundaries (127.0.0.1-only compose ports vs. the relay's 0.0.0.0 bind), migration/
        persistence behavior (explicit `buzz-admin migrate` in dev vs. the BUZZ_AUTO_MIGRATE
        gate in main.rs), trust boundaries described without quoting any credential value,
        deployment automation as authority (Justfile/docker-compose.yml/.env.example
        linked, not restated), and failure/recovery (health-wait loop, `just down`,
        `just reset`/dev-reset.sh).
        done when: every DoD bullet and the category tail has a corresponding body
        section.  ← RUNS HERE

STEP 3  Validate: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.
        Fix and re-run until clean.
        done when: exit code 0 against the full corpus tree including the new file.

STEP 4  Commit the plan and the node (unittest suite run first, as its own command, to
        earn the verification stamp).
        done when: `git log -1` shows both files staged in one signed-off commit.

PARALLEL  None — one target file, one plan file, strictly sequential.

GATES     python3 launchpad/project-intelligence/corpus/validate.py (this session).
          review-adjudicate and the cross-model pass are deferred to the batch owner's
          morning review — not run here, per the issue's overnight-batch instructions.

BUDGET    STEP 2 is where time goes: honestly separating FACT (opened and read) from
          INFERENCE (reasoned, needs confidence) for claims like "the relay's default
          0.0.0.0 bind is a wider network surface than the compose services' 127.0.0.1
          ports" — that comparison is drawn from two FACTs but is itself a reasoned
          inference, not a fact in its own right.

OPEN      The issue's DoD asks the node to describe deployment "failure/recovery
          implications." Buzz's local-dev automation only covers infrastructure
          failure/recovery (services down, data wipe) — there is no documented
          recovery path for a corrupted local Postgres volume short of `just reset`
          (which deletes the data). That gap is real, not resolved here, and is named
          in the document's own scope-and-omissions section rather than papered over.

LEFT OUT  Any relationships edge — no other architecture/deployment node is merged to
          target. Staging/production deployment topology (Kubernetes via
          block-coder-tf-stacks) — this node is scoped to local development only, per
          the issue's own target path; staging/prod topology is a separate node.
          Editing docker-compose.yml, .env.example, Justfile, or any script this node
          cites — findings there are reported in the node's body, not fixed here.
