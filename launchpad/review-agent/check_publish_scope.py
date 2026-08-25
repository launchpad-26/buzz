"""STEP 9 control: the publish workflow's credential is narrow, proven live.

Three assertions, because each alone is weak.

STATIC parses the workflow YAML and checks permissions, trigger, and the
absence of a checkout `ref:` override -- runs anywhere, no token needed, and
catches a later widening before it ever reaches a live credential. Every
static assertion here is proven against a MUTATED copy of the real document,
not only against the real one: a check never observed failing has not been
shown to test anything.

LIVE attempts one contents write -- create a ref -- with the workflow's own
token, and asserts HTTP 403. Any other outcome is FAIL, including success,
404, and a rate-limit error: treating "some error happened" as proof of
absent permission is fail-open, and would report PASS on a network blip.

IDENTITY asserts the login publish.py was configured with is the login the
credential actually posts as, read off post_or_update's own third return
element -- the only place the live identity exists.

Both LIVE and IDENTITY report SKIP, never PASS, unless GITHUB_WORKFLOW names
the publish workflow. #120's containment-controls workflow also carries a
real token with contents: read -- a ref-create under THAT token 403s too, so
a guard keyed only on "a token exists" would let this control report PASS
having measured the wrong credential entirely. A control that passes under
the wrong token is not a weak control; it is a false one.
"""

from __future__ import annotations

import copy
import os
import subprocess
import sys
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "launchpad-review-agent-publish.yml"

#: Must match the workflow's own `name:` key exactly -- this is the guard the
#: live half keys on, not merely "a token exists".
PUBLISH_WORKFLOW_NAME = "launchpad — review agent publish"

failures: list[str] = []


def check(ok: bool, label: str) -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {label}")
    if not ok:
        failures.append(label)


def skip(label: str, reason: str) -> None:
    print(f"SKIP  {label} — {reason}")


def _on_key(doc: dict):
    """`on:` parses as the boolean True in YAML 1.1 unless quoted."""
    return True if True in doc else "on"


def static_violations(doc: dict) -> list[str]:
    """Every reason ``doc`` fails the static half. Empty means it passes."""
    violations: list[str] = []

    triggers = doc.get(_on_key(doc), {}) or {}
    if not (isinstance(triggers, dict) and "pull_request_target" in triggers):
        violations.append("does not trigger on pull_request_target")
    if isinstance(triggers, dict) and "pull_request" in triggers:
        violations.append("also triggers on plain pull_request")

    perms = doc.get("permissions", {})
    if perms != {"contents": "read", "pull-requests": "write"}:
        violations.append(f"permissions is not exactly contents:read, pull-requests:write (got {perms})")

    jobs = doc.get("jobs", {}) or {}
    for jname, jbody in jobs.items():
        if "permissions" in (jbody or {}):
            violations.append(f"job {jname!r} overrides permissions")
        for step in (jbody or {}).get("steps", []) or []:
            if str(step.get("uses", "")).startswith("actions/checkout"):
                ref = (step.get("with") or {}).get("ref")
                if ref and ("pull_request.head" in str(ref) or "head.sha" in str(ref)):
                    violations.append(f"job {jname!r} checkout sets ref: {ref!r}")

    return violations


def run_static_half() -> dict | None:
    if not WORKFLOW.exists():
        check(False, f"workflow exists at {WORKFLOW}")
        return None

    try:
        import yaml
    except ImportError:
        skip("static checks", "PyYAML not installed")
        failures.append("static checks skipped: no PyYAML")
        return None

    doc = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))

    real_violations = static_violations(doc)
    check(not real_violations, f"real workflow passes the static half (violations: {real_violations})")

    # Mutation proofs. Each mutated copy must FAIL where the real document
    # passes, or the check above is not testing anything.
    contents_write = copy.deepcopy(doc)
    contents_write["permissions"] = {"contents": "write"}
    check(bool(static_violations(contents_write)), "mutation (contents: write) is caught")

    plain_trigger = copy.deepcopy(doc)
    on_key = _on_key(plain_trigger)
    triggers = plain_trigger[on_key]
    triggers["pull_request"] = triggers.pop("pull_request_target")
    check(bool(static_violations(plain_trigger)), "mutation (pull_request instead of _target) is caught")

    bad_ref = copy.deepcopy(doc)
    for job in bad_ref.get("jobs", {}).values():
        for step in job.get("steps", []) or []:
            if str(step.get("uses", "")).startswith("actions/checkout"):
                step["with"] = {"ref": "${{ github.event.pull_request.head.sha }}"}
    check(bool(static_violations(bad_ref)), "mutation (ref: pull_request.head.sha) is caught")

    return doc


