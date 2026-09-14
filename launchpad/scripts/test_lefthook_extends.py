#!/usr/bin/env python3
"""Assert the cohort hook lanes are still wired in, because lefthook fails open.

WHY THIS EXISTS. `lefthook.yml` pulls the cohort lanes in with:

    extends:
      - launchpad/lefthook-launchpad.yml

If that file is deleted, renamed, or moved, **lefthook does not complain**.
Measured: with the target removed, `lefthook dump` exits 0 and simply omits
every lane the file defined. No warning, no error, nothing in the output that
says three checks stopped existing.

That is a fail-open default, and a fail-open default guarding a check is worse
than no check: `git push` stays green and looks like it ran something. The
lanes would vanish exactly when someone tidied a filename.

WHAT THIS CAN AND CANNOT DO. It catches the reference breaking — the realistic
accident. It cannot make lefthook itself fail loudly, and it cannot help if
nothing runs it. That matters because of a circularity worth naming: the
`launchpad-scripts-tests` lane that runs this file is *defined in the file this
test checks for*. If the include disappears, so does the lane that would catch
it. This test therefore only bites when run from CI, from `just`, or by hand —
not from the hook it protects.

So this is a backstop, not a guarantee. The guarantee would be lefthook
erroring on a missing include, which is not in its behaviour.
"""

from __future__ import annotations

import os
import subprocess
import unittest

try:
    import yaml
except ImportError:  # pragma: no cover
    raise SystemExit("PyYAML is required: pip install pyyaml")


def repo_root() -> str:
    return subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


# The lanes this fork relies on. Named explicitly rather than counted, so
# deleting one is a failure rather than a smaller number nobody notices.
EXPECTED_LANES = {
    "launchpad-scripts-tests",
    "launchpad-adr-check",
    "launchpad-corpus-schema-tests",
}


class LefthookExtendsWiring(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = repo_root()
        with open(os.path.join(cls.root, "lefthook.yml"), encoding="utf-8") as fh:
            cls.root_cfg = yaml.safe_load(fh)

    def test_root_config_extends_the_cohort_file(self) -> None:
        extends = self.root_cfg.get("extends") or []
        self.assertIn(
            "launchpad/lefthook-launchpad.yml", extends,
            "lefthook.yml no longer extends launchpad/lefthook-launchpad.yml. "
            "Every cohort pre-push lane is defined there, and lefthook drops "
            "them SILENTLY when the reference is gone.",
        )

    def test_the_extended_file_exists(self) -> None:
        for rel in self.root_cfg.get("extends") or []:
            with self.subTest(extends=rel):
                self.assertTrue(
                    os.path.exists(os.path.join(self.root, rel)),
                    f"lefthook.yml extends {rel}, which does not exist. "
                    "lefthook exits 0 and omits its lanes rather than failing, "
                    "so nothing else will tell you.",
                )

    def test_every_expected_lane_is_defined(self) -> None:
        path = os.path.join(self.root, "launchpad/lefthook-launchpad.yml")
        if not os.path.exists(path):
            self.skipTest("covered by test_the_extended_file_exists")
        with open(path, encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh)
        defined = set((cfg.get("pre-push") or {}).get("commands") or {})
        missing = EXPECTED_LANES - defined
        self.assertFalse(
            missing,
            f"cohort pre-push lane(s) missing: {sorted(missing)}. Removing a "
            "lane is a decision; losing one is not.",
        )

    # Lanes that shell out to a suite which may itself run git. Named
    # explicitly: a future lane that runs git should be added here deliberately
    # rather than swept in by a wildcard.
    LANES_NEEDING_GIT_ENV_SCRUB = {"launchpad-scripts-tests"}

    # What git exports into a hook and honours over a subprocess's `cwd=`.
    REQUIRED_UNSETS = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")

    def test_git_env_is_scrubbed_where_tests_run_git(self) -> None:
        """Without this, a fixture's commits land in the repo being pushed.

        Measured, not hypothetical. The first version of this lane put 15
        commits titled "test fixture", authored `test <test@example.com>`, onto
        the branch being pushed — because git hooks export GIT_DIR and git
        honours it over a subprocess's `cwd=`, so suites that isolate their
        fixture repository with `cwd=` alone write into the real one instead.

        The damage was local and silent: the push aborted, nothing reached the
        remote, and the only symptom was `git status`. Deleting `env -u` would
        reintroduce it and nothing else here would notice — hence this test.
        """
        path = os.path.join(self.root, "launchpad/lefthook-launchpad.yml")
        if not os.path.exists(path):
            self.skipTest("covered by test_the_extended_file_exists")
        with open(path, encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh)
        lanes = (cfg.get("pre-push") or {}).get("commands") or {}
        for name in self.LANES_NEEDING_GIT_ENV_SCRUB:
            with self.subTest(lane=name):
                run = (lanes.get(name) or {}).get("run", "")
                for var in self.REQUIRED_UNSETS:
                    self.assertIn(
                        f"-u {var}", run,
                        f"{name} does not unset {var}. Git hooks export it, and "
                        "git honours it over a subprocess's cwd, so a fixture "
                        "repository built by these tests would commit into the "
                        "repository being pushed.",
                    )

    def test_each_lane_is_path_scoped(self) -> None:
        """An unscoped lane runs on every push, which is how hooks get bypassed."""
        path = os.path.join(self.root, "launchpad/lefthook-launchpad.yml")
        if not os.path.exists(path):
            self.skipTest("covered by test_the_extended_file_exists")
        with open(path, encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh)
        for name, lane in ((cfg.get("pre-push") or {}).get("commands") or {}).items():
            with self.subTest(lane=name):
                self.assertIn("glob", lane, f"{name} has no glob: it would run on every push")
                self.assertIn("files", lane, f"{name} has no files: its glob has nothing to match")


if __name__ == "__main__":
    unittest.main(verbosity=2)
