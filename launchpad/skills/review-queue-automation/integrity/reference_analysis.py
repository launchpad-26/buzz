"""Static reference analysis used by the RQA integrity tests.

This is deliberately a small, RQA-scoped analyser rather than a Python-wide dead-code
framework.  It resolves the reference shapes present in RQA and required by #2311 and
#2312: direct and qualified uses, aliases, annotations (recorded separately), ``getattr``
with a literal member, dispatch-table values, and dotted strings in explicitly named
registries.  Imports, re-exports, and alias bindings are bindings, not uses.
"""

from __future__ import annotations

import ast
import dataclasses
import pathlib
from collections import defaultdict
from collections.abc import Iterable


@dataclasses.dataclass(frozen=True, order=True)
class Definition:
    symbol: str
    path: pathlib.Path
    line: int
    kind: str


@dataclasses.dataclass(frozen=True, order=True)
class Reference:
    symbol: str
    path: pathlib.Path
    line: int
    evidence: str
    source_module: str


@dataclasses.dataclass(frozen=True, order=True)
class Finding:
    check: str
    symbol: str
    source: pathlib.Path
    line: int
    detail: str


@dataclasses.dataclass
class _Module:
    name: str
    path: pathlib.Path
    tree: ast.Module
    is_test: bool
    bindings: dict[str, str]
    aliases: dict[str, str]
    definitions: dict[str, Definition]
    exports: tuple[str, ...]


def _module_name(path: pathlib.Path, root: pathlib.Path, package: str) -> str:
    relative = path.relative_to(root)
    pieces = list(relative.with_suffix("").parts)
    if pieces[-1] == "__init__":
        pieces.pop()
    return ".".join([package, *pieces]) if pieces else package


def _literal_all(tree: ast.Module) -> tuple[str, ...]:
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(isinstance(target, ast.Name) and target.id == "__all__" for target in targets):
            continue
        value = node.value
        if not isinstance(value, (ast.List, ast.Tuple)):
            raise AssertionError("reference analysis requires a literal __all__")
        exports: list[str] = []
        for item in value.elts:
            if not isinstance(item, ast.Constant) or not isinstance(item.value, str):
                raise AssertionError("reference analysis requires string-only __all__")
            exports.append(item.value)
        return tuple(exports)
    return ()


def _target_names(node: ast.AST) -> set[str]:
    if isinstance(node, ast.Name):
        return {node.id}
    if isinstance(node, (ast.Tuple, ast.List)):
        return set().union(*(_target_names(item) for item in node.elts))
    return set()


def _top_level_definitions(module: str, path: pathlib.Path, tree: ast.Module) -> dict[str, Definition]:
    found: dict[str, Definition] = {}
    for node in tree.body:
        names: set[str] = set()
        kind = ""
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names, kind = {node.name}, "function"
        elif isinstance(node, ast.ClassDef):
            names, kind = {node.name}, "class"
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = set().union(*(_target_names(target) for target in targets))
            kind = "value"
        for name in names:
            if name.startswith("_") or name == "__all__":
                continue
            found[name] = Definition(f"{module}.{name}", path, node.lineno, kind)
    return found


def _import_from_base(module: str, *, is_package: bool, imported: str, level: int) -> str:
    if level == 0:
        return imported
    package = module if is_package else module.rsplit(".", 1)[0]
    pieces = package.split(".")
    keep = len(pieces) - (level - 1)
    prefix = ".".join(pieces[:keep])
    return f"{prefix}.{imported}" if imported else prefix


def _import_bindings(
    tree: ast.Module,
    known_modules: set[str],
    *,
    module: str,
    is_package: bool,
) -> dict[str, str]:
    bindings: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name.split(".")[0]
                bindings[local] = alias.name if alias.asname else alias.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.module:
            base = _import_from_base(
                module, is_package=is_package, imported=node.module, level=node.level
            )
            for alias in node.names:
                if alias.name == "*":
                    continue
                target = f"{base}.{alias.name}"
                # ``from rqa import authority`` binds a module; keeping the dotted
                # target is also correct for a symbol and avoids guessing.
                bindings[alias.asname or alias.name] = target
    return bindings


