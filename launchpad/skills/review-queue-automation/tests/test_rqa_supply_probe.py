#!/usr/bin/env python3
"""`rqa.supply.probe` — `code/P-05-reviewer-supply.md` §4 and §8's T12.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

No test here spawns a real harness or reaches a network. The process primitive is injected
(E-26's `ProcessRunner` shape), and the one test that touches `subprocess` asserts what the
environment handed to a child would contain — never running one.
"""

from __future__ import annotations

import inspect
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa import edges  # noqa: E402
from rqa.contracts import ProcessResult, Route  # noqa: E402
from rqa.supply import route  # noqa: E402
from rqa.supply.probe import (  # noqa: E402
    PROBE_COOLDOWN,
    PROBE_MARKER_NAME,
    PROBE_TIMEOUT_SECONDS,
    VERDICT_FILENAME,
    SubprocessHarnessProber,
    SubprocessProcessRunner,
    _probe_env,
    probe_argv,
)

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from test_rqa_supply_route import (  # noqa: E402
    EMPTY_CURSOR,
    FakeBreakers,
    make_facts,
    make_job,
    make_snapshot,
)

ALIVE = Route(harness="claude", model="claude-sonnet-4-5", provider="anthropic",
              family="anthropic", external=False)
DECLARED = Route(harness="tersely", model="tersely-1", provider="tersely", family="tersely",
                 external=False, command=("/opt/tersely/bin/review", "--json"))


# -- fakes --------------------------------------------------------------------


class RecordingRunner:
    """`ProcessRunner`. Asserts the probe's input, then plays a scripted outcome."""

    def __init__(self, *, returncode: int = 0, write_verdict: bool = False,
                 raises: BaseException | None = None):
        self.returncode = returncode
        self.write_verdict = write_verdict
        self.raises = raises
        self.calls: list[tuple[str, ...]] = []
        self.bundles: list[list[str]] = []
        self.timeouts: list[float] = []

    def run(self, *, cwd: pathlib.Path, argv: tuple[str, ...], timeout: float) -> ProcessResult:
        self.calls.append(argv)
        self.timeouts.append(timeout)
        bundle = pathlib.Path(argv[-2])
        verdict = pathlib.Path(argv[-1])
        self.bundles.append(sorted(entry.name for entry in bundle.iterdir()))
        assert verdict.name == VERDICT_FILENAME
        assert not verdict.exists(), "the probe must start with nothing at the output path"
        if self.raises is not None:
            raise self.raises
        if self.write_verdict:
            verdict.write_text("{}", encoding="utf-8")
        return ProcessResult(returncode=self.returncode, stdout=b"", stderr=b"")


# -- §4's constants ------------------------------------------------------------


def test_the_probe_constants_are_the_ones_section_four_states() -> None:
    assert PROBE_TIMEOUT_SECONDS == 300
    assert PROBE_COOLDOWN.total_seconds() == 300


def test_the_adapter_implements_e24s_protocol_method_character_for_character() -> None:
    """`HarnessProber` is `CONTRACTS.md` §9's, consumed verbatim: `route` positional,
    `timeout` keyword-only, returning `bool`."""
    assert inspect.signature(SubprocessHarnessProber.probe) == inspect.signature(
        edges.HarnessProber.probe
    )


# -- §8 T12 --------------------------------------------------------------------


def test_t12_the_probe_carries_an_empty_bundle_and_a_marker_and_nothing_else() -> None:
    runner = RecordingRunner()
    assert SubprocessHarnessProber(runner=runner).probe(ALIVE, timeout=PROBE_TIMEOUT_SECONDS)
    assert runner.bundles == [[PROBE_MARKER_NAME]]
    assert runner.timeouts == [PROBE_TIMEOUT_SECONDS]


def test_t12_exit_zero_with_no_verdict_written_is_alive() -> None:
    assert SubprocessHarnessProber(runner=RecordingRunner(returncode=0)).probe(ALIVE, timeout=1.0)


def test_t12_a_verdict_written_despite_the_marker_is_not_alive() -> None:
    """A harness that reviews a probe bundle does not honour E-19's published contract, so
    it is unavailable exactly like an absent one."""
    runner = RecordingRunner(returncode=0, write_verdict=True)
    assert SubprocessHarnessProber(runner=runner).probe(ALIVE, timeout=1.0) is False


def test_t12_a_non_zero_exit_is_not_alive() -> None:
    assert SubprocessHarnessProber(runner=RecordingRunner(returncode=2)).probe(ALIVE, timeout=1.0) is False


