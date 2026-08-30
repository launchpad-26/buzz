# Evidence Guidance

## Evidence states

For facts and conclusions use `CONFIRMED`, `STRONGLY_SUPPORTED`, `POTENTIAL`, `UNKNOWN`, or `NOT_APPLICABLE`. For sources use `AVAILABLE`, `UNAVAILABLE`, `INCOMPLETE`, `ERROR`, or `NOT_APPLICABLE`.

A claim is reproducible when another reviewer can identify the repository, SHA, path, relevant lines or diff, command, and command result. Prefer immutable SHAs over branch names. Preserve failed commands and scanner/test scope. Cite ADRs, policy, manifests, lockfiles, migrations, workflow files, and test output as applicable.

## Three-layer writing

- **Evidence:** directly observed repository/tool fact.
- **Interpretation:** what the fact indicates.
- **Assessment/uncertainty:** likely impact, confidence, and what remains unproven.

Example: `src/session.rs` changed upstream and downstream also changed session code (evidence); session lifecycle is an overlap area (interpretation); semantic incompatibility is possible and needs focused review, but runtime incompatibility is unproven (assessment/uncertainty).

Never turn unavailable dependency resolution, absent scanner output, or unrun tests into “no impact.”
