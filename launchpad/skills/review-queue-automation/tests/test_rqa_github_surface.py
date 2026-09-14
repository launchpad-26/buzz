#!/usr/bin/env python3
"""`rqa.github`'s public surface and its exclusions — `code/P-09-github-adapter.md`
§1, §2, §5, §7.

Wave-invariant by construction: `rqa/github` is one lane's finished state, so
its module set and `__all__` are pinned to §1's exact lists. Tree-wide scans
assert only properties the part contract states forever — the single HTTP
client import, the single writer of the three §5 tables — never the absence
of a sibling package.
"""

from __future__ import annotations

import ast
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.contracts as contracts  # noqa: E402
import rqa.github as github  # noqa: E402
from rqa.github.types import MutationKind  # noqa: E402

RQA = pathlib.Path(__file__).resolve().parent.parent / "rqa"
GITHUB = RQA / "github"

#: §1's module list — this lane's finished state; the sibling adds nothing here.
MODULES = frozenset(
    {"__init__", "types", "conclusions", "transport", "reads", "writes",
     "capability", "store", "testing"}
)

#: §1's re-export list: the §4 shared imports plus the eleven named names.
SHARED_EXPORTS = frozenset({"Activity", "Grant", "Job", "RecordWriter", "Entry"})
NAMED_EXPORTS = frozenset(
    {"GithubAdapter", "CheckConclusion", "FAILING", "UNSETTLED", "PASSING",
     "MutationKind", "Stale", "LeaseTaken", "GithubUnavailable",
     "CapabilityReading", "AdapterError"}
)
ALL_EXPORTS = SHARED_EXPORTS | NAMED_EXPORTS

#: An HTTP client import anywhere outside transport.py breaks §1's boundary.
HTTP_CLIENT_MODULES = frozenset(
    {"urllib.request", "http.client", "requests", "httpx", "aiohttp", "urllib3"}
)


def _sources() -> dict[str, str]:
    return {
        str(path.relative_to(RQA.parent)): path.read_text(encoding="utf-8")
        for path in sorted(RQA.rglob("*.py"))
    }


def _imported_modules(source: str) -> set[str]:
    imported: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    return imported


# -- §1: the module set and the re-export list -----------------------------------


def test_the_module_set_is_exactly_section_ones_list() -> None:
    found = frozenset(path.stem for path in GITHUB.glob("*.py"))
    assert found == MODULES, f"module set diverges from §1: {sorted(found ^ MODULES)}"


def test_all_is_exactly_section_ones_re_export_list() -> None:
    assert frozenset(github.__all__) == ALL_EXPORTS, (
        f"__all__ diverges from §1: {sorted(frozenset(github.__all__) ^ ALL_EXPORTS)}"
    )
    assert len(github.__all__) == len(set(github.__all__))


def test_every_re_exported_name_resolves() -> None:
    missing = [name for name in github.__all__ if not hasattr(github, name)]
    assert missing == []


def test_the_shared_seam_types_are_the_contracts_declarations() -> None:
    for name in sorted(ALL_EXPORTS - {"GithubAdapter", "MutationKind", "AdapterError"}):
        assert getattr(github, name) is getattr(contracts, name), name


def test_the_store_protocols_stay_module_names_not_package_surface() -> None:
    for name in ("EtagStore", "ApiCallStore", "MutationStore", "MutationRow"):
        assert name not in github.__all__, name


# -- §2/§7: MutationKind has exactly five members; no estate kinds ---------------


def test_mutation_kind_has_exactly_the_five_fixed_members() -> None:
    assert {kind.value for kind in MutationKind} == {
        "assignee_add", "assignee_remove", "comment", "review_submit", "merge"
    }
    assert len(MutationKind) == 5


def test_the_estate_mutation_kinds_are_not_carried() -> None:
    """§7: no `create_issue`, `add_labels`, `request_review` or `thread_reply`
    — neither as a kind nor as a GraphQL document."""
    estate_documents = ("createIssue", "addLabelsToLabelable", "requestReviews",
                        "addPullRequestReviewThreadReply")
    for name, source in _sources().items():
        if not name.startswith("rqa/github/"):
            continue
        for needle in estate_documents:
            assert needle not in source, f"{name} carries the estate mutation {needle}"


# -- §1/§4: one HTTP client, one boundary ----------------------------------------


def test_transport_is_the_only_http_client_import_in_rqa() -> None:
    """§1: `transport.py` is the ONLY module anywhere in RQA that imports an
    HTTP client — a forever property of the whole tree, safe against every
    sibling lane because their contracts forbid HTTP clients too."""
    offenders = []
    for name, source in _sources().items():
        clients = _imported_modules(source) & HTTP_CLIENT_MODULES
        if clients and name != "rqa/github/transport.py":
            offenders.append((name, sorted(clients)))
    assert offenders == [], offenders


