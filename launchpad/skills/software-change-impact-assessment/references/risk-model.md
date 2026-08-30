# Qualitative Risk Model

Choose `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL` from the combined evidence; never from commit/file count alone.

- **LOW:** limited, reversible, well-evidenced change; no material security, data, interface, operational, or downstream concern; routine verification is proportionate.
- **MEDIUM:** bounded functional/dependency/toolchain/operational effect, or meaningful uncertainty/overlap; focused verification required.
- **HIGH:** security or trust-boundary change, breaking interface/schema/runtime change, substantial downstream semantic conflict, broad blast radius, difficult verification, or multiple medium drivers.
- **CRITICAL:** credible severe security, privilege, irreversible data, or safety/availability impact with high consequence and insufficient mitigation/evidence. Use sparingly and explain the trigger.

Consider significance, affected-system criticality, security, supply chain, downstream overlap, semantic/policy conflict, blast radius, reversibility, verification difficulty, and uncertainty. Counter-evidence can lower risk; missing evidence increases uncertainty and may raise risk, but must not be treated as proof of harm.

Explain the dominant drivers in prose. A qualitative table is useful; an opaque numeric score is not required.
