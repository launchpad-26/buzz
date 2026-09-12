#!/usr/bin/env python3
"""P-06 §5 — the bundle, its envelopes and its fail-closed publication.

§8 rows covered here:

T14  every PR-derived field and arbitrary binary bytes -> no PR byte appears outside an
     envelope
T16  bundle assembly failure -> no attempt, no final bundle, shared `BundleFailure`

T14 is written as a walk of the produced tree rather than a spot-check of named fields,
because a field enumeration is exactly what a crafted pull request gets to be absent
from. Three separate properties are asserted: every artifact file is *entirely* one
envelope; no planted token survives anywhere outside one, including in a filename, in the
manifest, and in its base64 rendering; and the original bytes come back verbatim through
`extract()` — U-DOCS-26's salvage note is that the incumbent test "does not assert
verbatim content retention".
"""

from __future__ import annotations

import base64
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import test_rqa_harness_fixtures as fx  # noqa: E402
from rqa.contracts import BundleFailure  # noqa: E402
from rqa.harness.bundle import (  # noqa: E402
    ARTIFACTS_DIRNAME,
    MANIFEST_NAME,
    Bundle,
    assemble,
    protocol_instruction_path,
    text_artifacts,
)
from rqa.harness.errors import ProtocolVersionUnknown  # noqa: E402
from rqa.protocol import envelope, extract  # noqa: E402


def _assemble(state_dir: pathlib.Path, *, facts=None, snapshot=None):
    return assemble(
        job_id="job-1",
        facts=facts if facts is not None else fx.make_facts(),
        snapshot=snapshot if snapshot is not None else fx.make_snapshot(),
        state_dir=state_dir,
    )


def _artifact_files(bundle: Bundle) -> list[pathlib.Path]:
    root = bundle.path / ARTIFACTS_DIRNAME
    return sorted(path for path in root.rglob("*") if path.is_file())


def _label_of(bundle: Bundle, path: pathlib.Path) -> str:
    return path.relative_to(bundle.path / ARTIFACTS_DIRNAME).as_posix()


# -- T14 ------------------------------------------------------------------------


def test_t14_every_artifact_file_is_exactly_one_envelope() -> None:
    with fx.workspace() as raw:
        bundle = _assemble(pathlib.Path(raw))
        assert isinstance(bundle, Bundle)
        for path in _artifact_files(bundle):
            label = _label_of(bundle, path)
            text = path.read_text(encoding="utf-8")
            content = extract(text=text, label=label, nonce=bundle.nonce)
            assert content is not None, f"{label} is not an envelope keyed by this bundle"
            # Not merely "contains an envelope": the file *is* the envelope, so there is
            # no room beside it for an unenveloped byte.
            assert text == envelope(label=label, nonce=bundle.nonce, content=content)


