"""STEP 10 control: thirteen behavioural assertions covering #119's own done-criteria.

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


def _lifecycle() -> dict:
    return json.loads((FIXTURES / "review-lifecycle.json").read_text(encoding="utf-8"))


def _real_put_response() -> dict:
    """The real recorded PUT response body from STEP 1 -- genuinely measured,
    not authored from belief about the shape `_submit` parses.
    """
    return _lifecycle()["put"]["body"]


def _real_post_response() -> dict:
    return _lifecycle()["post"]["body"]


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
    real_review = listing["recorded_single_page"][0]
    marked_page = [_marked(real_review)]
    calls: list[list[str]] = []

    def list_reviews(argv):
        return marked_page

    real_put = _real_put_response()

    def submit(argv):
        calls.append(argv)
        return 200, real_put

    result = publish.post_or_update(
        1421, "launchpad-26/buzz", publish.MARKER + "\nsecond run",
        "serina-mcfall", list_reviews=list_reviews, submit=submit,
    )
    puts = [c for c in calls if "PUT" in c]
    posts = [c for c in calls if "POST" in c]
    single_ok = len(puts) == 1 and len(posts) == 0 and result[1] == "updated"

    # A submitted review can't be deleted, so once two of the agent's own
    # markers exist on one PR neither can be retired -- find_existing must
    # resolve to the NEWER one, never the older, or the body a human reads
    # last stays permanently stale. Older copy dated well before the real
    # recording's own submitted_at.
    older = _marked(real_review)
    older["id"] = 1
    older["submitted_at"] = "2020-01-01T00:00:00Z"
    newer = _marked(real_review)  # the real recording's own (later) timestamp

    def list_reviews_both(argv):
        return [older, newer]

    calls2: list[list[str]] = []

    def submit2(argv):
        calls2.append(argv)
        return 200, real_put

    result2 = publish.post_or_update(
        1421, "launchpad-26/buzz", publish.MARKER + "\nthird run",
        "serina-mcfall", list_reviews=list_reviews_both, submit=submit2,
    )
    targeted_newer = any(f"/{newer['id']}" in c[2] for c in calls2 if "PUT" in c)
    tie_break_ok = targeted_newer and result2[0] == newer["id"]

    ok = single_ok and tie_break_ok
    return check(
        ok,
        "(ii) marker present -> PUT and no POST; two own markers -> PUT targets the NEWER, not the older",
        f"puts={len(puts)} posts={len(posts)} result={result}; "
        f"tie-break targeted newer id={newer['id']!r}: {targeted_newer}, result2={result2}",
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
    idx_blocker = body.find("Blocker")
    idx_low = body.find("Low")
    ok = idx_blocker != -1 and idx_low != -1 and idx_blocker < idx_low
    return check(
        ok, "(iv) a Blocker appended last in the array still renders first",
        f"Blocker index={idx_blocker}, Low index={idx_low}",
    )


# ---------------------------------------------------------------------------
# (v) clean and incomplete inputs both produce a body, and the bodies differ.
# ---------------------------------------------------------------------------
def assertion_v() -> bool:
    # Both bodies declare an injected reviewer, so containment is the ONLY
    # difference between them. Without that, condition (11) marks both incomplete
    # and this assertion stops testing what it names -- which is exactly what
    # happened when (11) was added.
    reviewed = {"kind": "injected", "name": "recorded_reviewer"}
    clean_body = publish_render.render_body(
        publish.MARKER, [_make_report(d) for d in DIMS], _make_stages(), _make_containment(),
        "h", "b", nonce=NONCE, reviewer=reviewed,
    )
    incomplete_body = publish_render.render_body(
        publish.MARKER, [_make_report(d) for d in DIMS], _make_stages(), None,  # containment=None
        "h", "b", nonce=NONCE, reviewer=reviewed,
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
        # SYNTHETIC, not recorded: STEP 1's fixture holds a 422 DELETE but no
        # 403 PUT (this session's own PUT calls all returned 200). The shape
        # matters here only as much as post_or_update's own status check
        # (200 <= status < 300), which does not inspect the body at all.
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
            # Page-shaped, as `gh api --paginate --slurp` actually emits: an array
            # OF PAGES. Emitting the flat list here was what let the concatenated
            # -JSON defect survive every control -- see assertion (xi).
            result.stdout = json.dumps([listing_reviews])
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
    # An injected reviewer, so this really is the all-clean case its name claims.
    # Without it, condition (11) marks the body INCOMPLETE and the "goes silent on
    # a clean run" mutation this assertion exists to catch never even fires.
    document = {
        "pr": 1421, "head_sha": "h", "merge_base_sha": "b",
        "reviewer": {"kind": "injected", "name": "recorded_reviewer"},
        "stages": _make_stages(), "reports": [_make_report(d) for d in DIMS],
        "containment": _make_containment(), "nonce": NONCE,
    }
    fake, calls = _fake_run(listing_reviews=[], post_response=lambda argv: (200, _real_post_response()))
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
# (ix) a foreign marked review is not a PUT candidate, and does not deny us a POST.
# ---------------------------------------------------------------------------
def assertion_ix() -> bool:
    """Create-then-update, with a foreign marker present throughout.

    This assertion previously demanded the OPPOSITE -- that a foreign marked
    review make the run refuse to post at all. An independent review panel found
    the denial-of-service in that: the marker is public and PUBLISHING.md prints
    it, so anyone able to comment could paste it once and permanently prevent
    this agent from ever publishing its required review. The duplicate the
    refusal guarded against cannot occur, because find_existing matches on marker
    AND author.

    Both halves run here, in sequence, because the risk in relaxing a refusal is
    that the relaxed path now posts EVERY time -- a duplicate on run two is the
    failure this must rule out, not just "run one posted".
    """
    listing = _listing()
    foreign = _marked(listing["recorded_single_page"][0])
    foreign["user"] = dict(foreign["user"])
    foreign["user"]["login"] = "some-outsider"
    foreign["id"] = 999_001
    document = {
        "pr": 1421, "head_sha": "h", "merge_base_sha": "b",
        "reviewer": {"kind": "injected", "name": "recorded"},
        "stages": _make_stages(), "reports": [_make_report(d) for d in DIMS],
        "containment": _make_containment(), "nonce": NONCE,
    }

    # Run one: foreign marker only. Must CREATE ours.
    post_response = _real_post_response()
    fake, calls = _fake_run(listing_reviews=[foreign], post_response=lambda argv: (200, post_response))
    with mock.patch("publish.subprocess.run", side_effect=fake):
        with mock.patch("sys.stdin", __import__("io").StringIO(json.dumps(document))):
            rc1 = publish.main(["--repo", "launchpad-26/buzz", "--as", "github-actions[bot]"])
    posts1 = [c for c in calls if "-X" in c and "POST" in c]
    puts1 = [c for c in calls if "-X" in c and "PUT" in c]
    created_ok = rc1 == 0 and len(posts1) == 1 and len(puts1) == 0

    # Run two: the same foreign marker, plus the review run one created. Must
    # UPDATE ours in place -- never post a second one, and never target theirs.
    ours = _marked(listing["recorded_single_page"][0])
    ours["id"] = post_response["id"]
    ours["user"] = dict(ours["user"])
    ours["user"]["login"] = "github-actions[bot]"
    fake2, calls2 = _fake_run(
        listing_reviews=[foreign, ours], post_response=lambda argv: (200, _real_put_response())
    )
    with mock.patch("publish.subprocess.run", side_effect=fake2):
        with mock.patch("sys.stdin", __import__("io").StringIO(json.dumps(document))):
            rc2 = publish.main(["--repo", "launchpad-26/buzz", "--as", "github-actions[bot]"])
    posts2 = [c for c in calls2 if "-X" in c and "POST" in c]
    puts2 = [c for c in calls2 if "-X" in c and "PUT" in c]
    targeted_ours = all(f"/{ours['id']}" in c[2] for c in puts2)
    never_theirs = not any(f"/{foreign['id']}" in c[2] for c in puts2)
    updated_ok = rc2 == 0 and len(puts2) == 1 and len(posts2) == 0 and targeted_ours and never_theirs

    ok = created_ok and updated_ok
    return check(
        ok,
        "(ix) foreign marker -- does not deny creation, and run two updates OURS in place",
        f"run1 exit={rc1} posts={len(posts1)} puts={len(puts1)}; "
        f"run2 exit={rc2} posts={len(posts2)} puts={len(puts2)} "
        f"targeted_ours={targeted_ours} never_theirs={never_theirs}",
    )


# ---------------------------------------------------------------------------
# (x) a clean listing (zero foreign count, not just "no match") still POSTS.
# ---------------------------------------------------------------------------
def assertion_x() -> bool:
    document = {
        "pr": 1421, "head_sha": "h", "merge_base_sha": "b",
        "reviewer": {"kind": "injected", "name": "recorded_reviewer"},
        "stages": _make_stages(), "reports": [_make_report(d) for d in DIMS],
        "containment": _make_containment(), "nonce": NONCE,
    }
    fake, calls = _fake_run(listing_reviews=[], post_response=lambda argv: (200, _real_post_response()))
    with mock.patch("publish.subprocess.run", side_effect=fake):
        with mock.patch("sys.stdin", __import__("io").StringIO(json.dumps(document))):
            rc = publish.main(["--repo", "launchpad-26/buzz", "--as", "github-actions[bot]"])
    writes = [c for c in calls if "-X" in c and "POST" in c]
    ok = rc == 0 and len(writes) == 1
    return check(
        ok, "(x) a clean (empty) listing still posts",
        f"exit={rc}, POST calls={len(writes)}",
    )


# ---------------------------------------------------------------------------
# (xi) _list_reviews parses what `gh` actually prints, not a pre-flattened list.
# ---------------------------------------------------------------------------
def assertion_xi() -> bool:
    """The real transport, against real CLI-shaped output.

    Every other assertion here injects `list_reviews`, and the injected one
    returned a flat list -- so `_list_reviews`, the only code that ever parses
    `gh`'s actual stdout, was never exercised. `gh api --paginate` emits one bare
    JSON array PER PAGE, which is not a single JSON value: `json.loads` raises
    JSONDecodeError the moment a PR has a second page of reviews, and publication
    dies before it can PUT or POST. An independent review panel found it in code
    that ten assertions had already passed over.

    Asserts both halves: the argv carries `--slurp` (without it the output is
    unparseable no matter how it is handled), and page-shaped output flattens to
    every review across every page.
    """
    listing = _listing()
    two_page = listing["constructed_two_page"]
    page_1 = two_page["page_1"]
    page_2 = [_marked(r) for r in two_page["page_2"]]

    seen_argv: list[list[str]] = []

    def fake(argv, **kwargs):
        seen_argv.append(argv)
        result = mock.Mock()
        result.stdout = json.dumps([page_1, page_2])  # --slurp: an array of pages
        result.returncode = 0
        return result

    with mock.patch("publish.subprocess.run", side_effect=fake):
        found_id, foreign = publish.find_existing(1421, "launchpad-26/buzz", "serina-mcfall")

    slurp_ok = bool(seen_argv) and "--slurp" in seen_argv[0] and "--paginate" in seen_argv[0]
    reached_page_two = found_id == page_2[0]["id"]

    # The concatenated-array shape `--paginate` produces WITHOUT `--slurp` is not
    # decodable at all -- proving that is what makes the flag load-bearing rather
    # than decorative.
    concatenated = json.dumps(page_1) + json.dumps(page_2)
    try:
        json.loads(concatenated)
        undecodable = False
    except json.JSONDecodeError:
        undecodable = True

    ok = slurp_ok and reached_page_two and undecodable
    return check(
        ok,
        "(xi) _list_reviews parses real --paginate --slurp page output; without --slurp it cannot",
        f"--slurp in argv={slurp_ok}, found id={found_id!r} (expected {page_2[0]['id']!r}), "
        f"foreign={foreign}, un-slurped output undecodable={undecodable}",
    )


# ---------------------------------------------------------------------------
# (xii) a stub-reviewer run publishes INCOMPLETE; an injected finding reaches the body.
# ---------------------------------------------------------------------------
def assertion_xii() -> bool:
    """The false-clean blocker, both directions.

    The publish workflow invokes `run_dimensions.py`'s `main()`, which binds
    `default_reviewer` -- a stub returning `{"outcome": "clean", "findings": []}`
    for every dimension without reading anything. An independent review panel
    found that a successful run therefore published "No confirmed findings" as
    though a review had happened. A false clean is worse than no review: it is
    durable, indexed, and reads as a pass.

    Wiring a real dimension reviewer is #116's work and is not in this issue.
    What IS in scope is refusing to claim a clean pass the pipeline did not earn,
    so a stub-produced document renders INCOMPLETE with the stub named as the
    reason. The second half is the regression the panel asked for by name: inject
    a known finding and prove it reaches the published body -- without it, an
    "always INCOMPLETE" bug would satisfy the first half perfectly.
    """
    reports = [_make_report(d) for d in DIMS]
    stub_body = publish_render.render_body(
        publish.MARKER, reports, _make_stages(), _make_containment(), "h", "b",
        nonce=NONCE, reviewer={"kind": "stub", "name": "default_reviewer"},
    )
    stub_incomplete = "## Incomplete" in stub_body and "stub reviewer" in stub_body
    stub_not_clean = "No confirmed findings" not in stub_body

    # Absent is treated as stub, per the default-is-incomplete rule -- a document
    # that will not say what reviewed it has established nothing.
    absent_body = publish_render.render_body(
        publish.MARKER, reports, _make_stages(), _make_containment(), "h", "b", nonce=NONCE,
    )
    absent_incomplete = "## Incomplete" in absent_body

    # An injected reviewer's finding must reach the rendered body verbatim.
    known = _finding("F-INJECTED-1", "Blocker", defect="an injected dimension finding")
    reviewed_reports = [
        _make_report(DIMS[0], outcome="findings", findings=[known], findings_count=1),
        *[_make_report(d) for d in DIMS[1:]],
    ]
    reviewed_body = publish_render.render_body(
        publish.MARKER, reviewed_reports, _make_stages(), _make_containment(), "h", "b",
        nonce=NONCE, reviewer={"kind": "injected", "name": "recorded_reviewer"},
    )
    finding_reached = "an injected dimension finding" in reviewed_body
    not_stub_flagged = "stub reviewer" not in reviewed_body

    ok = (
        stub_incomplete and stub_not_clean and absent_incomplete
        and finding_reached and not_stub_flagged
    )
    return check(
        ok,
        "(xii) stub reviewer renders INCOMPLETE, never clean; an injected finding reaches the body",
        f"stub incomplete={stub_incomplete} not-clean={stub_not_clean} "
        f"absent incomplete={absent_incomplete} finding reached={finding_reached} "
        f"injected not stub-flagged={not_stub_flagged}",
    )


# ---------------------------------------------------------------------------
# (xiii) build_document records which reviewer produced it.
# ---------------------------------------------------------------------------
def assertion_xiii() -> bool:
    """(xii) is worthless if nothing ever sets the key it reads.

    Renders the two ends of the seam: the stub is recorded as a stub, and an
    injected callable is recorded as injected. Without this, `run_dimensions.py`
    could stop emitting `reviewer` entirely and every document would silently
    become "absent" -- which (xii) proves renders INCOMPLETE, so the pipeline
    would fail safe but for the wrong reason, and nobody would learn why.
    """
    sys.path.insert(0, str(HERE))
    import run_dimensions  # noqa: PLC0415

    def injected(document: str) -> dict:
        return {"outcome": "clean", "findings": []}

    stub = run_dimensions.reviewer_identity(run_dimensions.default_reviewer)
    real = run_dimensions.reviewer_identity(injected)

    stub_ok = stub["kind"] == run_dimensions.REVIEWER_STUB and stub["name"] == "default_reviewer"
    injected_ok = real["kind"] == run_dimensions.REVIEWER_INJECTED and real["name"] == "injected"

    ok = stub_ok and injected_ok
    return check(
        ok, "(xiii) build_document's reviewer identity distinguishes stub from injected",
        f"stub={stub}, injected={real}",
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
    "xi": assertion_xi,
    "xii": assertion_xii,
    "xiii": assertion_xiii,
}

#: (name, target file, find, replace) -- each must break EXACTLY the named assertion.
MUTATIONS = [
    ("i", "publish.py", '"event=COMMENT"', '"event=APPROVE"'),
    ("ii", "publish.py",
     "    argv = [\"gh\", \"api\", f\"repos/{repo}/pulls/{pr}/reviews\", \"--paginate\", \"--slurp\"]\n"
     "    reviews = list_reviews(argv)\n"
     "    marked = [r for r in reviews if (r.get(\"body\") or \"\").startswith(MARKER)]\n"
     "    own = [r for r in marked if r.get(\"user\", {}).get(\"login\") == login]\n"
     "    foreign_count = len(marked) - len(own)\n"
     "    if not own:\n        return None, foreign_count\n"
     "    newest = max(own, key=lambda r: r[\"submitted_at\"])\n"
     "    return newest[\"id\"], foreign_count",
     "    return None, 0"),
    ("iii", "publish.py",
     '["gh", "api", f"repos/{repo}/pulls/{pr}/reviews", "--paginate", "--slurp"]',
     '["gh", "api", f"repos/{repo}/pulls/{pr}/reviews", "--slurp"]'),
    ("iv", "publish_render.py",
     "review.SEVERITY_ORDER.get(finding.get(\"severity\"), 9),\n"
     "        finding.get(\"dimension\") or \"\",\n"
     "        finding.get(\"file\") or \"\",\n"
     "        finding.get(\"line\") or 0,\n"
     "        finding.get(\"finding_id\") or \"\",",
     "finding.get(\"finding_id\") or \"\","),
    ("v", "publish_render.py",
     "    reasons = _incomplete_reasons(stages, reports, containment, nonce, all_findings, reviewer)\n"
     "    if reasons:\n        lines.append(_render_incomplete_banner(reasons))",
     "    reasons = _incomplete_reasons(stages, reports, containment, nonce, all_findings, reviewer)"),
    ("vi", "review.py",
     "def fence_for(evidence: str) -> str:",
     "def fence_for(evidence: str) -> str:\n    return '```'  # mutated: fixed fence\n"),
    ("vii", "publish.py",
     "    status, response = submit(argv)\n"
     "    if not (200 <= status < 300):\n"
     "        detail = f\" ({response['parse_error']})\" if \"parse_error\" in response else \"\"\n"
     "        raise RuntimeError(f\"PUT on review {review_id} failed with status {status}{detail}\")\n"
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
    # (ix) now has two ways to fail, and each gets a mutation: matching on the
    # marker alone (so a foreign review is mistaken for ours and PUT onto), and
    # restoring the refusal (so a foreign marker denies us publication at all).
    ("ix", "publish.py",
     "    own = [r for r in marked if r.get(\"user\", {}).get(\"login\") == login]",
     "    own = list(marked)"),
    ("ix", "publish.py",
     "def _note_foreign(foreign_count: int, login: str) -> None:",
     "def _note_foreign(foreign_count: int, login: str) -> None:\n"
     "    raise RuntimeError(  # mutated: back to refusing -- the DoS the panel found\n"
     "        f\"refusing to post: {foreign_count} foreign marked review(s)\"\n"
     "    )"),
    # Mutation (x) must break assertion (x) -- "a clean, EMPTY listing still
    # posts". The old mutation here restored the unconditional refusal, which
    # after the foreign-marker fix is caught by (ix) instead, leaving (x) with no
    # mutation of its own. This one is the plausible off-by-one in its place:
    # treating "nothing marked yet" as "nothing to do".
    ("x", "publish.py",
     "    if foreign_count:\n"
     "        _note_foreign(foreign_count, login)\n"
     "\n"
     "    existing_id, foreign_count = find_existing(pr, repo, login, list_reviews=list_reviews)",
     "    if not foreign_count:\n"
     "        return None, \"skipped\", login  # mutated: an empty listing never posts\n"
     "\n"
     "    existing_id, foreign_count = find_existing(pr, repo, login, list_reviews=list_reviews)"),
    # The three fix-round controls. Each mutation restores the exact defect an
    # independent review panel found, so a regression reproduces the original bug
    # rather than merely failing somewhere nearby.
    ("xi", "publish.py",
     "    return _flatten_pages(json.loads(result.stdout))",
     "    return json.loads(result.stdout)  # mutated: back to parsing pages as one value"),
    ("xii", "publish_render.py",
     "    if not isinstance(reviewer, dict):",
     "    if False:  # mutated: stub-produced documents render clean again"),
    ("xiii", "run_dimensions.py",
     "    kind = REVIEWER_STUB if reviewer is default_reviewer else REVIEWER_INJECTED",
     "    kind = REVIEWER_INJECTED  # mutated: the stub claims to be a real reviewer"),
]


def apply_mutation(root: Path, filename: str, find: str, replace: str) -> bool:
    path = root / filename
    src = path.read_text(encoding="utf-8")
    if find not in src:
        return False
    path.write_text(src.replace(find, replace, 1), encoding="utf-8")
    return True


import re

_FAIL_LABEL_RE = re.compile(r"^FAIL\s+\(([a-zA-Z]+)\)")


def _failing_assertion_names(stdout: str) -> set[str]:
    """Which of the ten assertions' own FAIL lines appear in a full-suite run.

    Parses labels rather than trusting the exit code alone, because the exit
    code only says "something failed" -- the "exactly" in this step's own
    done-when needs to know WHICH one(s).
    """
    return {m.group(1) for line in stdout.splitlines() if (m := _FAIL_LABEL_RE.match(line))}


def prove_mutations() -> int:
    print(f"{len(MUTATIONS)} mutations, each must be caught by its own named assertion\n")
    mutation_failures = []
    for name, filename, find, replace in MUTATIONS:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "review-agent"
            shutil.copytree(HERE, root, ignore=shutil.ignore_patterns("__pycache__"))
            if not apply_mutation(root, filename, find, replace):
                print(f"FAIL  mutation {name:<6}could not apply -- the anchor has drifted in {filename}")
                mutation_failures.append(name)
                continue
            # Full suite, no --only: --only alone cannot see collateral
            # breakage. Verified empirically that mutation (ii) ("make
            # find_existing return None unconditionally" -- the plan's own
            # stated mutation) also breaks (iii), (vii) and (ix), since all
            # four exercise the same shared find_existing/post_or_update
            # code path. That is not a suite defect -- a mutation to
            # widely-shared code SHOULD break every assertion that depends
            # on it -- so the full failing set is reported for honesty, and
            # only "the named assertion did NOT fail" counts as survival.
            proc = subprocess.run(
                [sys.executable, str(root / "check_publish_single.py")],
                capture_output=True, text=True, cwd=root, timeout=60,
            )
            failing = _failing_assertion_names(proc.stdout)
            if name in failing:
                extra = sorted(failing - {name})
                note = f" (also broke: {extra})" if extra else ""
                print(f"PASS  mutation {name:<6}caught{note}")
            else:
                print(f"FAIL  mutation {name:<6}SURVIVED -- assertion {name} still passed")
                print(proc.stdout)
                mutation_failures.append(name)
    print(f"\n{len(mutation_failures)} surviving mutant(s)")
    return 1 if mutation_failures else 0


def _run_assertion_safely(name: str, fn) -> bool:
    """A mutation can make an assertion raise rather than merely return False
    (STEP 4's own reasoning about crashes vs incomplete banners applies here
    too) -- an uncaught exception must report as that assertion's own FAIL,
    not kill the whole run and leave prove_mutations() unable to tell which
    assertion (if any) actually caught the mutant.
    """
    try:
        return fn()
    except Exception as exc:  # noqa: BLE001 -- deliberately broad: any crash is a FAIL
        return check(False, f"({name}) CRASHED instead of failing cleanly", f"{type(exc).__name__}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default=None, choices=list(ASSERTIONS))
    parser.add_argument("--prove-mutations", action="store_true")
    args = parser.parse_args()

    if args.prove_mutations:
        return prove_mutations()

    if args.only:
        ok = _run_assertion_safely(args.only, ASSERTIONS[args.only])
        return 0 if ok else 1

    for name, fn in ASSERTIONS.items():
        _run_assertion_safely(name, fn)

    print(f"\n{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
