#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""The Professor's tool layer — a plain script, no MCP dependency.

Replaces `tools/server.py` per `launchpad/Research/the-professor-skill-suite-redesign.md`
§4: no MCP, no registration, no dual mode — one small script-based toolkit, callable
identically from any harness via Bash, with a hard split between what needs the network
and what doesn't.

Four subcommands (§4's diagram):

  - resolve-pin       netcmd  — resolve a repo ref to its full 40-char commit SHA
  - path-exists-at    netcmd  — does a path exist in a repo at a pinned commit?
  - check-page        localcmd — run `tools/contract/page-contract.md`'s mechanical
                                 checks against a draft page, entirely offline for a
                                 citation to `--target`'s own repo
  - screen-content    localcmd — run `tools/contract/sensitive-patterns.md`'s
                                 `[pattern]` categories against a draft's content

`$PROFESSOR_PACK_ROOT` resolution (Open Questions item 6, decided): every subcommand
reads this env var before doing anything else, and fails loud with a specific,
actionable message — never a generic crash three steps later — if it's unset. This is
checked ahead of argparse's own subcommand dispatch so it applies uniformly to all four,
not re-implemented per subcommand.
"""

import argparse
import os
import sys
from pathlib import Path

# So `professor_lib` (this file's sibling package) is importable regardless of the
# caller's own working directory -- professor.py is meant to be invoked by an
# absolute path from any cwd (see step 2/7's "from a working directory outside this
# checkout" requirement).
sys.path.insert(0, str(Path(__file__).resolve().parent))

PROFESSOR_PACK_ROOT_ENV = "PROFESSOR_PACK_ROOT"


def _require_pack_root() -> str:
    """Read `$PROFESSOR_PACK_ROOT`, failing loud with a specific, actionable message
    if it is unset or empty -- never a generic crash three steps later.

    Phase 1's own review gate (redesign doc §9) requires this exact behaviour: "fails
    loud with a specific, actionable message if it's unset... This isn't optional
    polish; it's the decision's own stated requirement."
    """
    pack_root = os.environ.get(PROFESSOR_PACK_ROOT_ENV, "")
    if not pack_root:
        print(
            f"professor.py: ${PROFESSOR_PACK_ROOT_ENV} is not set. This tool needs "
            f"it to resolve where this pack's own files (contract specs, etc.) live "
            f"-- set ${PROFESSOR_PACK_ROOT_ENV} to this pack's root directory "
            f"(the directory containing this `tools/` folder) before calling "
            f"professor.py.",
            file=sys.stderr,
        )
        sys.exit(1)
    return pack_root


def _cmd_resolve_pin(args: argparse.Namespace, pack_root: str) -> int:
    from professor_lib.netcmd import resolve_pin

    return resolve_pin(repo=args.repo, ref=args.ref)


def _cmd_path_exists_at(args: argparse.Namespace, pack_root: str) -> int:
    from professor_lib.netcmd import path_exists_at

    return path_exists_at(repo=args.repo, commit=args.commit, path=args.path)


def _cmd_check_page(args: argparse.Namespace, pack_root: str) -> int:
    from professor_lib.localcmd import check_page

    return check_page(file_path=args.file, target=args.target, pack_root=pack_root)


def _cmd_screen_content(args: argparse.Namespace, pack_root: str) -> int:
    from professor_lib.localcmd import screen_content

    return screen_content(file_path=args.file, pack_root=pack_root, target=args.target)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="professor.py",
        description="The Professor's tool layer (four subcommands, no MCP).",
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    resolve_pin_parser = subparsers.add_parser(
        "resolve-pin",
        help="Resolve a repo ref (branch/tag/SHA) to its full 40-char commit SHA.",
    )
    resolve_pin_parser.add_argument("repo", help="owner/repo")
    resolve_pin_parser.add_argument("ref", help="branch, tag, or SHA")
    resolve_pin_parser.set_defaults(func=_cmd_resolve_pin)

    path_exists_parser = subparsers.add_parser(
        "path-exists-at",
        help="Check whether a path exists in a repo at a pinned commit.",
    )
    path_exists_parser.add_argument("repo", help="owner/repo")
    path_exists_parser.add_argument("commit", help="full 40-char hex commit SHA")
    path_exists_parser.add_argument("path", help="repo-relative path")
    path_exists_parser.set_defaults(func=_cmd_path_exists_at)

    check_page_parser = subparsers.add_parser(
        "check-page",
        help="Run page-contract.md's mechanical checks against a draft page.",
    )
    check_page_parser.add_argument("file", help="path to the draft page's Markdown file")
    check_page_parser.add_argument(
        "--target",
        required=True,
        help="root of the target repo the draft's citations are checked against",
    )
    check_page_parser.set_defaults(func=_cmd_check_page)

    screen_content_parser = subparsers.add_parser(
        "screen-content",
        help="Run sensitive-patterns.md's [pattern] categories against a draft's content.",
    )
    screen_content_parser.add_argument("file", help="path to the file to screen")
    screen_content_parser.add_argument(
        "--target",
        required=False,
        default=None,
        help=(
            "root of the target repo. If <target>/.professor/sensitive-"
            "patterns.md exists, this tool reports an explicit "
            "target-ruleset-override (not_evaluated) result instead of "
            "silently screening against the bundled default -- its "
            "pattern-matching categories are hardcoded Python, not parsed "
            "from a markdown ruleset file at runtime, so it cannot honour "
            "a target-specific override's content."
        ),
    )
    screen_content_parser.set_defaults(func=_cmd_screen_content)

    return parser


def main(argv: list[str] | None = None) -> int:
    pack_root = _require_pack_root()
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args, pack_root)


if __name__ == "__main__":
    sys.exit(main())
