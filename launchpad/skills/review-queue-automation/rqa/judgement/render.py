"""Pure GitHub review/comment body renderer — `code/P-07-judgement.md` §3's
second entry point.

`render(judgement)` is positional, not keyword-only — the contract's own
stated exception (alongside `rqa.protocol.paths.matches`) to the
"every function keyword-only" convention.
"""

from __future__ import annotations

from rqa.contracts import Judgement
from rqa.judgement import findings as findings_mod

__all__ = ["render"]


def _escape(value: object) -> str:
    """Render any value as inert Markdown prose (not inside a code span):
    backslashes and newlines are neutralised so no judged field can break a
    line or inject a heading/fence."""
    text = str(value)
    return text.replace("\\", "\\\\").replace("\n", "\\n")


def _code_span(value: object) -> str:
    """Render `value` as a CommonMark inline code span that cannot be broken
    open by backticks the value itself contains.

    A backslash before a backtick is inert inside a CommonMark code span —
    escaping `` ` `` with `\\` does not stop it from closing the span early.
    The only reliable defence is a delimiter run strictly longer than the
    longest run of consecutive backticks the (already backslash/newline
    escaped) content contains; that delimiter can never be matched by
    anything shorter inside the content, so the span cannot close early. A
    leading/trailing space is added whenever the content starts or ends with
    a backtick (or is empty/all-space), per CommonMark's own code-span rule,
    so the delimiter is never rendered flush against a backtick it did not
    intend to pair with.
    """
    text = str(value).replace("\\", "\\\\").replace("\n", "\\n")
    longest_run = 0
    current_run = 0
    for character in text:
        if character == "`":
            current_run += 1
            longest_run = max(longest_run, current_run)
        else:
            current_run = 0
    delimiter = "`" * (longest_run + 1)
    if text == "" or text.strip() == "" or text.startswith("`") or text.endswith("`"):
        return f"{delimiter} {text} {delimiter}"
    return f"{delimiter}{text}{delimiter}"


def render(judgement: Judgement) -> str:
    """Byte-identical for the same judgement (§3).

    Lists corroborated findings in retained order — each with its category
    set, blocking marker and provenance (the attempt that produced it, and
    the PR-attributed failing check it cites when it is check-backed) —
    every judged obligation and its state, inherited check attribution,
    assurance, and `reused_from`. Every value is escaped as data.
    """
    lines: list[str] = ["# Judgement", ""]

    lines.append("## Obligations")
    if judgement.obligations:
        for obligation_id, state in judgement.obligations.items():
            lines.append(f"- {_code_span(obligation_id)}: {_escape(state.value)}")
    else:
        lines.append("- (none)")
    lines.append("")

    lines.append("## Findings")
    corroborated_findings = [
        finding for finding in judgement.findings if finding.id in judgement.corroborated
    ]
    pr_failing_checks = [name for name, kind in judgement.attribution.items() if kind == "pr"]
    if corroborated_findings:
        for finding in corroborated_findings:
            categories = ", ".join(sorted(category.value for category in finding.categories))
            blocking_marker = "blocking" if finding.id in judgement.blocking else "non-blocking"
            cited_check = findings_mod.cited_pr_failing_check(
                finding.evidence, pr_failing_checks=pr_failing_checks
            )
            provenance = f"attempt={finding.source_attempt or '-'}"
            if cited_check is not None:
                provenance = f"{provenance} check={cited_check}"
            lines.append(
                f"- {_code_span(finding.id)} [{blocking_marker}] "
                f"categories={_escape(categories)} provenance={_code_span(provenance)} "
                f"evidence={_code_span(finding.evidence)}"
            )
    else:
        lines.append("- (none)")
    lines.append("")

    lines.append("## Inherited check attribution")
    inherited = sorted(
        name for name, kind in judgement.attribution.items() if kind == "inherited"
    )
    if inherited:
        for name in inherited:
            lines.append(f"- {_code_span(name)}")
    else:
        lines.append("- (none)")
    lines.append("")

    lines.append("## Assurance")
    lines.append(f"- required={judgement.assurance.required} achieved={judgement.assurance.achieved}")
    lines.append("")

    lines.append("## Reused from")
    reused_from = "(none)" if judgement.reused_from is None else _code_span(judgement.reused_from)
    lines.append(f"- {reused_from}")

    return "\n".join(lines)
