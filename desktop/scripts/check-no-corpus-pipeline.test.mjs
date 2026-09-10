import assert from "node:assert/strict";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";

import {
  checkNoCorpusPipeline,
  FORBIDDEN,
} from "./check-no-corpus-pipeline.mjs";

function fixtureFile(content) {
  const dir = mkdtempSync(path.join(tmpdir(), "no-corpus-pipeline-"));
  const file = path.join(dir, "config.json");
  writeFileSync(file, content, "utf8");
  return file;
}

test("passes when no file references the pipeline directory", () => {
  const file = fixtureFile('{"scripts": {"build": "vite build"}}');
  const { failed, violations } = checkNoCorpusPipeline([file], FORBIDDEN);
  assert.equal(failed, false);
  assert.deepEqual(violations, []);
});

test("fails when a file references the pipeline directory", () => {
  const file = fixtureFile(
    '{"scripts": {"build": "python3 launchpad/project-intelligence/corpus/package.py && vite build"}}',
  );
  const { failed, violations } = checkNoCorpusPipeline([file], FORBIDDEN);
  assert.equal(failed, true);
  assert.equal(violations.length, 1);
  assert.match(violations[0], /references "project-intelligence\/corpus"/);
});

test("fails on a missing file rather than silently skipping it", () => {
  // The regression this guards: a typo'd path in FILES used to `continue`
  // past a missing file identically to a legitimately-absent one, so the
  // guard could go permanently silent with nobody noticing. A read failure
  // must be a violation, not a skip.
  const missing = path.join(
    mkdtempSync(path.join(tmpdir(), "no-corpus-pipeline-")),
    "does-not-exist.json",
  );
  const { failed, violations } = checkNoCorpusPipeline([missing], FORBIDDEN);
  assert.equal(failed, true);
  assert.equal(violations.length, 1);
  assert.match(violations[0], /could not read/);
});

test("checks every file independently -- one clean file does not mask a violation in another", () => {
  const clean = fixtureFile("clean");
  const dirty = fixtureFile("project-intelligence/corpus is here");
  const { failed, violations } = checkNoCorpusPipeline(
    [clean, dirty],
    FORBIDDEN,
  );
  assert.equal(failed, true);
  assert.equal(violations.length, 1);
  assert.ok(violations[0].includes(dirty));
});

test("the real desktop build files pass today", async () => {
  const { DEFAULT_FILES } = await import("./check-no-corpus-pipeline.mjs");
  const { failed, violations } = checkNoCorpusPipeline(
    DEFAULT_FILES,
    FORBIDDEN,
  );
  assert.equal(failed, false, violations.join("; "));
});
