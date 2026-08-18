"""The Symbol record -- issue #206, STEP 1.

Schema fixed by launchpad/Research/project-intelligence-layer-design.md (Data Model,
item 1). This module holds the type only -- no extraction, no data source. Populating
a real Symbol from this repo is #206's later steps.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DefinedAt:
    file: str
    start_line: int
    end_line: int
    temporal_state: str  # "BASE" | "WORKING"


@dataclass(frozen=True)
class GitOwnership:
    primary_authors: tuple[str, ...] = ()
    history: tuple[str, ...] = ()  # one summary line per commit touching this symbol


@dataclass(frozen=True)
class Symbol:
    symbol_id: str
    kind: str  # "function" | "method" | "class" | "module" | "service" | "route"
    qualified_name: str
    defined_at: DefinedAt
    signature: str
    calls: tuple[str, ...] = ()
    called_by: tuple[str, ...] = ()
    tests: tuple[str, ...] = ()
    config_dependencies: tuple[str, ...] = ()
    documentation_links: tuple[str, ...] = ()
    git_ownership: GitOwnership = field(default_factory=GitOwnership)
