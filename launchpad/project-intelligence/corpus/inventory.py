"""Deterministic Buzz source inventory -- issue #624.

Discovers Rust workspace members, relay HTTP route registrations,
desktop/mobile/web features, event kinds, migrations, `.env.example`
configuration keys, buzz-test-client integration test suites, formal models
and existing documentation, and reports each as one `InventoryItem` carrying
a stable source key and a concrete path (plus a symbol, where one exists).

Every discoverer reads real files under `--root` and nothing else; there is
no network access and no dependency on GitHub. Output is sorted before
serialization, so re-running against an unchanged tree produces
byte-identical JSON (issue #624's determinism requirement) -- the ordering
`Path.iterdir()`/`glob()` return is filesystem-dependent and is never trusted
on its own.

Any top-level directory this inventory does not recognise is reported in
`unrecognized_areas` rather than silently skipped -- see `_KNOWN_TOP_LEVEL`
and `_IGNORED_TOP_LEVEL` for the two ways a directory can be excluded
deliberately, and the distinction between them.

Run:  python3 launchpad/project-intelligence/corpus/inventory.py [--root PATH] [--out PATH]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class InventoryItem:
    category: str
    source_key: str
    path: str
    symbol: str | None = None


@dataclass
class InventoryReport:
    items: list[InventoryItem] = field(default_factory=list)
    unrecognized_areas: list[str] = field(default_factory=list)

    def to_json(self) -> str:
        payload = {
            "items": [
                {
                    "category": item.category,
                    "source_key": item.source_key,
                    "path": item.path,
                    "symbol": item.symbol,
                }
                for item in sorted(self.items, key=lambda i: (i.category, i.source_key))
            ],
            "unrecognized_areas": sorted(self.unrecognized_areas),
        }
        return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def repo_root() -> Path:
    """Resolve the repository root via git, never via cwd or a hard-coded parent count."""
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=Path(__file__).resolve().parent,
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(out.stdout.strip())


# Directories at the repo root this inventory deliberately does not walk,
# because they hold no Buzz source surface: VCS/tool internals, build
# artifacts, and -- per launchpad/CLAUDE.md's fork note -- the cohort's own
# operating tree, which catalogues our process, not the Buzz product this
# inventory is about. Excluded by name, not by pattern, so a new top-level
# directory is never silently swallowed by a broad rule.
_IGNORED_TOP_LEVEL = {
    ".git",
    ".github",
    ".claude",
    "target",
    "node_modules",
    "__worktrees",
    "scratchpad",
    "launchpad",
}

# Directories at the repo root this inventory actively discovers from.
# Anything present that is in neither this set nor `_IGNORED_TOP_LEVEL` is a
# source area this inventory does not yet recognise, and is reported rather
# than dropped -- see `discover_unrecognized_areas`.
_KNOWN_TOP_LEVEL = {"crates", "examples", "desktop", "mobile", "web", "migrations", "docs"}

_WORKSPACE_MEMBERS_RE = re.compile(r"members\s*=\s*\[(.*?)\]", re.S)
_QUOTED_RE = re.compile(r'"([^"]+)"')
_CRATE_NAME_RE = re.compile(r'^\s*name\s*=\s*"([^"]+)"', re.M)
_EVENT_KIND_RE = re.compile(r"\s*pub const (KIND_[A-Z0-9_]+)\s*:\s*u32\s*=\s*(\d+)\s*;")
_ROUTE_RE = re.compile(r'\s*\.route\(\s*"([^"]+)"')
_ENV_KEY_RE = re.compile(r"\s*([A-Z][A-Z0-9_]*)\s*=")


def discover_rust_crates(root: Path) -> list[InventoryItem]:
    """Every `[workspace] members` entry in the root Cargo.toml, one item each."""
    cargo_toml = root / "Cargo.toml"
    if not cargo_toml.exists():
        return []
    match = _WORKSPACE_MEMBERS_RE.search(cargo_toml.read_text())
    if not match:
        return []
    items: list[InventoryItem] = []
    for entry in _QUOTED_RE.findall(match.group(1)):
        member_toml = root / entry / "Cargo.toml"
        name = entry
        if member_toml.exists():
            name_match = _CRATE_NAME_RE.search(member_toml.read_text())
            if name_match:
                name = name_match.group(1)
        items.append(InventoryItem(category="rust_crate", source_key=f"rust_crate:{name}", path=entry))
    return items


def discover_event_kinds(root: Path) -> list[InventoryItem]:
    """Every `pub const KIND_*: u32 = N;` in buzz-core's kind registry."""
    kind_rs = root / "crates" / "buzz-core" / "src" / "kind.rs"
    if not kind_rs.exists():
        return []
    rel = kind_rs.relative_to(root)
    items: list[InventoryItem] = []
    for lineno, line in enumerate(kind_rs.read_text().splitlines(), start=1):
        m = _EVENT_KIND_RE.match(line)
        if m:
            name = m.group(1)
            items.append(
                InventoryItem(
                    category="event_kind",
                    source_key=f"event_kind:{name}",
                    path=f"{rel}:{lineno}",
                    symbol=name,
                )
            )
    return items


