#!/usr/bin/env python3
"""Deterministic pre-review pass over a batch of pull requests. Issue #426.

WHAT THIS IS FOR

Reviewing a batch of PRs has two halves. One is judgement: is this claim true,
does the conclusion depend on this defect, is it wrong now or wrong later. The
other is bookkeeping applied identically to every PR: which reviews are stale,
which CI failures belong to this diff, am I even allowed to review this.

The second half is a fixed set of rules, so it belongs in a script. That is the
line ADR-0019 draws -- a deterministic script may gate a merge, a model verdict
may only annotate -- and it is the same extraction `pr_body_check.py` and
`adr_boundary_check.py` already did for their own rules.

WHAT IT DELIBERATELY DOES NOT DO

It emits no severity and no verdict on any claim. Across the review batches on
2026-08-21/22, five proposed blockers were demoted to High and one upheld; every
one turned on whether a document's conclusion depended on the defect. A script
guessing that would be the model-gating ADR-0019 forbids, dressed as automation.
`BriefingTests.test_the_briefing_states_no_severity_anywhere` asserts the absence.

It also posts nothing. The caller decides and acts, so this can run read-only.

WHY EACH RULE EXISTS

Every classifier below was applied by hand across those batches, and each one was
applied WRONGLY at least once. The cost is recorded here because a rule whose
failure nobody remembers gets removed as clutter.

  STALE / MISFILED reviews. Four PRs carried change-requests that had already
  been satisfied. #262's blockers were fixed at 03:21; the review restating them
  was submitted at 03:57, re-posting a body written at 01:38 against a head that
  had moved twice. Worse, #271's change-request was #275's review MISFILED --
  textually identical, down to a "same as #271's" self-reference that only makes
  sense sitting on the other PR. No change to #271 could ever have addressed it.
  Detected here by citation/diff mismatch rather than by comparing bodies,
  because the same body legitimately appears on a stacked pair.

  CI triage. #268's red CI was `setup-mold` timing out while fetching a linker,
  on a PR that changed one markdown file. #288's log printed four biome items
  first -- all warnings, all in files the PR never touched, inherited from
  upstream commits dated weeks earlier -- while the actual blocker, a file-size
  guard tripping at 1001 lines, sat forty lines further down. Reading the first
  recognisable failure would have cleared that PR.

  Independence. #265 contained a commit written in the very session that was
  about to review it. Caught by hand, one review too late to be free.

  Drift calibration. The expensive one. #374's headline "796 files" was reported
  REFUTED by a competent reviewer who ran the document's own command against the
  live `upstream/main` and got 912. Reconstructing the 67-commit point the
  document actually measured gave 796 exactly -- and 575/110/52/35 for every
  sub-total. A correct document nearly took a change-request because nobody
  pinned the tip. Handing reviewers the pinned SHA up front removes the trap.

USAGE

    python3 pr_review_batch.py --author tucktuck101 --author benmitchell11
    python3 pr_review_batch.py --review-required
    python3 pr_review_batch.py --pr 405 --pr 406 --json
    python3 pr_review_batch.py --pr 374 --calibrate f8692fa9b --commits 67

Requires `gh` on PATH and authenticated. Read-only: every `gh` call is a GET.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field

DEFAULT_REPO = "launchpad-26/buzz"

#: Substrings whose appearance in an ADDED diff line means private tooling has
#: leaked into a public repository. These live in a separate private repo; the
#: rule is to describe what a gate does, never to name its files. See #281.
DEFAULT_LEAK_PATTERNS = ("pr-gate", "git-safety", "verify-gate")

#: Trees upstream owns. `launchpad/AGENTS.md` section 3 bars cohort files here.
#: Note this only judges files that look like cohort documentation or tooling --
#: a PR editing `crates/` is upstream-shaped work, which is legitimate.
_UPSTREAM_ONLY_PREFIXES = ("docs/", "scripts/")

#: Failure-log signatures that mean the infrastructure broke, not the change.
_FLAKE_SIGNATURES = (
    "connection timed out",
    "read error (connection timed out)",
    "tar: error is not recoverable",
    "could not resolve host",
    "temporary failure in name resolution",
    "502 bad gateway",
    "503 service unavailable",
    "the runner has received a shutdown signal",
)

#: Steps that only fetch a toolchain. A failure inside one is never the diff's
#: fault, whatever the log says.
_TOOLCHAIN_STEPS = ("setup-mold", "rust-cache", "actions/cache", "setup-python",
                    "setup-node", "activate-hermit", "install tauri dependencies")

#: `path/to/file.ext:123` and `path/to/file.ext: 123`.
#:
#: The optional space matters and was missed on the first pass. Two formats
#: occur in real CI output: compilers and linters emit `lib.rs:276:15`, while
#: this repo's file-size guard emits `src-tauri/src/lib.rs: 1000 -> 1001`. A
#: regex requiring the digit to touch the colon sees only the first, which is
#: how a REAL failure on #288 was classified UNKNOWN.
_PATH_TOKEN = re.compile(r"(?<![\w/.:-])((?:[\w.-]+/)*[\w.-]+\.[A-Za-z]{1,6}):\s?\d+")


def parse_time(value):
    """An aware datetime, or None. Never raises.

    A classifier that dies on a malformed timestamp takes the whole batch with
    it. "Unknown" is a usable verdict; a traceback in the middle of twenty-two
    PRs is not.
    """
    if not value or not isinstance(value, str):
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def cited_paths(body):
    """File paths a review body cites as `path/to/file.ext:LINE`.

    Deliberately narrow. It must not match `#271` (an issue), `1.2.3` (a
    version) or a URL, because a false path makes a real review look misfiled --
    which is the most damaging wrong answer this script can give.
    """
    if not body:
        return set()
    cleaned = re.sub(r"https?://\S+", " ", body)
    return {match.group(1) for match in _PATH_TOKEN.finditer(cleaned)}


def is_misfiled(body, diff_paths):
    """True when a review body appears to be about a different pull request.

    Three conditions, all required, because a false MISFILED is the most
    damaging answer this script can give -- it tells an author to dismiss a
    review that may be perfectly valid.

      1. At least TWO distinct cited paths. One is not a pattern.
      2. None of them appear in this PR's diff.
      3. The body never names any of this PR's own files, even without a line
         number.

    Condition 3 exists because the first draft got this wrong on live data.
    Reviewing #374 -- a research note -- it reported the reviewer's genuine
    review as MISFILED because the only `path.ext:line` token in the body was
    `launchpad/ARCHITECTURE.md`, cited as CORROBORATING EVIDENCE for a quote,
    not as the site of a defect. Reviews legitimately cite files outside the
    diff; that is what checking a claim looks like. What #271's genuinely
    misfiled review had instead was several cited paths, all absent, and no
    mention anywhere of the file the PR actually changed.
    """
    cited = cited_paths(body)
    if len(cited) < 2 or not diff_paths:
        return False
    if cited & diff_paths:
        return False
    lowered = (body or "").lower()
    for path in diff_paths:
        if path.lower() in lowered:
            return False
        base = path.rsplit("/", 1)[-1].lower()
        if base and base in lowered:
            return False
    return True


@dataclass
class Verdict:
    state: str
    reason: str = ""

    def as_dict(self):
        return {"state": self.state, "reason": self.reason}


def classify_review(review, head_committed_at, diff_paths):
    """Classify one CHANGES_REQUESTED review. None for any other state.

    MISFILED is checked before STALE on purpose. A review that never applied to
    this PR cannot be "addressed by a later push", and reporting STALE would
    tell the author to expect it to clear on re-review. It never will.
    """
    if review.get("state") != "CHANGES_REQUESTED":
        return None

    body = review.get("body") or ""
    if is_misfiled(body, diff_paths):
        return Verdict(
            "MISFILED",
            f"cites {sorted(cited_paths(body))[:3]} and never names a file in "
            "this PR's diff",
        )

    submitted = parse_time(review.get("submittedAt"))
    head_at = parse_time(head_committed_at)
    if submitted is None or head_at is None:
        return Verdict("UNKNOWN", "could not read review or head timestamp")

    if submitted < head_at:
        return Verdict(
            "STALE",
            f"head moved after the review (review {submitted.isoformat()}, "
            f"head {head_at.isoformat()})",
        )
    return Verdict("CURRENT", f"review postdates the head commit ({submitted.isoformat()})")


#: Lines worth keeping out of a CI log. Everything else is setup and teardown.
_LOG_SIGNAL = re.compile(
    r"error|failed|failure|\bexit code\b|allowed \d+|lint/|✘|✖|"
    r"assertionerror|panicked|traceback|" + "|".join(
        re.escape(sig) for sig in ("connection timed out", "not recoverable")
    ),
    re.IGNORECASE,
)

#: Teardown chatter that matches _LOG_SIGNAL but never explains a failure.
_LOG_NOISE = re.compile(
    r"safe\.directory|orphan process|Post job cleanup|git-credentials|"
    r"includeif\.gitdir|Removing (?:SSH|HTTP|credentials)|--unset",
    re.IGNORECASE,
)


def relevant_log_lines(log_text, limit=60):
    """Failure-explaining lines from a CI log, chosen by content not position.

    The first draft took the last 80 lines. That is wrong, and it was wrong on
    real data: GitHub appends checkout teardown after the failure, so on #288
    the tail was `git config --unset` chatter and the size-guard line that
    actually broke the build -- `src-tauri/src/lib.rs: 1000 -> 1001 (+1) lines
    (allowed 1000)` -- had already scrolled past. The classifier answered
    UNKNOWN for a failure it should have called REAL.

    Position in a log is not evidence. Content is.
    """
    kept = []
    for line in (log_text or "").splitlines():
        if _LOG_NOISE.search(line):
            continue
        if _LOG_SIGNAL.search(line):
            kept.append(line.strip())
    return "\n".join(kept[-limit:])


def classify_failure(check_name, failed_step, log_tail, diff_paths, failing_paths):
    """Classify one failing check as REAL, FLAKE, PRE_EXISTING or UNKNOWN.

    REAL outranks PRE_EXISTING because a log can carry both, and #288's did:
    inherited warnings printed above the size-guard failure that actually broke
    the build. Anything that stopped at the first recognised line would have
    reported that PR clean.
    """
    haystack = f"{failed_step or ''}\n{log_tail or ''}".lower()

    if any(step in (failed_step or "").lower() for step in _TOOLCHAIN_STEPS):
        return Verdict("FLAKE", f"failed inside a toolchain step: {failed_step}")
    if any(sig in haystack for sig in _FLAKE_SIGNATURES):
        return Verdict("FLAKE", "log carries an infrastructure-failure signature")

    if failing_paths:
        owned = {p for p in failing_paths if p in diff_paths}
        if owned:
            return Verdict("REAL", f"failing path(s) in this diff: {sorted(owned)[:3]}")
        return Verdict(
            "PRE_EXISTING",
            f"failing path(s) absent from this diff: {sorted(failing_paths)[:3]}",
        )

    return Verdict("UNKNOWN", f"no attributable path in {check_name}'s output")


def classify_independence(commits, self_login, session_since):
    """CONFLICT when the reviewing identity authored a commit in this window.

    The window matters. In this repo every commit carries the operator's git
    identity, including ones written weeks ago by other sessions, so an
    unwindowed check flags every PR and the signal becomes noise. Only commits
    inside the current session count as "mine to disclose".
    """
    since = parse_time(session_since)
    if since is None:
        return Verdict("UNKNOWN", "no session window given; independence unassessed")

    mine = [
        c for c in commits
        if c.get("author_login") == self_login
        and (parse_time(c.get("committed_at")) or since) >= since
    ]
    if mine:
        oids = ", ".join(c["oid"][:8] for c in mine[:3])
        return Verdict("CONFLICT", f"reviewing identity authored {oids} in this session")
    return Verdict("INDEPENDENT", "no commit by the reviewing identity in this window")


@dataclass
class Attributed:
    """A verdict plus what it is about -- a check name, or a reviewer's login.

    A named type rather than a bare tuple because the first draft stored bare
    ``Verdict`` objects in one place and ``(name, Verdict)`` pairs in another.
    ``blocks_review()`` accepted both, since it only reads ``.state``, while
    ``render()`` crashed on the first shape. One of the two callers was always
    going to be wrong and nothing would have said which.
    """

    subject: str
    verdict: Verdict

    @property
    def state(self):
        return self.verdict.state

    def as_dict(self):
        return {"subject": self.subject, **self.verdict.as_dict()}


@dataclass
class LeakHit:
    pattern: str
    line: str


def scan_leaks(diff_text, patterns):
    """Private-tooling references in ADDED lines only.

    Removed lines are skipped: a deleted reference is the fix, and flagging it
    would punish the commit that cleaned it up. Diff headers are skipped too,
    since `+++ b/path/verify-gate.sh` is a filename, not content.
    """
    hits = []
    for line in (diff_text or "").splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue
        low = line.lower()
        for pattern in patterns:
            if pattern in low:
                hits.append(LeakHit(pattern, line.strip()[:160]))
    return hits


def check_placement(paths):
    """Added paths that break `launchpad/AGENTS.md` section 3."""
    bad = []
    for path in sorted(paths):
        if path.startswith(_UPSTREAM_ONLY_PREFIXES):
            bad.append(path)
            continue
        # A bare .md directly in launchpad/agents/ is scanned as a subagent
        # roster and blocks the commit. Pack docs go in a pack subdirectory.
        if path.startswith("launchpad/agents/") and path.endswith(".md"):
            if path.count("/") == 2:
                bad.append(path)
    return bad


@dataclass
class Briefing:
    number: int
    author: str
    title: str
    head_sha: str
    reviews: list = field(default_factory=list)
    ci: list = field(default_factory=list)
    independence: Verdict | None = None
    leaks: list = field(default_factory=list)
    placement: list = field(default_factory=list)
    calibration: dict | None = None

    def blocks_review(self):
        """True when a reviewer should not be dispatched yet.

        Only two things stop a review outright: a real CI failure the author
        must fix first, and an independence conflict that disqualifies the
        reviewer. Flakes and inherited failures are noted, not blocking.
        """
        if self.independence and self.independence.state == "CONFLICT":
            return True
        return any(v.state == "REAL" for v in self.ci)

    def as_dict(self):
        return {
            "number": self.number,
            "author": self.author,
            "title": self.title,
            "head_sha": self.head_sha,
            "blocks_review": self.blocks_review(),
            "reviews": [a.as_dict() for a in self.reviews],
            "ci": [a.as_dict() for a in self.ci],
            "independence": self.independence.as_dict() if self.independence else None,
            "leaks": [{"pattern": h.pattern, "line": h.line} for h in self.leaks],
            "placement": self.placement,
            "calibration": self.calibration,
        }

    def render(self):
        out = [f"PR #{self.number}  {self.author}  {self.head_sha[:9]}", f"  {self.title}"]
        if self.blocks_review():
            out.append("  DO NOT DISPATCH A REVIEWER YET")
        for item in self.reviews:
            out.append(f"  review by {item.subject}: {item.state} -- {item.verdict.reason}")
        for item in self.ci:
            out.append(f"  check {item.subject}: {item.state} -- {item.verdict.reason}")
        if self.independence:
            out.append(f"  independence: {self.independence.state} -- {self.independence.reason}")
        for hit in self.leaks:
            out.append(f"  LEAK ({hit.pattern}): {hit.line}")
        for path in self.placement:
            out.append(f"  PLACEMENT: {path} is outside the cohort trees")
        if self.calibration:
            c = self.calibration
            out.append(
                f"  calibration: at {c['commits']} commits from {c['merge_base'][:9]} "
                f"the tip is {c['tip'][:9]} and the diff is {c['files']} files"
            )
        return "\n".join(out)


# ---------------------------------------------------------------------------
# gh / git plumbing. Everything below shells out; everything above is pure.
# ---------------------------------------------------------------------------


def _run(args):
    proc = subprocess.run(args, capture_output=True, text=True, check=False)
    return proc.returncode, proc.stdout, proc.stderr


def _gh_json(args):
    code, out, err = _run(["gh"] + args)
    if code != 0:
        print(f"pr_review_batch: gh failed: {' '.join(args)}: {err.strip()}",
              file=sys.stderr)
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


def calibrate(merge_base, commits, upstream_ref="upstream/main"):
    """The pinned tip and file count N commits from a merge base.

    This is the anti-drift step. Reviewers get the SHA the document measured
    against, so a count that fails to reproduce at the live tip is recognised
    as drift rather than reported as an error. See #374 and issue #384.
    """
    code, out, _ = _run(
        ["git", "rev-list", f"{merge_base}..{upstream_ref}"]
    )
    if code != 0:
        return None
    revs = out.split()
    if len(revs) < commits:
        return None
    tip = revs[-commits]
    code, out, _ = _run(["git", "diff", "--name-only", merge_base, tip])
    if code != 0:
        return None
    return {
        "merge_base": merge_base,
        "commits": commits,
        "tip": tip,
        "files": len([line for line in out.splitlines() if line.strip()]),
    }


def brief(number, repo, self_login, session_since, calibration=None):
    meta = _gh_json([
        "pr", "view", str(number), "--repo", repo,
        "--json", "number,title,author,headRefOid,reviews,commits,files",
    ])
    if meta is None:
        return None

    diff_paths = {f["path"] for f in meta.get("files") or []}
    commits = [
        {
            "oid": c.get("oid", ""),
            "author_login": (c.get("authors") or [{}])[0].get("login")
                            or (c.get("authors") or [{}])[0].get("name"),
            "committed_at": c.get("committedDate"),
        }
        for c in meta.get("commits") or []
    ]
    head_at = commits[-1]["committed_at"] if commits else None

    b = Briefing(
        number=meta["number"],
        author=(meta.get("author") or {}).get("login", "?"),
        title=meta.get("title", ""),
        head_sha=meta.get("headRefOid", ""),
    )

    for review in meta.get("reviews") or []:
        verdict = classify_review(review, head_at, diff_paths)
        if verdict:
            b.reviews.append(
                Attributed((review.get("author") or {}).get("login", "?"), verdict)
            )

    checks = _gh_json(["pr", "checks", str(number), "--repo", repo,
                       "--json", "name,state,link"]) or []
    for check in checks:
        if check.get("state") != "FAILURE":
            continue
        # Attributing a failure needs the log. Kept to the tail: a full CI log
        # is megabytes and the failure is always at the end.
        job_id = (check.get("link") or "").rstrip("/").split("/")[-1]
        failed_step, log_tail, failing = "", "", set()
        if job_id.isdigit():
            job = _gh_json(["api", f"repos/{repo}/actions/jobs/{job_id}"]) or {}
            for step in job.get("steps") or []:
                if step.get("conclusion") == "failure":
                    failed_step = step.get("name", "")
                    break
            code, out, _ = _run(["gh", "run", "view", "--job", job_id,
                                 "--repo", repo, "--log-failed"])
            log_tail = relevant_log_lines(out) if code == 0 else ""
            failing = {m.group(1) for m in _PATH_TOKEN.finditer(log_tail)}
            # Log paths are workspace-relative; diff paths are repo-relative.
            failing = {p for p in failing} | {
                d for d in diff_paths if any(d.endswith(p) for p in failing)
            }
        b.ci.append(Attributed(
            check.get("name", "?"),
            classify_failure(check.get("name", ""), failed_step,
                             log_tail, diff_paths, failing),
        ))

    b.independence = classify_independence(commits, self_login, session_since)

    code, diff_text, _ = _run(["gh", "pr", "diff", str(number), "--repo", repo])
    if code == 0:
        b.leaks = scan_leaks(diff_text, DEFAULT_LEAK_PATTERNS)
    b.placement = check_placement(diff_paths)
    b.calibration = calibration
    return b


def _select(args):
    if args.pr:
        return args.pr
    query = ["pr", "list", "--repo", args.repo, "--state", "open",
             "--limit", str(args.limit), "--json", "number,author,reviewDecision"]
    rows = _gh_json(query) or []
    picked = []
    for row in rows:
        if args.author and (row.get("author") or {}).get("login") not in args.author:
            continue
        if args.review_required and row.get("reviewDecision") not in (None, "REVIEW_REQUIRED"):
            continue
        picked.append(row["number"])
    return picked


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--pr", type=int, action="append", default=[])
    parser.add_argument("--author", action="append", default=[])
    parser.add_argument("--review-required", action="store_true")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--self", dest="self_login", default=None,
                        help="identity to check independence against; "
                             "defaults to the authenticated gh user")
    parser.add_argument("--session-since", default=None,
                        help="ISO timestamp; commits by --self at or after this "
                             "count as the reviewer's own work")
    parser.add_argument("--calibrate", default=None, metavar="MERGE_BASE")
    parser.add_argument("--commits", type=int, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    self_login = args.self_login
    if self_login is None:
        who = _gh_json(["api", "user", "--jq", "{login: .login}"]) or {}
        self_login = who.get("login")

    calibration = None
    if args.calibrate and args.commits:
        calibration = calibrate(args.calibrate, args.commits)
        if calibration is None:
            print("pr_review_batch: calibration failed; is the upstream remote fetched?",
                  file=sys.stderr)

    numbers = _select(args)
    if not numbers:
        print("pr_review_batch: no pull requests matched", file=sys.stderr)
        return 1

    briefings = [b for b in (brief(n, args.repo, self_login, args.session_since,
                                   calibration) for n in numbers) if b]
    if args.json:
        print(json.dumps([b.as_dict() for b in briefings], indent=2))
    else:
        for b in briefings:
            print(b.render())
            print()
        held = [b.number for b in briefings if b.blocks_review()]
        if held:
            print(f"Hold: {held} -- real CI failure or independence conflict.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