def _raw_expr_symbol(node: ast.AST, bindings: dict[str, str]) -> str | None:
    if isinstance(node, ast.Name):
        return bindings.get(node.id)
    if isinstance(node, ast.Attribute):
        base = _raw_expr_symbol(node.value, bindings)
        return f"{base}.{node.attr}" if base else None
    return None


def _assignment_aliases(
    module: str,
    tree: ast.Module,
    bindings: dict[str, str],
    definitions: dict[str, Definition],
) -> dict[str, str]:
    working = dict(bindings)
    working.update({name: definition.symbol for name, definition in definitions.items()})
    aliases: dict[str, str] = {}
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)) or node.value is None:
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        names = set().union(*(_target_names(target) for target in targets))
        if len(names) != 1:
            continue
        target = _raw_expr_symbol(node.value, {**working, **aliases})
        if target:
            name = next(iter(names))
            symbol = f"{module}.{name}"
            if symbol != target:
                aliases[symbol] = target
                working[name] = symbol
    return aliases


def _function_locals(node: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    names = {argument.arg for argument in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)}
    if node.args.vararg:
        names.add(node.args.vararg.arg)
    if node.args.kwarg:
        names.add(node.args.kwarg.arg)
    for child in ast.walk(node):
        if child is node:
            continue
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(child.name)
        elif isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
            names.add(child.id)
        elif isinstance(child, (ast.Import, ast.ImportFrom)):
            for alias in child.names:
                names.add(alias.asname or alias.name.split(".")[0])
    return names


class _ReferenceVisitor(ast.NodeVisitor):
    def __init__(self, module: _Module, known_symbols: set[str], known_modules: set[str]) -> None:
        self.module = module
        self.known_symbols = known_symbols
        self.known_modules = known_modules
        self.references: list[Reference] = []
        self._scopes: list[set[str]] = []
        self._local_bindings: list[dict[str, str]] = []
        self._bindings = dict(module.bindings)
        self._bindings.update({name: definition.symbol for name, definition in module.definitions.items()})

    def _resolve(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            for local in reversed(self._local_bindings):
                if node.id in local:
                    return local[node.id]
            if any(node.id in scope for scope in reversed(self._scopes)):
                return None
            return self._bindings.get(node.id)
        if isinstance(node, ast.Attribute):
            base = self._resolve(node.value)
            return f"{base}.{node.attr}" if base else None
        return None

    def _record(self, symbol: str | None, node: ast.AST, evidence: str) -> None:
        if not symbol:
            return
        candidates = [symbol]
        prefix = symbol
        while "." in prefix:
            prefix = prefix.rsplit(".", 1)[0]
            if prefix in self.known_symbols:
                candidates.append(prefix)
        for candidate in candidates:
            self.references.append(
                Reference(
                    candidate,
                    self.module.path,
                    getattr(node, "lineno", 1),
                    evidence,
                    self.module.name,
                )
            )

    def _visit_annotation(self, node: ast.AST | None) -> None:
        if node is None:
            return
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            try:
                parsed = ast.parse(node.value, mode="eval").body
            except SyntaxError:
                return
            self._visit_annotation(parsed)
            return
        if isinstance(node, (ast.Name, ast.Attribute)):
            self._record(self._resolve(node), node, "annotation")
            if isinstance(node, ast.Attribute):
                return
        for child in ast.iter_child_nodes(node):
            self._visit_annotation(child)

    def visit_Import(self, node: ast.Import) -> None:
        if self._local_bindings:
            for alias in node.names:
                local = alias.asname or alias.name.split(".")[0]
                self._local_bindings[-1][local] = (
                    alias.name if alias.asname else alias.name.split(".")[0]
                )
        return

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if self._local_bindings and node.module:
            base = _import_from_base(
                self.module.name,
                is_package=self.module.path.name == "__init__.py",
                imported=node.module,
                level=node.level,
            )
            for alias in node.names:
                if alias.name != "*":
                    self._local_bindings[-1][alias.asname or alias.name] = (
                        f"{base}.{alias.name}"
                    )
        return

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        for decorator in node.decorator_list:
            self.visit(decorator)
        for default in (*node.args.defaults, *node.args.kw_defaults):
            if default is not None:
                self.visit(default)
        for argument in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs):
            self._visit_annotation(argument.annotation)
        if node.args.vararg:
            self._visit_annotation(node.args.vararg.annotation)
        if node.args.kwarg:
            self._visit_annotation(node.args.kwarg.annotation)
        self._visit_annotation(node.returns)
        self._scopes.append(_function_locals(node))
        self._local_bindings.append({})
        for statement in node.body:
            self.visit(statement)
        self._local_bindings.pop()
        self._scopes.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for decorator in node.decorator_list:
            self.visit(decorator)
        for base in node.bases:
            self.visit(base)
        for keyword in node.keywords:
            self.visit(keyword.value)
        for statement in node.body:
            self.visit(statement)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._visit_annotation(node.annotation)
        if node.value is not None and not self._is_alias_binding(node):
            self.visit(node.value)

    def visit_Assign(self, node: ast.Assign) -> None:
        if any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets):
            return
        if self._is_alias_binding(node):
            return
        registry = any(
            isinstance(target, ast.Name)
            and any(marker in target.id.upper() for marker in ("REGISTRY", "DISPATCH", "HANDLERS"))
            for target in node.targets
        )
        if registry:
            self._visit_registry(node.value)
        else:
            self.visit(node.value)

    def _is_alias_binding(self, node: ast.Assign | ast.AnnAssign) -> bool:
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        names = set().union(*(_target_names(target) for target in targets))
        if len(names) != 1 or node.value is None:
            return False
        symbol = f"{self.module.name}.{next(iter(names))}"
        return symbol in self.module.aliases

    def _visit_registry(self, node: ast.AST) -> None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            candidate = node.value if "." in node.value else f"{self.module.name}.{node.value}"
            if candidate in self.known_symbols:
                self._record(candidate, node, "dynamic-registry")
            return
        self.visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "getattr" and len(node.args) >= 2:
            member = node.args[1]
            base = self._resolve(node.args[0])
            if base and isinstance(member, ast.Constant) and isinstance(member.value, str):
                self._record(f"{base}.{member.value}", member, "dynamic-getattr")
                for argument in node.args[2:]:
                    self.visit(argument)
                for keyword in node.keywords:
                    self.visit(keyword.value)
                return
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if isinstance(node.ctx, ast.Load):
            symbol = self._resolve(node)
            self._record(symbol, node, "runtime")
            if symbol is None:
                self.visit(node.value)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            self._record(self._resolve(node), node, "runtime")


