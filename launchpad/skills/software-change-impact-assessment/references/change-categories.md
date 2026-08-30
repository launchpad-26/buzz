# Change Categories

Use these as a coverage checklist; report relevant categories and mark material unassessed areas `UNKNOWN`.

- **functional:** new, changed, removed, default, failure, compatibility, deprecation, user-visible behaviour
- **architecture:** component boundaries, ownership, data flow, process/lifecycle, state, concurrency, trust boundaries
- **api / interfaces:** APIs, CLI, events, RPC, protocols, exported types, plugins, configuration contracts; classify compatibility
- **schema / data:** database/storage/cache/event/config schemas, migrations, validation, destructive or irreversible effects, backward/forward compatibility
- **configuration:** defaults, environment variables, feature flags, deployment/runtime settings
- **dependencies / supply_chain:** direct/transitive versions, lockfiles, sources/registries, Git dependencies, build/runtime role, licenses, findings, provenance
- **build / toolchain:** compiler/runtime/package manager, generated code, scripts, minimum versions, reproducibility, platforms
- **ci_cd:** workflow permissions, checkout, runners, environments, secrets, actions, release/artifact/deployment automation
- **security / authentication / authorization / networking:** identity, privilege, secrets, crypto, validation/parsing, code execution, exposure, audit, external input
- **deployment:** manifests, packaging, rollout assumptions, artifact generation
- **operations / observability:** resources, startup/shutdown, retries/timeouts, recovery, logs/metrics/traces/alerts, supportability
- **testing / developer_experience / documentation:** test coverage and contracts, local prerequisites, docs/ADRs and downstream policy context
- **downstream_overlap:** independently modified shared paths/components, consumers, assumptions, contradictions

No detected migration, scanner finding, or workflow file means only that the artifact was not detected; it does not prove no impact.
