#!/usr/bin/env python3
"""The registry every #62 check plugs into.

Adding a check: write it in its own `security_audit_*_check.py` file exposing a
`run(repo_root) -> CheckResult`, import that function below, and append it to
CHECKS. Nothing else changes — not this file's structure, not the workflow YAML,
not security_audit.py.

Empty except for the self-test today; #62's detection checks (secret material,
ignore coverage, Actions hygiene, settings attestation) land here as separate
tasks.
"""

from security_audit_selftest_check import run as harness_self_test
from security_audit_secrets_check import run as secret_material_scan

CHECKS = [
    harness_self_test,
    secret_material_scan,
]