class ReferenceAnalysis:
    def __init__(
        self,
        production_root: pathlib.Path,
        test_root: pathlib.Path,
        *,
        package: str = "rqa",
    ) -> None:
        self.production_root = production_root.resolve()
        self.test_root = test_root.resolve()
        self.package = package
        self.modules = self._load_modules()
        self.known_modules = {module.name for module in self.modules}
        self.definitions = {
            definition.symbol: definition
            for module in self.modules
            if not module.is_test
            for definition in module.definitions.values()
        }
        self.aliases = {
            source: target for module in self.modules for source, target in module.aliases.items()
        }
        for module in self.modules:
            if module.is_test:
                continue
            for local, target in module.bindings.items():
                surface = f"{module.name}.{local}"
                if surface != target:
                    self.aliases[surface] = target
        self.references = self._collect_references()

    def _load_modules(self) -> list[_Module]:
        pending: list[tuple[pathlib.Path, bool, str]] = []
        for path in sorted(self.production_root.rglob("*.py")):
            pending.append((path, False, _module_name(path, self.production_root, self.package)))
        for path in sorted(self.test_root.glob("test_*.py")):
            pending.append((path, True, f"tests.{path.stem}"))

        parsed = [(path, is_test, name, ast.parse(path.read_text(encoding="utf-8"))) for path, is_test, name in pending]
        known_modules = {name for _, _, name, _ in parsed}
        modules: list[_Module] = []
        for path, is_test, name, tree in parsed:
            definitions = {} if is_test else _top_level_definitions(name, path, tree)
            bindings = _import_bindings(
                tree,
                known_modules,
                module=name,
                is_package=path.name == "__init__.py",
            )
            aliases = {} if is_test else _assignment_aliases(name, tree, bindings, definitions)
            modules.append(
                _Module(name, path, tree, is_test, bindings, aliases, definitions, _literal_all(tree))
            )
        return modules

    def _expand_aliases(self, symbol: str) -> tuple[str, ...]:
        expanded = [symbol]
        seen = {symbol}
        current = symbol
        while current in self.aliases and self.aliases[current] not in seen:
            current = self.aliases[current]
            seen.add(current)
            expanded.append(current)
        return tuple(expanded)

    def _collect_references(self) -> tuple[Reference, ...]:
        known_symbols = set(self.definitions)
        references: list[Reference] = []
        for module in self.modules:
            visitor = _ReferenceVisitor(module, known_symbols, self.known_modules)
            visitor.visit(module.tree)
            for reference in visitor.references:
                for symbol in self._expand_aliases(reference.symbol):
                    references.append(dataclasses.replace(reference, symbol=symbol))

            # A surface test that reads a part's ``__all__`` tests every name in that
            # declared contract even when it resolves them through a loop/getattr.
            if module.is_test:
                referenced_modules = {
                    reference.symbol[: -len(".__all__")]
                    for reference in visitor.references
                    if reference.symbol.endswith(".__all__")
                }
                for exported_module in self.modules:
                    if exported_module.name not in referenced_modules:
                        continue
                    for export in exported_module.exports:
                        references.append(
                            Reference(
                                f"{exported_module.name}.{export}",
                                module.path,
                                1,
                                "export-contract",
                                module.name,
                            )
                        )
        return tuple(sorted(set(references)))

    def _export_surfaces(self) -> Iterable[tuple[_Module, str, str]]:
        for module in self.modules:
            if module.is_test or not module.exports:
                continue
            # Architectural parts expose their surface from package ``__init__``;
            # ``rqa.contracts`` is the one file-based shared part.
            if module.path.name != "__init__.py":
                continue
            for name in module.exports:
                surface = f"{module.name}.{name}"
                target = module.bindings.get(name, surface)
                yield module, surface, target

    def t1_findings(self) -> tuple[Finding, ...]:
        findings: list[Finding] = []
        references = defaultdict(list)
        for reference in self.references:
            references[reference.symbol].append(reference)

        for module, surface, target in self._export_surfaces():
            identities = {surface, *self._expand_aliases(target)}
            test_refs = [
                reference
                for identity in identities
                for reference in references[identity]
                if reference.source_module.startswith("tests.")
            ]
            if not test_refs:
                continue
            production_refs = [
                reference
                for identity in identities
                for reference in references[identity]
                if not reference.source_module.startswith("tests.")
                and reference.evidence.startswith(("runtime", "dynamic", "annotation"))
                and reference.source_module != module.name
                and not reference.source_module.startswith(f"{module.name}.")
            ]
            if production_refs:
                continue
            definition = self.definitions.get(target)
            source = definition.path if definition else module.path
            line = definition.line if definition else 1
            detail = (
                f"tested by {len(set(test_refs))} reference(s); "
                f"no recognised production use outside {module.name}"
            )
            findings.append(Finding("T1", surface, source, line, detail))
        return tuple(sorted(findings))

    def t2_findings(self) -> tuple[Finding, ...]:
        """Return every non-private top-level definition with no recognised use.

        Annotation references count here because T2 asks whether *anything* refers to a
        definition.  T1 deliberately applies the stricter runtime-only rule.  Binding an
        import, re-export, or alias does not count until code actually uses the binding.
        """
        referenced = {reference.symbol for reference in self.references}
        findings = [
            Finding("T2", symbol, definition.path, definition.line, "zero recognised references")
            for symbol, definition in self.definitions.items()
            if symbol not in referenced
        ]
        return tuple(sorted(findings))

def format_findings(findings: Iterable[Finding], root: pathlib.Path) -> str:
    rows = []
    for finding in findings:
        try:
            source = finding.source.relative_to(root)
        except ValueError:
            source = finding.source
        rows.append(
            f"{finding.check} {finding.symbol} ({source}:{finding.line}) — {finding.detail}"
        )
    return "\n".join(rows)