def test_t12_exceeding_the_timeout_is_not_alive() -> None:
    runner = RecordingRunner(raises=subprocess.TimeoutExpired(cmd="claude", timeout=1.0))
    assert SubprocessHarnessProber(runner=runner).probe(ALIVE, timeout=1.0) is False


def test_t12_a_spawn_failure_is_not_alive_and_never_raises() -> None:
    runner = RecordingRunner(raises=OSError(2, "No such file or directory: 'claude'"))
    assert SubprocessHarnessProber(runner=runner).probe(ALIVE, timeout=1.0) is False


def test_t12_the_probe_leaves_no_workspace_behind() -> None:
    runner = RecordingRunner()
    SubprocessHarnessProber(runner=runner).probe(ALIVE, timeout=1.0)
    bundle = pathlib.Path(runner.calls[0][-2])
    assert not bundle.exists() and not bundle.parent.exists()


# -- argv: whose command runs ---------------------------------------------------


def test_a_registered_harness_is_spawned_by_its_own_name() -> None:
    runner = RecordingRunner()
    SubprocessHarnessProber(runner=runner).probe(ALIVE, timeout=1.0)
    assert runner.calls[0][0] == "claude"


def test_an_operator_declared_command_is_spawned_verbatim() -> None:
    """`RQA-FR-030`: the operator's argv is what runs, in the order they wrote it."""
    runner = RecordingRunner()
    SubprocessHarnessProber(runner=runner).probe(DECLARED, timeout=1.0)
    assert runner.calls[0][: len(DECLARED.command)] == DECLARED.command


def test_probe_argv_appends_the_bundle_and_output_paths_in_that_order() -> None:
    argv = probe_argv(DECLARED, bundle=pathlib.Path("/tmp/b"), verdict=pathlib.Path("/tmp/o/verdict.json"))
    assert argv == (*DECLARED.command, "/tmp/b", "/tmp/o/verdict.json")


def test_the_probe_carries_no_protocol_definition() -> None:
    """§4: no PR content, no protocol definition, nothing to review — the marker directory
    is the entire input."""
    argv = probe_argv(ALIVE, bundle=pathlib.Path("/tmp/b"), verdict=pathlib.Path("/tmp/o/verdict.json"))
    assert len(argv) == 3
    assert not any("protocol" in element for element in argv)


# -- security -------------------------------------------------------------------


def test_the_child_environment_is_an_allowlist_and_carries_no_credential() -> None:
    """E-19: RQA supplies the bundle, the output path and a minimal environment — never a
    credential (`RQA-NFR-025`). The suite sets sentinel GitHub tokens in `conftest.py`;
    neither may reach a harness."""
    environment = _probe_env()
    assert "GITHUB_TOKEN" not in environment
    assert "GH_TOKEN" not in environment
    assert set(environment) <= {"PATH", "HOME", "LANG", "LC_ALL", "TMPDIR"}


def test_a_failed_probe_returns_false_without_re_raising_anything() -> None:
    """A transport error's message and `__context__` can name the argv and the environment
    it was handed. Nothing here re-raises, wraps or returns one — the answer is a bool."""
    secret = "ghp_" + "a" * 36
    carrier = Route(harness="tersely", model="tersely-1", provider="tersely", family="tersely",
                    external=False, command=("/opt/tersely/bin/review", "--token", secret))
    runner = RecordingRunner(raises=RuntimeError(f"spawn failed for --token {secret}"))
    answer = SubprocessHarnessProber(runner=runner).probe(carrier, timeout=1.0)
    assert answer is False
    assert secret not in repr(answer)


def test_an_interrupt_is_not_swallowed_as_a_liveness_answer() -> None:
    runner = RecordingRunner(raises=KeyboardInterrupt())
    try:
        SubprocessHarnessProber(runner=runner).probe(ALIVE, timeout=1.0)
    except KeyboardInterrupt:
        return
    raise AssertionError("KeyboardInterrupt must propagate, not read as 'not alive'")


def test_the_default_runner_is_the_subprocess_one() -> None:
    assert isinstance(SubprocessHarnessProber()._runner, SubprocessProcessRunner)


# -- E-24 through `route()` -----------------------------------------------------


def test_route_drives_the_real_prober_and_returns_the_live_candidate() -> None:
    runner = RecordingRunner()
    answer = route(
        job=make_job(),
        obligation="correctness",
        snapshot=make_snapshot(ALIVE),
        facts=make_facts(),
        cursor=EMPTY_CURSOR,
        prober=SubprocessHarnessProber(runner=runner),
        breakers=FakeBreakers(),
    )
    selected, _ = answer
    assert selected == ALIVE
    assert runner.bundles == [[PROBE_MARKER_NAME]]
