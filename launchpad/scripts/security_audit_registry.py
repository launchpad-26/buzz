#!/usr/bin/env python3
"""The registry every #62 check plugs into.

Adding a check: write it in its own `security_audit_*_check.py` file exposing a
`run(repo_root) -> CheckResult`, import that function below, and append it to
CHECKS. Nothing else changes — not this file's structure, not the workflow YAML,
not security_audit.py.

#62's detection checks (secret material, ignore coverage, Actions hygiene,
settings attestation) land here as separate tasks; Actions hygiene and
settings attestation remain.
"""

from security_audit_agent_surface_check import run as agent_surface_secret_scan
from security_audit_ignore_coverage_check import run as ignore_coverage
from security_audit_secrets_check import run as secret_material_scan
from security_audit_selftest_check import run as harness_self_test
from security_audit_tracked_files_check import run as tracked_sensitive_files

CHECKS = [
    harness_self_test,
    secret_material_scan,
    ignore_coverage,
    tracked_sensitive_files,
    agent_surface_secret_scan,
]
