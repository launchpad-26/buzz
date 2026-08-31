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

import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const desktopRoot = path.resolve(__dirname, "..");
const repoRoot = path.resolve(desktopRoot, "..");

const FORBIDDEN = "project-intelligence/corpus";

const FILES = [
  path.join(desktopRoot, "package.json"),
  path.join(desktopRoot, "vite.config.ts"),
  path.join(desktopRoot, "src-tauri", "tauri.conf.json"),
];

let failed = false;
for (const file of FILES) {
  let content;
  try {
    content = readFileSync(file, "utf8");
  } catch {
    // A file may legitimately not exist (e.g. a future config split);
    // nothing to check in that case.
    continue;
  }
  if (content.includes(FORBIDDEN)) {
    failed = true;
    console.error(
      `FAIL  ${path.relative(repoRoot, file)} references "${FORBIDDEN}" -- ` +
        "the desktop build must never invoke the Python corpus pipeline " +
        '(launchpad/crates/knowledge/AGENTS.md\'s "one rule"; #552 DoD bullet 5).',
    );
  }
}

if (failed) {
  process.exit(1);
}

console.log(
  "PASS  desktop build files (package.json, vite.config.ts, tauri.conf.json) " +
    "do not invoke the Python corpus pipeline",
);