def test_no_module_here_imports_a_part_section_one_forbids() -> None:
    """§1: `rqa.github` imports only `rqa.record` (to append) among parts —
    never `rqa.policy`, `rqa.lifecycle`, `rqa.judgement`, `rqa.authority` or
    any other. The one blessed exception is the call-time resolution of
    P-01's `stable_hash` in `writes.py` (§3 preamble; `rqa.intake.identity`)."""
    allowed_intake = {("rqa/github/writes.py", "rqa.intake.identity")}
    offenders = []
    for name, source in _sources().items():
        if not name.startswith("rqa/github/"):
            continue
        for module in _imported_modules(source):
            if module in ("rqa.contracts", "rqa.record") or module.startswith("rqa.github"):
                continue
            if module.startswith("rqa"):
                if (name, module) in allowed_intake:
                    continue
                offenders.append((name, module))
    assert offenders == [], offenders


def test_the_sibling_tree_wide_authority_grep_cannot_hit_this_package() -> None:
    """P-08 §8's closing property: `authority[` hits only `rqa/authority/` and
    `rqa/policy/`. §7 here: never reads `.rqa/config.json`, never interprets
    `snapshot.authority`."""
    for name, source in _sources().items():
        if not name.startswith("rqa/github/"):
            continue
        assert "authority[" not in source, name
        assert "snapshot.authority" not in source, name
        assert ".rqa/config.json" not in source, name


# -- §5: this package alone writes its three tables -------------------------------


def test_only_the_github_store_writes_etags_api_calls_and_mutations() -> None:
    """§5 / the task's tree-wide grep: `mutations`, `etags`, `api_calls` are
    written by `rqa/github/store.py` and by nothing else."""
    writers = []
    for name, source in _sources().items():
        for table in ("etags", "api_calls", "mutations"):
            for verb in (f"INSERT INTO {table}", f"UPDATE {table}", f"DELETE FROM {table}",
                         f"INSERT INTO {table}(", f"insert into {table}"):
                if verb.lower() in source.lower():
                    writers.append((name, table))
                    break
    assert sorted(set(writers)) == [
        ("rqa/github/store.py", "api_calls"),
        ("rqa/github/store.py", "etags"),
        ("rqa/github/store.py", "mutations"),
    ], writers


def test_the_store_schema_carries_the_three_section_five_tables() -> None:
    from rqa.github.store import SCHEMA

    joined = "\n".join(SCHEMA)
    for table, column in (
        ("etags", "cache_key"),
        ("api_calls", "rate_limit"),
        ("mutations", "client_mutation_id"),
    ):
        assert f"CREATE TABLE IF NOT EXISTS {table}" in joined
        assert column in joined


# -- §4/§7: credential hygiene ------------------------------------------------------


def test_no_module_here_prints_or_logs() -> None:
    """§7: the credential is never stored, logged, or persisted; nothing in
    this package writes to stdout or a logger at all."""
    for name, source in _sources().items():
        if not name.startswith("rqa/github/"):
            continue
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                target = node.func
                assert not (isinstance(target, ast.Name) and target.id == "print"), name
        assert "import logging" not in source, name


def test_the_transport_holds_no_credential_field() -> None:
    """§4: resolved fresh per call, held in a local for one HTTP call. The
    Transport dataclass carries resolvers and stores, never a token value."""
    import rqa.github.transport as transport_module

    fields = set(transport_module.Transport.__dataclass_fields__)
    assert fields == {"etags", "api_calls", "send", "resolve_credential"}


def test_the_non_token_credential_is_visibly_not_a_token() -> None:
    from rqa.github.testing import NON_TOKEN_CREDENTIAL

    assert not NON_TOKEN_CREDENTIAL.startswith(("ghp_", "gho_", "ghu_", "ghs_", "github_pat_"))
    assert "token" in NON_TOKEN_CREDENTIAL or "sentinel" in NON_TOKEN_CREDENTIAL


# -- conventions -------------------------------------------------------------------


def test_no_pep_695_type_alias_statements_anywhere_in_the_package() -> None:
    """`type X = ...` is a parse-time SyntaxError on Python 3.11, which the CI
    workflow runs (the Batch 2a trap)."""
    for name, source in _sources().items():
        if not name.startswith("rqa/github/"):
            continue
        for node in ast.walk(ast.parse(source)):
            assert type(node).__name__ != "TypeAlias", f"{name} uses a PEP-695 alias"


def test_the_adapter_methods_carry_the_contracts_signatures() -> None:
    """§3: every public edge has exactly its `CONTRACTS.md` §9 shape after
    `self` — keyword-only, same names, in order."""
    import inspect

    expected = {
        "inventory": ("repo",),
        "claim_lease": ("job", "grant", "record"),
        "release_lease": ("job", "grant", "record"),
        "submit_review": ("job", "state", "body", "grant", "record"),
        "comment": ("job", "body", "grant", "record"),
        "merge": ("job", "grant", "record"),
        "checks": ("repo", "sha"),
        "probe": ("repo", "credential"),
        "facts": ("job", "record"),
    }
    for name, parameter_names in expected.items():
        signature = inspect.signature(getattr(github.GithubAdapter, name))
        parameters = list(signature.parameters.values())[1:]  # drop self
        assert tuple(p.name for p in parameters) == parameter_names, name
        assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in parameters), name
