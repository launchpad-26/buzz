"""STEP 10 control: ten behavioural assertions covering #119's own done-criteria.

Recorded inputs, no network, no model. Every assertion below carries a stated
mutation that must break it -- a control never observed failing has not been
shown to test anything, and the temptation is to prove that only for the
assertions where it is easy, which leaves the load-bearing ones unproven.
`--prove-mutations` applies each mutation to a scratch copy of this directory
and re-runs the ONE assertion it targets there via subprocess; the real
checkout is never modified.

Every recorded input here is STEP 1's, by path: fixtures/reviews-listing.json
(the real single-page listing and the constructed two-page split) and
fixtures/review-lifecycle.json (the real POST/PUT/DELETE responses). None is
authored fresh for this step -- a hand-written listing would test this
plan's belief about `gh`, not the code.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

HERE = Path(__file__).parent
FIXTURES = HERE / "fixtures"

sys.path.insert(0, str(HERE))
import contain  # noqa: E402
import publish  # noqa: E402
import publish_render  # noqa: E402

failures: list[str] = []


def check(ok: bool, label: str, detail: str = "") -> bool:
    line = f"{'PASS' if ok else 'FAIL'}  {label}"
    if detail:
        line += f"\n      {detail}"
    print(line)
    if not ok:
        failures.append(label)
    return ok


def _marked(review: dict, body: str | None = None) -> dict:
    r = dict(review)
    r["body"] = body if body is not None else publish.MARKER + "\n" + r.get("body", "")
    return r


def _listing() -> dict:
    return json.loads((FIXTURES / "reviews-listing.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# (i) the event published is COMMENT, and no other event string exists.
# ---------------------------------------------------------------------------
def assertion_i() -> bool:
    src = (HERE / "publish.py").read_text(encoding="utf-8")
    has_comment = '"event=COMMENT"' in src
    no_approve = "APPROVE" not in src
    no_request_changes = "REQUEST_CHANGES" not in src
    ok = has_comment and no_approve and no_request_changes
    return check(
        ok,
        "(i) event is COMMENT and no other event string exists in the source",
        f"event=COMMENT present={has_comment}; APPROVE absent={no_approve}; "
        f"REQUEST_CHANGES absent={no_request_changes}",
    )


# ---------------------------------------------------------------------------
# (ii) a second run with a marker present issues PUT, never POST.
# ---------------------------------------------------------------------------
def assertion_ii() -> bool:
    listing = _listing()
    marked_page = [_marked(listing["recorded_single_page"][0])]
    calls: list[list[str]] = []

    def list_reviews(argv):
        return marked_page

    def submit(argv):
        calls.append(argv)
        return 200, {"id": marked_page[0]["id"], "user": {"login": "serina-mcfall"}}

    result = publish.post_or_update(
        1421, "launchpad-26/buzz", publish.MARKER + "\nsecond run",
        "serina-mcfall", list_reviews=list_reviews, submit=submit,
    )
    puts = [c for c in calls if "PUT" in c]
    posts = [c for c in calls if "POST" in c]
    ok = len(puts) == 1 and len(posts) == 0 and result[1] == "updated"
    return check(
        ok,
        "(ii) marker present -> PUT and no POST",
        f"puts={len(puts)} posts={len(posts)} result={result}",
    )


# ---------------------------------------------------------------------------
# (iii) find_existing paginates: page two is reachable only with --paginate.
# ---------------------------------------------------------------------------
def assertion_iii() -> bool:
    listing = _listing()
    two_page = listing["constructed_two_page"]
    page_1 = two_page["page_1"]
    page_2 = [_marked(r) for r in two_page["page_2"]]

    def transport(argv):
        if "--paginate" in argv:
            return page_1 + page_2
        return list(page_1)

    with_flag = publish.find_existing(1421, "launchpad-26/buzz", "serina-mcfall", list_reviews=transport)
    without_flag_reviews = transport(["gh", "api", "repos/x/pulls/1421/reviews"])
    marked_without = [r for r in without_flag_reviews if (r.get("body") or "").startswith(publish.MARKER)]

    reaches_page_two = with_flag[0] == page_2[0]["id"]
    unreachable_without_flag = marked_without == []
    ok = reaches_page_two and unreachable_without_flag
    return check(
        ok,
        "(iii) find_existing paginates -- page two reachable only with --paginate",
        f"with --paginate found id={with_flag[0]!r} (expected {page_2[0]['id']!r}); "
        f"without --paginate, marked reviews visible={len(marked_without)} (expected 0)",
    )


# ---------------------------------------------------------------------------
# Shared document builder for (iv), (v), (vi), (viii), (ix), (x).
# ---------------------------------------------------------------------------
NONCE = "the-run-nonce"
DIMS = ["paraphrase", "claim-vs-evidence", "line-anchored"]


def _make_report(dim, outcome="clean", findings=None, findings_count=0):
    return {
        "schema_version": 1, "dimension": dim, "pr": 1421, "merge_base_sha": "basesha",
        "head_sha": "headsha", "status": "complete", "outcome": outcome, "error": None,
        "findings": findings or [], "findings_count": findings_count,
        "completion_marker": f"BUZZ-DIMENSION-COMPLETE:{dim}:{NONCE}",
    }


def _make_stages():
    return [{"name": n, "status": "complete", "reason": None} for n in ["preflight"] + DIMS + ["adjudication"]]


def _make_containment():
    return {"findings": [], "states": {ep: "ok" for ep in contain.ENTRY_POINTS}}


def _finding(fid, severity, dim=DIMS[0], **overrides):
    base = dict(
        dimension=dim, severity=severity, anchor="line", file="a.rs", line=1,
        defect=f"defect {fid}", failure=f"failure {fid}", finding_id=fid,
        entry_point=None, evidence=None,
    )
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# (iv) severity order holds after an update with a NEW Blocker appended LAST.
# ---------------------------------------------------------------------------
def assertion_iv() -> bool:
    findings = [
        # finding_ids chosen so alphabetical order (what the identity-sort-key
        # mutation degrades to) DISAGREES with severity order -- otherwise the
        # mutation survives by accident regardless of which key is used.
        _finding("a-medium", "Medium"),
        _finding("b-low", "Low"),
        _finding("z-blocker-appended-last", "Blocker"),  # appended LAST in the array
    ]
    report = _make_report(DIMS[0], outcome="findings", findings=findings, findings_count=3)
    body = publish_render.render_body(
        publish.MARKER, [report], _make_stages(), _make_containment(), "h", "b", nonce=NONCE,
    )
    idx_blocker = body.index("Blocker")
    idx_low = body.index("Low", idx_blocker)
    ok = idx_blocker < idx_low
    return check(
        ok, "(iv) a Blocker appended last in the array still renders first",
        f"Blocker index={idx_blocker}, Low index={idx_low}",
    )


# ---------------------------------------------------------------------------
# (v) clean and incomplete inputs both produce a body, and the bodies differ.
# ---------------------------------------------------------------------------
def assertion_v() -> bool:
    clean_body = publish_render.render_body(
        publish.MARKER, [_make_report(d) for d in DIMS], _make_stages(), _make_containment(),
        "h", "b", nonce=NONCE,
    )
    incomplete_body = publish_render.render_body(
        publish.MARKER, [_make_report(d) for d in DIMS], _make_stages(), None,  # containment=None
        "h", "b", nonce=NONCE,
    )
    both_nonempty = bool(clean_body) and bool(incomplete_body)
    differ = clean_body != incomplete_body
    banner_present_only_where_expected = (
        "Incomplete" in incomplete_body and "Incomplete" not in clean_body
    )
    ok = both_nonempty and differ and banner_present_only_where_expected
    return check(
        ok, "(v) clean and incomplete inputs both post, and the bodies differ",
        f"clean has 'Incomplete': {'Incomplete' in clean_body}; "
        f"incomplete has 'Incomplete': {'Incomplete' in incomplete_body}",
    )


# ---------------------------------------------------------------------------
# (vi) a 4-backtick evidence run fences at >=5 backticks; text after stays outside it.
# ---------------------------------------------------------------------------
def assertion_vi() -> bool:
    evidence = "before " + "`" * 4 + " after-marker-AFTER-FENCE-TEXT"
    finding = _finding(
        "f-evidence", "High", entry_point="pr_diff", evidence=evidence,
    )
    report = _make_report(DIMS[0], outcome="findings", findings=[finding], findings_count=1)
    body = publish_render.render_body(
        publish.MARKER, [report], _make_stages(), _make_containment(), "h", "b", nonce=NONCE,
    )
    fence = publish_render.review.fence_for(evidence)
    fence_long_enough = len(fence) >= 5
    escaped_present = contain.escape(evidence) in body
    # The closing fence must be followed by something -- proof the text after it
    # is not swallowed into an unterminated (too-short) code block.
    last_fence_idx = body.rfind(fence)
    text_follows = last_fence_idx != -1 and last_fence_idx + len(fence) < len(body)
    ok = fence_long_enough and escaped_present and text_follows
    return check(
        ok, "(vi) 4-backtick evidence fences at >=5 backticks, escaped, text after stays outside",
        f"fence length={len(fence)}, escaped_present={escaped_present}, text_follows={text_follows}",
    )


# ---------------------------------------------------------------------------
# (vii) a PUT that returns 403 raises and issues no POST.
# ---------------------------------------------------------------------------
def assertion_vii() -> bool:
    listing = _listing()
    marked_page = [_marked(listing["recorded_single_page"][0])]
    calls: list[list[str]] = []

    def list_reviews(argv):
        return marked_page

    def submit_403(argv):
        calls.append(argv)
        return 403, {"message": "forbidden"}

    raised = False
    try:
        publish.post_or_update(
            1421, "launchpad-26/buzz", publish.MARKER + "\nx", "serina-mcfall",
            list_reviews=list_reviews, submit=submit_403,
        )
    except RuntimeError:
        raised = True

    posts = [c for c in calls if "POST" in c]
    ok = raised and len(posts) == 0
    return check(
        ok, "(vii) a 403 PUT raises and issues no POST",
        f"raised={raised}, posts issued={len(posts)}",
    )


# ---------------------------------------------------------------------------
# Subprocess-level fake for driving publish.main() end to end offline.
# ---------------------------------------------------------------------------
def _fake_run(listing_reviews, post_response):
    """A stand-in for subprocess.run, dispatching on the real argv shape
    both _list_reviews and _submit build. Patches at the actual I/O boundary
    since post_or_update's transport parameters are bound to the real
    functions at def-time, not resolved by name when main() calls it.
    """
    calls: list[list[str]] = []

    def fake(argv, **kwargs):
        calls.append(argv)
        result = mock.Mock()
        if "--paginate" in argv:
            result.stdout = json.dumps(listing_reviews)
            result.returncode = 0
            return result
        # POST or PUT, run with -i appended by _submit
        status, body = post_response(argv)
        body_text = json.dumps(body)
        result.stdout = f"HTTP/2.0 {status} X\n\n{body_text}"
        result.returncode = 0
        return result

    return fake, calls


# ---------------------------------------------------------------------------
# (viii) an all-clean input POSTS through main(), exactly one write call.
# ---------------------------------------------------------------------------
def assertion_viii() -> bool:
    document = {
        "pr": 1421, "head_sha": "h", "merge_base_sha": "b",
        "stages": _make_stages(), "reports": [_make_report(d) for d in DIMS],
        "containment": _make_containment(), "nonce": NONCE,
    }
    fake, calls = _fake_run(listing_reviews=[], post_response=lambda argv: (200, {"id": 1, "user": {"login": "github-actions[bot]"}}))
    with mock.patch("publish.subprocess.run", side_effect=fake):
        with mock.patch("sys.stdin", __import__("io").StringIO(json.dumps(document))):
            rc = publish.main(["--repo", "launchpad-26/buzz"])
    writes = [c for c in calls if "-X" in c and ("POST" in c or "PUT" in c)]
    ok = rc == 0 and len(writes) == 1 and "POST" in writes[0]
    return check(
        ok, "(viii) an all-clean input posts through main() -- exactly one write call",
        f"exit={rc}, write calls={len(writes)}",
    )


# ---------------------------------------------------------------------------
# (ix) a foreign marked review is neither a PUT candidate nor a POST licence.
# ---------------------------------------------------------------------------
def assertion_ix() -> bool:
    listing = _listing()
    foreign = _marked(listing["recorded_single_page"][0])
    foreign["user"] = dict(foreign["user"])
    foreign["user"]["login"] = "some-outsider"
    document = {
        "pr": 1421, "head_sha": "h", "merge_base_sha": "b",
        "stages": _make_stages(), "reports": [_make_report(d) for d in DIMS],
        "containment": _make_containment(), "nonce": NONCE,
    }
    fake, calls = _fake_run(listing_reviews=[foreign], post_response=lambda argv: (200, {"id": 1, "user": {"login": "github-actions[bot]"}}))
    with mock.patch("publish.subprocess.run", side_effect=fake):
        with mock.patch("sys.stdin", __import__("io").StringIO(json.dumps(document))):
            rc = publish.main(["--repo", "launchpad-26/buzz", "--as", "github-actions[bot]"])
    writes = [c for c in calls if "-X" in c and ("POST" in c or "PUT" in c)]
    ok = rc != 0 and len(writes) == 0
    return check(
        ok, "(ix) foreign marked review -- neither PUT nor POST, main() exits non-zero",
        f"exit={rc}, write calls={len(writes)}",
    )


# ---------------------------------------------------------------------------
# (x) a clean listing (zero foreign count, not just "no match") still POSTS.
# ---------------------------------------------------------------------------
def assertion_x() -> bool:
    document = {
        "pr": 1421, "head_sha": "h", "merge_base_sha": "b",
        "stages": _make_stages(), "reports": [_make_report(d) for d in DIMS],
        "containment": _make_containment(), "nonce": NONCE,
    }
    fake, calls = _fake_run(listing_reviews=[], post_response=lambda argv: (200, {"id": 1, "user": {"login": "github-actions[bot]"}}))
    with mock.patch("publish.subprocess.run", side_effect=fake):
        with mock.patch("sys.stdin", __import__("io").StringIO(json.dumps(document))):
            rc = publish.main(["--repo", "launchpad-26/buzz", "--as", "github-actions[bot]"])
    writes = [c for c in calls if "-X" in c and "POST" in c]
    ok = rc == 0 and len(writes) == 1
    return check(
        ok, "(x) a clean (empty) listing still posts",
        f"exit={rc}, POST calls={len(writes)}",
    )


ASSERTIONS = {
    "i": assertion_i,
    "ii": assertion_ii,
    "iii": assertion_iii,
    "iv": assertion_iv,
    "v": assertion_v,
    "vi": assertion_vi,
    "vii": assertion_vii,
    "viii": assertion_viii,
    "ix": assertion_ix,
    "x": assertion_x,
}

#: (name, target file, find, replace) -- each must break EXACTLY the named assertion.
MUTATIONS = [
    ("i", "publish.py", '"event=COMMENT"', '"event=APPROVE"'),
    ("ii", "publish.py",
     "    if not login:\n        raise ValueError(\"find_existing requires a non-empty login\")\n"
     "    argv = [\"gh\", \"api\", f\"repos/{repo}/pulls/{pr}/reviews\", \"--paginate\"]\n"
     "    reviews = list_reviews(argv)\n"
     "    marked = [r for r in reviews if (r.get(\"body\") or \"\").startswith(MARKER)]\n"
     "    own = [r for r in marked if r.get(\"user\", {}).get(\"login\") == login]\n"
     "    foreign_count = len(marked) - len(own)\n"
     "    if not own:\n        return None, foreign_count\n"
     "    newest = max(own, key=lambda r: r[\"submitted_at\"])\n"
     "    return newest[\"id\"], foreign_count",
     "    return None, 0"),
    ("iii", "publish.py", '["gh", "api", f"repos/{repo}/pulls/{pr}/reviews", "--paginate"]',
     '["gh", "api", f"repos/{repo}/pulls/{pr}/reviews"]'),
    ("iv", "publish_render.py",
     "review.SEVERITY_ORDER.get(finding.get(\"severity\"), 9),\n"
     "        finding.get(\"dimension\") or \"\",\n"
     "        finding.get(\"file\") or \"\",\n"
     "        finding.get(\"line\") or 0,\n"
     "        finding.get(\"finding_id\") or \"\",",
     "finding.get(\"finding_id\") or \"\","),
    ("v", "publish_render.py",
     "    reasons = _incomplete_reasons(stages, reports, containment, nonce, all_findings)\n"
     "    if reasons:\n        lines.append(_render_incomplete_banner(reasons))",
     "    reasons = _incomplete_reasons(stages, reports, containment, nonce, all_findings)"),
    ("vi", "review.py",
     "def fence_for(evidence: str) -> str:",
     "def fence_for(evidence: str) -> str:\n    return '```'  # mutated: fixed fence\n"),
    ("vii", "publish.py",
     "    status, response = submit(argv)\n"
     "    if not (200 <= status < 300):\n"
     "        raise RuntimeError(f\"PUT on review {review_id} failed with status {status}\")\n"
     "    return review_id, \"updated\", response[\"user\"][\"login\"]",
     "    status, response = submit(argv)\n"
     "    if not (200 <= status < 300):\n"
     "        argv2 = [\"gh\", \"api\", f\"repos/{repo}/pulls/{pr}/reviews\", \"-X\", \"POST\", "
     "\"-f\", f\"body={body}\", \"-f\", \"event=COMMENT\"]\n"
     "        status2, response2 = submit(argv2)\n"
     "        return response2.get(\"id\"), \"created\", response2.get(\"user\", {}).get(\"login\")\n"
     "    return review_id, \"updated\", response[\"user\"][\"login\"]"),
    ("viii", "publish.py",
     "    if args.dry_run:\n        print(body)\n        return 0\n\n    pr = document.get(\"pr\")",
     "    if args.dry_run:\n        print(body)\n        return 0\n\n"
     "    if \"No confirmed findings\" in body and \"Incomplete\" not in body:\n"
     "        return 0  # mutated: a 'reasonable' optimisation that goes silent on a clean run\n\n"
     "    pr = document.get(\"pr\")"),
    ("ix", "publish.py",
     "    own = [r for r in marked if r.get(\"user\", {}).get(\"login\") == login]",
     "    own = list(marked)"),
    ("x", "publish.py",
     "    existing_id, foreign_count = find_existing(pr, repo, login, list_reviews=list_reviews)\n"
     "    if existing_id is not None:\n"
     "        return _put(repo, pr, existing_id, body, submit)\n"
     "    if foreign_count:\n"
     "        _refuse(foreign_count, login)\n"
     "\n"
     "    existing_id, foreign_count = find_existing(pr, repo, login, list_reviews=list_reviews)",
     "    existing_id, foreign_count = find_existing(pr, repo, login, list_reviews=list_reviews)\n"
     "    if existing_id is not None:\n"
     "        return _put(repo, pr, existing_id, body, submit)\n"
     "    _refuse(foreign_count, login)  # mutated: refuse unconditionally, not only when foreign_count\n"
     "\n"
     "    existing_id, foreign_count = find_existing(pr, repo, login, list_reviews=list_reviews)"),
]


def apply_mutation(root: Path, filename: str, find: str, replace: str) -> bool:
    path = root / filename
    src = path.read_text(encoding="utf-8")
    if find not in src:
        return False
    path.write_text(src.replace(find, replace, 1), encoding="utf-8")
    return True


def prove_mutations() -> int:
    print(f"{len(MUTATIONS)} mutations, each must break exactly its own assertion\n")
    mutation_failures = []
    for name, filename, find, replace in MUTATIONS:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "review-agent"
            shutil.copytree(HERE, root, ignore=shutil.ignore_patterns("__pycache__"))
            if not apply_mutation(root, filename, find, replace):
                print(f"FAIL  mutation {name:<6}could not apply -- the anchor has drifted in {filename}")
                mutation_failures.append(name)
                continue
            proc = subprocess.run(
                [sys.executable, str(root / "check_publish_single.py"), "--only", name],
                capture_output=True, text=True, cwd=root, timeout=60,
            )
            if proc.returncode != 0:
                print(f"PASS  mutation {name:<6}caught (assertion {name} failed under the mutant)")
            else:
                print(f"FAIL  mutation {name:<6}SURVIVED -- assertion {name} still passed")
                print(proc.stdout)
                mutation_failures.append(name)
    print(f"\n{len(mutation_failures)} surviving mutant(s)")
    return 1 if mutation_failures else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default=None, choices=list(ASSERTIONS))
    parser.add_argument("--prove-mutations", action="store_true")
    args = parser.parse_args()

    if args.prove_mutations:
        return prove_mutations()

    if args.only:
        ok = ASSERTIONS[args.only]()
        return 0 if ok else 1

    for name, fn in ASSERTIONS.items():
        fn()

    print(f"\n{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