def _in_publish_workflow() -> bool:
    return os.environ.get("GITHUB_WORKFLOW") == PUBLISH_WORKFLOW_NAME


def attempt_ref_create(repo: str, run_id: str) -> tuple[int, dict]:
    """Real transport: try to create a ref with the workflow's own token.

    NOT the literal string ``${{ github.run_id }}`` -- that is an Actions
    expression, interpolated by the workflow YAML and never by Python, so
    transcribing it here would produce a ref name containing spaces and
    braces, and GitHub answers on ref-name validity before it evaluates
    permissions -- the control would then fail for a reason that has
    nothing to do with scope.
    """
    ref_name = f"refs/heads/scope-probe-{run_id}"
    result = subprocess.run(
        [
            "gh", "api", f"repos/{repo}/git/refs", "-X", "POST", "-i",
            "-f", f"ref={ref_name}",
            "-f", "sha=0000000000000000000000000000000000000000",
        ],
        capture_output=True, text=True,
    )
    lines = result.stdout.splitlines()
    if not lines:
        return 0, {}
    status = int(lines[0].split()[1])
    blank = next((i for i, line in enumerate(lines) if line.strip() == ""), len(lines))
    body_text = "\n".join(lines[blank + 1 :])
    import json as _json

    body = _json.loads(body_text) if body_text.strip() else {}
    body["ref_name"] = ref_name
    return status, body


def run_live_half(probe=attempt_ref_create) -> None:
    if not _in_publish_workflow():
        skip(
            "live scope probe",
            f"GITHUB_WORKFLOW is {os.environ.get('GITHUB_WORKFLOW')!r}, not the publish workflow",
        )
        return

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        skip("live scope probe", "no GITHUB_TOKEN in the environment")
        return

    run_id = os.environ.get("GITHUB_RUN_ID")
    if not run_id:
        check(False, "live scope probe: GITHUB_RUN_ID is not set")
        return

    repo = os.environ.get("GITHUB_REPOSITORY")
    if not repo:
        check(False, "live scope probe: GITHUB_REPOSITORY is not set")
        return

    status, body = probe(repo, run_id)
    check(status == 403, f"contents-write probe returns 403 (got {status})")
    if status == 403:
        # Pasted into the PR as evidence of which credential was actually
        # measured, per this control's own reasoning -- not taken on trust.
        print(f"    GITHUB_WORKFLOW: {os.environ.get('GITHUB_WORKFLOW')!r}")
        print(f"    response body: {body}")
    if status == 200 or status == 201:
        ref_name = body.get("ref_name")
        if ref_name:
            subprocess.run(["gh", "api", f"repos/{repo}/git/{ref_name}", "-X", "DELETE"], capture_output=True)
        check(False, "live scope probe unexpectedly SUCCEEDED -- token is not narrow, ref deleted")


def run_identity_check(configured_login: str, observed_login: str | None) -> None:
    if not _in_publish_workflow():
        skip("identity check", "not running in the publish workflow")
        return
    if observed_login is None:
        skip("identity check", "no post_or_update response observed this run")
        return
    check(
        observed_login == configured_login,
        f"configured login {configured_login!r} matches the credential's actual login "
        f"{observed_login!r}",
    )


if __name__ == "__main__":
    run_static_half()
    run_live_half()
    run_identity_check(
        configured_login=os.environ.get("PUBLISH_CONFIGURED_LOGIN", "github-actions[bot]"),
        observed_login=os.environ.get("PUBLISH_OBSERVED_LOGIN"),
    )

    print(f"\n{len(failures)} failure(s)")
    sys.exit(1 if failures else 0)
