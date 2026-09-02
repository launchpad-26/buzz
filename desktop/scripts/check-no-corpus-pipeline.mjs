#!/usr/bin/env node
// Guard: the desktop build must never invoke the Python corpus-generation
// pipeline -- #552's DoD bullet 5, and the "one rule" stated in
// launchpad/crates/knowledge/AGENTS.md: this crate (and the desktop build
// that packages it) reads a static, already-committed artifact and never
// re-derives it.
//
// Checks the three build-configuration files BY NAME, not a broad sweep, for
// any reference to launchpad/project-intelligence/corpus -- the pipeline's
// own directory. The generated JSON asset the Settings panel imports lives
// at a different path (desktop/src/launchpad/settings/knowledge/generated/)
// and is referenced only as a relative import, so a legitimate build never
// needs to name the pipeline directory at all -- any occurrence is the
// violation this guard exists to catch.
//
// Run: node desktop/scripts/check-no-corpus-pipeline.mjs
//  or: pnpm check:no-corpus-pipeline (part of `pnpm check`)
//
// The check logic itself lives in checkNoCorpusPipeline() below, exported
// for check-no-corpus-pipeline.test.mjs -- untested until #552's review
// found this guard could go permanently silent (a typo in FILES reads
// identically to a legitimately-absent file, both taking the `continue`
// path with no signal). A missing file is now a hard failure: all three
// entries in FILES are files this repo always carries, so their absence
// means the guard itself is broken, not that there's nothing to check.

import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const desktopRoot = path.resolve(__dirname, "..");
const repoRoot = path.resolve(desktopRoot, "..");

export const FORBIDDEN = "project-intelligence/corpus";

export const DEFAULT_FILES = [
  path.join(desktopRoot, "package.json"),
  path.join(desktopRoot, "vite.config.ts"),
  path.join(desktopRoot, "src-tauri", "tauri.conf.json"),
];

/**
 * Checks each file in `files` for `forbidden`. Returns one violation entry
 * per file that either contains `forbidden` or could not be read at all --
 * a read failure is a violation, not a skip, since every entry in
 * DEFAULT_FILES is expected to exist; treating a missing file as "nothing to
 * check" is exactly how a typo'd path in FILES would go unnoticed forever.
 */
export function checkNoCorpusPipeline(files, forbidden) {
  const violations = [];
  for (const file of files) {
    let content;
    try {
      content = readFileSync(file, "utf8");
    } catch (error) {
      violations.push(
        `could not read ${file} (${error.code ?? error.message}) -- ` +
          "expected this file to exist; check FILES for a typo'd path",
      );
      continue;
    }
    if (content.includes(forbidden)) {
      violations.push(`${file} references "${forbidden}"`);
    }
  }
  return { failed: violations.length > 0, violations };
}

function main() {
  const { failed, violations } = checkNoCorpusPipeline(
    DEFAULT_FILES,
    FORBIDDEN,
  );
  for (const violation of violations) {
    console.error(
      `FAIL  ${violation} -- the desktop build must never invoke the Python ` +
        'corpus pipeline (launchpad/crates/knowledge/AGENTS.md\'s "one rule"; ' +
        "#552 DoD bullet 5).",
    );
  }
  if (failed) {
    process.exit(1);
  }
  console.log(
    `PASS  desktop build files (${DEFAULT_FILES.map((f) => path.relative(repoRoot, f)).join(", ")}) ` +
      "do not invoke the Python corpus pipeline",
  );
}

// Only run as a CLI when invoked directly, not when imported by the test.
// Compares as a URL (via pathToFileURL), not a raw `file://${...}` string --
// on Windows process.argv[1] is backslash-separated, so a naive template
// string never matches and this guard would silently no-op there.
if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main();
}