def test_t14_no_pr_derived_token_survives_outside_an_envelope() -> None:
    with fx.workspace() as raw:
        bundle = _assemble(pathlib.Path(raw))
        assert isinstance(bundle, Bundle)
        tokens = list(fx.TOKENS.values())
        encoded = [base64.b64encode(token.encode()).decode() for token in tokens]
        for path in sorted(bundle.path.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(bundle.path).as_posix()
            for token in tokens:
                assert token not in relative, f"{token} used as a bundle path: {relative}"
            text = path.read_text(encoding="utf-8", errors="replace")
            if relative == MANIFEST_NAME:
                residue = text
            else:
                label = _label_of(bundle, path)
                content = extract(text=text, label=label, nonce=bundle.nonce)
                residue = text.replace(
                    envelope(label=label, nonce=bundle.nonce, content=content or ""), ""
                )
            for token in tokens + encoded:
                assert token not in residue, f"{token} outside an envelope in {relative}"


def test_t14_arbitrary_binary_bytes_round_trip_verbatim() -> None:
    with fx.workspace() as raw:
        bundle = _assemble(pathlib.Path(raw))
        assert isinstance(bundle, Bundle)
        recovered = []
        for path in _artifact_files(bundle):
            label = _label_of(bundle, path)
            if not label.startswith("files/"):
                continue
            content = extract(text=path.read_text(encoding="utf-8"), label=label, nonce=bundle.nonce)
            assert content is not None
            recovered.append(base64.b64decode(content))
        assert recovered == [fx.BINARY]
        # And the raw bytes never appear anywhere in the tree, enveloped or not: only
        # their base64 rendering may.
        for path in sorted(bundle.path.rglob("*")):
            if path.is_file():
                assert fx.BINARY not in path.read_bytes()


def test_t14_every_text_channel_is_recoverable_verbatim() -> None:
    with fx.workspace() as raw:
        facts = fx.make_facts()
        snapshot = fx.make_snapshot()
        bundle = _assemble(pathlib.Path(raw), facts=facts, snapshot=snapshot)
        assert isinstance(bundle, Bundle)
        expected = text_artifacts(facts=facts, snapshot=snapshot)
        for label, content in expected.items():
            path = bundle.path / ARTIFACTS_DIRNAME / label
            assert extract(text=path.read_text(encoding="utf-8"), label=label, nonce=bundle.nonce) == content
        # Every planted token is in some channel, and the diff, title, body, labels,
        # changed paths, check names, author, branch and comment actor are all covered.
        joined = "\n".join(expected.values())
        for token in fx.TOKENS.values():
            assert token in joined, token


def test_t14_a_wrong_nonce_recovers_nothing() -> None:
    with fx.workspace() as raw:
        bundle = _assemble(pathlib.Path(raw))
        assert isinstance(bundle, Bundle)
        path = bundle.path / ARTIFACTS_DIRNAME / "diff"
        assert extract(text=path.read_text(encoding="utf-8"), label="diff", nonce="0" * 32) is None


def test_t14_the_manifest_carries_only_nonce_protocol_hash_and_artifact_hashes() -> None:
    with fx.workspace() as raw:
        bundle = _assemble(pathlib.Path(raw))
        assert isinstance(bundle, Bundle)
        manifest = json.loads((bundle.path / MANIFEST_NAME).read_text(encoding="utf-8"))
        assert set(manifest) == {"nonce", "protocol_hash", "artifacts"}
        assert manifest["nonce"] == bundle.nonce
        assert manifest["protocol_hash"] == bundle.protocol_hash
        for label, digest in manifest["artifacts"].items():
            assert len(digest) == 64 and all(c in "0123456789abcdef" for c in digest)
            assert (bundle.path / ARTIFACTS_DIRNAME / label).is_file()


def test_t14_the_nonce_is_fresh_for_every_bundle() -> None:
    with fx.workspace() as raw:
        first = _assemble(pathlib.Path(raw))
        second = _assemble(pathlib.Path(raw))
        assert isinstance(first, Bundle) and isinstance(second, Bundle)
        assert first.nonce != second.nonce


def test_a_changed_path_name_is_never_a_filename_but_is_in_the_index() -> None:
    """The filename is not in the file: a path used as a bundle filename would be a PR
    byte no envelope can cover."""
    with fx.workspace() as raw:
        path = f"src/{fx.TOKENS['path']}.py"
        bundle = _assemble(pathlib.Path(raw), facts=fx.make_facts(changed_paths=frozenset({path})))
        assert isinstance(bundle, Bundle)
        index = bundle.path / ARTIFACTS_DIRNAME / "file_index"
        content = extract(text=index.read_text(encoding="utf-8"), label="file_index", nonce=bundle.nonce)
        assert content is not None and path in content
        assert (bundle.path / ARTIFACTS_DIRNAME / "files" / "000001").is_file()


def test_the_protocol_instruction_is_a_packaged_file_not_a_bundle_artifact() -> None:
    """§3.3: RQA supplies the bundle, the protocol instruction and the verdict path. The
    instruction is version-controlled beside the schema, never assembled from PR bytes."""
    assert protocol_instruction_path().is_file()
    assert protocol_instruction_path().name == "PROTOCOL.md"


# -- T16 ------------------------------------------------------------------------


def test_t16_assembly_failure_returns_bundle_failure_and_leaves_no_final_bundle() -> None:
    with fx.workspace() as raw:
        state_dir = pathlib.Path(raw)
        # `jobs` is a regular file, so creating the job directory beneath it fails.
        (state_dir / "jobs").write_text("not a directory", encoding="utf-8")
        failure = _assemble(state_dir)
        assert isinstance(failure, BundleFailure)
        assert failure.reason
        assert not (state_dir / "jobs" / "job-1").exists()


def test_t16_a_failed_assembly_leaves_no_staging_directory() -> None:
    with fx.workspace() as raw:
        state_dir = pathlib.Path(raw)
        job_dir = state_dir / "jobs" / "job-1"
        job_dir.mkdir(parents=True)
        # A file where the bundle directory must go: the rename at the end fails.
        (job_dir / "bundle").write_text("occupied", encoding="utf-8")
        failure = _assemble(state_dir)
        assert isinstance(failure, BundleFailure)
        assert [entry.name for entry in job_dir.iterdir() if entry.name.startswith(".bundle")] == []


def test_t16_the_failure_reason_carries_no_pr_byte() -> None:
    with fx.workspace() as raw:
        state_dir = pathlib.Path(raw)
        (state_dir / "jobs").write_text("not a directory", encoding="utf-8")
        failure = _assemble(state_dir)
        assert isinstance(failure, BundleFailure)
        for token in fx.TOKENS.values():
            assert token not in failure.reason


def test_a_pinned_protocol_this_build_does_not_package_is_a_deployment_error() -> None:
    from dataclasses import replace

    with fx.workspace() as raw:
        snapshot = replace(fx.make_snapshot(), protocol_hash="deadbeef")
        try:
            _assemble(pathlib.Path(raw), snapshot=snapshot)
        except ProtocolVersionUnknown:
            return
        raise AssertionError("an unknown pinned protocol hash must not produce a bundle")


def test_a_stale_bundle_from_an_earlier_run_is_cleared() -> None:
    """U-VERDICT-12's clearing rule, applied to the bundle: a re-run must not be able to
    invoke against bytes captured under an earlier head."""
    with fx.workspace() as raw:
        state_dir = pathlib.Path(raw)
        first = _assemble(state_dir)
        assert isinstance(first, Bundle)
        (first.path / ARTIFACTS_DIRNAME / "stale-leftover").write_text("old", encoding="utf-8")
        second = _assemble(state_dir)
        assert isinstance(second, Bundle)
        assert not (second.path / ARTIFACTS_DIRNAME / "stale-leftover").exists()