def discover_relay_routes(root: Path) -> list[InventoryItem]:
    """Every `.route("path", ...)` registration anywhere under buzz-relay's src/.

    This is the declared route string as it appears in whichever file
    registers it -- `router.rs` for the top-level surface, plus the sub-router
    files (media, git transport, push delivery) CONTRIBUTING.md's HTTP-surface
    list also covers. It is not the fully-mounted path: a route registered on
    a sub-router that is later `.nest()`-ed under a prefix elsewhere is
    reported at its own declared string, not the concatenated one, because
    resolving `.nest()` mount points is out of scope for this first pass and
    fabricating a mounted path this inventory did not verify would be worse
    than reporting the literal, checkable one.
    """
    relay_src = root / "crates" / "buzz-relay" / "src"
    if not relay_src.is_dir():
        return []
    items: list[InventoryItem] = []
    for rs_file in sorted(relay_src.rglob("*.rs")):
        rel = rs_file.relative_to(root)
        for lineno, line in enumerate(rs_file.read_text().splitlines(), start=1):
            m = _ROUTE_RE.match(line)
            if m:
                route = m.group(1)
                items.append(
                    InventoryItem(
                        category="relay_route",
                        source_key=f"relay_route:{route}:{rel}:{lineno}",
                        path=f"{rel}:{lineno}",
                        symbol=route,
                    )
                )
    return items


def discover_migrations(root: Path) -> list[InventoryItem]:
    """Every `migrations/*.sql` file, one item per file."""
    migrations_dir = root / "migrations"
    if not migrations_dir.is_dir():
        return []
    items = []
    for sql_file in sorted(migrations_dir.glob("*.sql")):
        items.append(
            InventoryItem(
                category="migration",
                source_key=f"migration:{sql_file.stem}",
                path=str(sql_file.relative_to(root)),
            )
        )
    return items


def _discover_client_features(root: Path, client: str, features_dir: Path) -> list[InventoryItem]:
    if not features_dir.is_dir():
        return []
    items = []
    for entry in sorted(features_dir.iterdir()):
        if entry.is_dir():
            items.append(
                InventoryItem(
                    category=f"{client}_feature",
                    source_key=f"{client}_feature:{entry.name}",
                    path=str(entry.relative_to(root)),
                )
            )
    return items


def discover_desktop_features(root: Path) -> list[InventoryItem]:
    return _discover_client_features(root, "desktop", root / "desktop" / "src" / "features")


def discover_mobile_features(root: Path) -> list[InventoryItem]:
    return _discover_client_features(root, "mobile", root / "mobile" / "lib" / "features")


def discover_web_features(root: Path) -> list[InventoryItem]:
    return _discover_client_features(root, "web", root / "web" / "src" / "features")


def discover_test_suites(root: Path) -> list[InventoryItem]:
    """Every integration test file under buzz-test-client/tests/."""
    tests_dir = root / "crates" / "buzz-test-client" / "tests"
    if not tests_dir.is_dir():
        return []
    items = []
    for rs_file in sorted(tests_dir.glob("*.rs")):
        items.append(
            InventoryItem(
                category="test_suite",
                source_key=f"test_suite:{rs_file.stem}",
                path=str(rs_file.relative_to(root)),
            )
        )
    return items


def discover_formal_models(root: Path) -> list[InventoryItem]:
    """Every Python formal model under docs/formal/."""
    formal_dir = root / "docs" / "formal"
    if not formal_dir.is_dir():
        return []
    items = []
    for py_file in sorted(formal_dir.rglob("*.py")):
        key = str(py_file.relative_to(formal_dir).with_suffix(""))
        items.append(
            InventoryItem(
                category="formal_model",
                source_key=f"formal_model:{key}",
                path=str(py_file.relative_to(root)),
            )
        )
    return items


def discover_existing_docs(root: Path) -> list[InventoryItem]:
    """Root-level Markdown files plus everything under docs/, recursively."""
    items = []
    for md_file in sorted(root.glob("*.md")):
        items.append(
            InventoryItem(
                category="existing_doc",
                source_key=f"existing_doc:{md_file.name}",
                path=str(md_file.relative_to(root)),
            )
        )
    docs_dir = root / "docs"
    if docs_dir.is_dir():
        for md_file in sorted(docs_dir.rglob("*.md")):
            key = str(md_file.relative_to(root))
            items.append(InventoryItem(category="existing_doc", source_key=f"existing_doc:{key}", path=key))
    return items


def discover_configuration(root: Path) -> list[InventoryItem]:
    """Every key `.env.example` declares, one item per key."""
    env_example = root / ".env.example"
    if not env_example.exists():
        return []
    rel = env_example.relative_to(root)
    items = []
    for lineno, line in enumerate(env_example.read_text().splitlines(), start=1):
        m = _ENV_KEY_RE.match(line)
        if m:
            key = m.group(1)
            items.append(
                InventoryItem(
                    category="config",
                    source_key=f"config:{key}",
                    path=f"{rel}:{lineno}",
                    symbol=key,
                )
            )
    return items


def discover_unrecognized_areas(root: Path) -> list[str]:
    """Top-level directories that are neither actively discovered nor deliberately ignored."""
    unrecognized = []
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name in _IGNORED_TOP_LEVEL or entry.name in _KNOWN_TOP_LEVEL:
            continue
        unrecognized.append(entry.name)
    return unrecognized


_DISCOVERERS = (
    discover_rust_crates,
    discover_event_kinds,
    discover_relay_routes,
    discover_migrations,
    discover_desktop_features,
    discover_mobile_features,
    discover_web_features,
    discover_test_suites,
    discover_formal_models,
    discover_existing_docs,
    discover_configuration,
)


def run_inventory(root: Path) -> InventoryReport:
    report = InventoryReport()
    for discoverer in _DISCOVERERS:
        report.items.extend(discoverer(root))
    report.unrecognized_areas.extend(discover_unrecognized_areas(root))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=None, help="Repository root (default: resolved via git)")
    parser.add_argument("--out", type=Path, default=None, help="Write JSON here instead of stdout")
    args = parser.parse_args(argv)

    root = args.root or repo_root()
    output = run_inventory(root).to_json()

    if args.out:
        args.out.write_text(output)
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
