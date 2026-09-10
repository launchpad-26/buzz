---
id: development-typescript-style
type: development
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "The repository has exactly one substantive Biome configuration -- the root biome.json -- and desktop/biome.json and web/biome.json each contain nothing but {\"extends\": [\"../biome.json\"]}, so every Biome rule and formatting option applied to desktop and web source is declared in that one root file."
    entry_class: FACT
    evidence:
      - "biome.json"
      - "desktop/biome.json"
      - "web/biome.json"
  - statement: "The root biome.json enables the formatter with indentStyle 'space' and javascript.formatter.quoteStyle 'double', enables the linter with rules.recommended true and the single override suspicious.noUnknownAtRules 'off', sets assist.enabled to false, sets files.ignoreUnknown to false, enables vcs integration with useIgnoreFile true, and enables css.parser.tailwindDirectives."
    entry_class: FACT
    evidence:
      - "biome.json"
  - statement: "Biome is declared once, at the workspace root, as devDependency '@biomejs/biome': '^2.4.6'; the root biome.json pins its $schema to the 2.4.14 schema; and pnpm-lock.yaml resolves the dependency to @biomejs/biome@2.4.16."
    entry_class: FACT
    evidence:
      - "package.json"
      - "biome.json"
      - "pnpm-lock.yaml"
  - statement: "desktop/tsconfig.json and web/tsconfig.json both set strict, noUnusedLocals, noUnusedParameters and noFallthroughCasesInSwitch to true, target ES2020, module ESNext, moduleResolution 'bundler', isolatedModules, noEmit, allowImportingTsExtensions, resolveJsonModule, useDefineForClassFields, jsx 'react-jsx', and each includes only 'src' with a project reference to its own tsconfig.node.json."
    entry_class: FACT
    evidence:
      - "desktop/tsconfig.json"
      - "web/tsconfig.json"
  - statement: "admin-web/tsconfig.json sets strict, forceConsistentCasingInFileNames, esModuleInterop, allowSyntheticDefaultImports and allowJs false, targets ES2022, and does NOT set noUnusedLocals, noUnusedParameters or noFallthroughCasesInSwitch -- so admin-web compiles under a materially weaker unused-code and switch-fallthrough contract than desktop and web."
    entry_class: FACT
    evidence:
      - "admin-web/tsconfig.json"
      - "desktop/tsconfig.json"
      - "web/tsconfig.json"
  - statement: "The three front-end packages define different 'check' scripts: desktop's is 'biome check . && pnpm check:px-text && pnpm check:pubkey-truncation', web's is 'biome check . && pnpm check:pubkey-truncation', and admin-web's is 'biome check . && pnpm typecheck && pnpm test'; only admin-web's check script runs tsc, and neither desktop's nor web's check script runs tsc or the file-size guard."
    entry_class: FACT
    evidence:
      - "desktop/package.json"
      - "web/package.json"
      - "admin-web/package.json"
  - statement: "desktop/package.json and web/package.json each declare a 'check:file-sizes' script that no other script, Justfile recipe, lefthook lane or workflow step invokes; the Justfile's file-size-check recipe runs the underlying .mjs files directly instead."
    entry_class: FACT
    evidence:
      - "desktop/package.json"
      - "web/package.json"
      - "Justfile"
      - "grep(pattern='check:file-sizes', paths=['Justfile','lefthook.yml','.github/workflows/*.yml','package.json','desktop/package.json','web/package.json']) -> only desktop/package.json and web/package.json declare it; no invoker found"
  - statement: "The Justfile's aggregate 'check' recipe depends on fmt-check, clippy, desktop-check, desktop-tauri-fmt-check, desktop-tauri-clippy, web-check, mobile-check, security-review-check and file-size-check -- it does not depend on desktop-typecheck, web-typecheck or admin-check."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "The Justfile's 'ci' recipe is 'check test-unit desktop-test desktop-build desktop-tauri-check desktop-tauri-test web-build mobile-test', and desktop-build and web-build each run 'pnpm build', which is 'tsc && vite build' in both packages -- so TypeScript type errors reach 'just ci' through the build step rather than through a typecheck recipe."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "desktop/package.json"
      - "web/package.json"
  - statement: "The Justfile defines a 'web-typecheck' recipe running 'pnpm typecheck' in web/, but no Justfile recipe, lefthook lane or GitHub Actions step invokes it."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "grep(pattern='web-typecheck', paths=['Justfile','lefthook.yml','.github/workflows/*.yml']) -> Justfile:722 (the recipe definition) only; no invocation"
  - statement: "lefthook.yml's pre-commit stage runs desktop-fix (glob desktop/**, excluding desktop/src-tauri/**) and web-fix (glob web/**) with stage_fixed true, and both recipes run 'pnpm exec biome check --write .' -- so Biome formatting and auto-fixable lint issues are rewritten and re-staged at commit time for desktop and web."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
      - "Justfile"
  - statement: "lefthook.yml's pre-push stage has desktop-check, desktop-typecheck and desktop-test lanes (glob desktop/**, pnpm-lock.yaml, excluding desktop/src-tauri/**) and an unfiltered file-size-check lane, but no web lane and no admin-web lane of any kind."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "Each globbed pre-push lane sets 'files: git diff --name-only origin/main...HEAD', so a lane fires only when the branch's merge-base diff touches a path its glob matches; the file-size-check lane is deliberately unfiltered because the ratchet computes its own merge-base diff; and lefthook.yml records that lefthook 2.1.x drops deleted paths from push-file discovery, so a deletion-only surface change triggers no local lane and CI's paths-filter is what catches it."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "In .github/workflows/ci.yml the Desktop Core job runs 'just desktop-check', 'just desktop-test' and 'just desktop-build', and the Web job runs 'just web-check' and 'just web-build'; neither job runs a standalone typecheck step, and the repository-wide 'just file-size-check' runs as its own unfiltered step."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "The dorny/paths-filter groups in .github/workflows/ci.yml define desktop, desktop-rust, web, rust and mobile filters, and no filter, job or step in any file under .github/workflows/ references admin-web -- so admin-web has no continuous-integration coverage in this repository."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
      - "grep(pattern='admin-web|admin_web', path='.github/workflows/*.yml') -> no matches"
  - statement: "admin-web is checked only by the Justfile's 'admin-check' recipe (which runs 'pnpm -C admin-web check' and 'pnpm -C admin-web test:e2e' alongside Rust checks), and that recipe is not a dependency of 'check' or 'ci'."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "The px-text guard's shared core, scripts/check-px-text-core.mjs, flags two patterns: the Tailwind arbitrary text-size regex /\\btext-\\[\\d+(?:\\.\\d+)?(?:px|rem|em)\\]/g -- which matches px, rem AND em literals -- and the CSS regex /(?<!-)\\bfont-size:\\s*\\d+(?:\\.\\d+)?px/g, whose negative lookbehind deliberately spares custom properties named --font-size."
    entry_class: FACT
    evidence:
      - "scripts/check-px-text-core.mjs"
  - statement: "The px-text guard's allowlist key is `${relativePath}:${match}` -- a path paired with the matched literal, not a path paired with a line number -- and desktop/scripts/check-px-text.mjs states in comment that matching the literal 'keeps these exceptions stable when unrelated edits move lines'; its four current entries are the text-[6rem] and text-[4rem] avatar/preview glyphs."
    entry_class: FACT
    evidence:
      - "scripts/check-px-text-core.mjs"
      - "desktop/scripts/check-px-text.mjs"
  - statement: "The px-text guard, its shared core, the desktop rem-token additions to tailwind.config.js and the AGENTS.md 'Text sizing & zoom' section were all introduced by one upstream commit, c22c54e7ae4318f9648dc9441a152732cb29d6d5 ('fix(desktop): restore timeline zoom via rem tokens + chat-as-base type scale (#1052)'); the guard's own comment attributes the regression it prevents to a different, earlier PR (#891)."
    entry_class: FACT
    evidence:
      - "git_show(commit='c22c54e7ae4318f9648dc9441a152732cb29d6d5', stat=true) -> adds AGENTS.md +34, desktop/scripts/check-px-text.mjs +36, scripts/check-px-text-core.mjs +126, desktop/tailwind.config.js +9"
      - "desktop/scripts/check-px-text.mjs"
      - "scripts/check-px-text-core.mjs"
  - statement: "AGENTS.md states that decorative glyphs 'are allowlisted by `path:line`' in desktop/scripts/check-px-text.mjs; that statement is false -- the script's overrides set contains path-plus-literal entries and the core composes its lookup key from the matched literal, never from a line number."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
      - "desktop/scripts/check-px-text.mjs"
      - "scripts/check-px-text-core.mjs"
  - statement: "desktop/scripts/check-px-text.mjs scans desktop/src recursively for .ts, .tsx and .css files, and it is the only importer of scripts/check-px-text-core.mjs anywhere in the repository -- web/ and admin-web/ have no px-text guard."
    entry_class: FACT
    evidence:
      - "desktop/scripts/check-px-text.mjs"
      - "grep(pattern='check-px-text-core', scope='repository excluding node_modules and .git') -> desktop/scripts/check-px-text.mjs:3 only"
  - statement: "desktop/tailwind.config.js declares the named rem-derived fontSize tokens 2xs (0.6875 x --buzz-type-rem), 3xs (0.5x), badge (0.625x), message, message-timestamp, title (2.5x) and nsec-key (2.25x), and its own comment instructs authors not to reintroduce arbitrary text-[…rem] / text-[…px] literals because the px-text guard rejects them."
    entry_class: FACT
    evidence:
      - "desktop/tailwind.config.js"
  - statement: "desktop/src/shared/styles/globals/typography.css defines --buzz-type-rem as calc(1rem * var(--buzz-type-scale)) and derives the --text-xs through --text-5xl ramp and --conversation-message-font-size (0.875 x --buzz-type-rem) from it, so every named token in tailwind.config.js is rem-relative rather than an absolute pixel size."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/styles/globals/typography.css"
      - "desktop/tailwind.config.js"
  - statement: "desktop/src/app/useWebviewZoomShortcuts.ts implements keyboard zoom by assigning document.documentElement.style.fontSize and pins the native webview zoom via webview.setZoom(DEFAULT_ZOOM_FACTOR), which is the mechanism that makes rem-based text scale and hardcoded px text stay frozen."
    entry_class: FACT
    evidence:
      - "desktop/src/app/useWebviewZoomShortcuts.ts"
  - statement: "The pubkey-truncation guard (desktop/scripts/check-pubkey-truncation.mjs, run by desktop's and web's 'check' scripts) uses a path-and-line allowlist of the form 'src/path/File.tsx:150' plus an allowedFiles set, which is a different allowlist shape from the px-text guard's path-and-literal keys."
    entry_class: FACT
    evidence:
      - "desktop/scripts/check-pubkey-truncation.mjs"
      - "desktop/package.json"
      - "web/package.json"
  - statement: "The file-size gate is a differential ratchet, not a flat ceiling: scripts/check-file-sizes-core.mjs's allowedLineCount returns maxLines when the base revision's line count is null or already within maxLines, and otherwise returns the base line count -- so a file that is already over 1000 lines is permitted to stay at its current size but may not grow."
    entry_class: FACT
    evidence:
      - "scripts/check-file-sizes-core.mjs"
  - statement: "The TypeScript roots governed by the file-size ratchet are enumerated per project: desktop/scripts/check-file-sizes.mjs governs src/app, src/features, src/shared/api, src/shared/context, src/shared/lib, src/shared/ui (.ts/.tsx) plus src/shared/styles (.css) and two Rust roots, while web/scripts/check-file-sizes.mjs governs only src/app, src/features and src/shared/api; both set MAX_LINES to 1000, and TypeScript outside those roots is ungoverned."
    entry_class: FACT
    evidence:
      - "desktop/scripts/check-file-sizes.mjs"
      - "web/scripts/check-file-sizes.mjs"
  - statement: "scripts/check-file-sizes-core.mjs's resolveBaseRef prefers CHECK_FILE_SIZES_BASE, then 'HEAD^1' when GITHUB_ACTIONS is 'true', and otherwise the merge base of origin/main and HEAD -- so the ratchet's comparison point is a base revision, not the working tree."
    entry_class: FACT
    evidence:
      - "scripts/check-file-sizes-core.mjs"
  - statement: "AGENTS.md's React.memo reference-stability guidance and its rem-not-px prose are review-enforced only: no script under scripts/, desktop/scripts/, web/scripts/ or .github/ references React.memo or useStableReference, and desktop/src/shared/hooks/useStableReference.ts is a helper the guidance points at rather than a rule any gate applies."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
      - "desktop/src/shared/hooks/useStableReference.ts"
      - "grep(pattern='React.memo|useStableReference', paths=['scripts/','desktop/scripts/','web/scripts/','.github/']) -> no matches"
  - statement: "CONTRIBUTING.md's 'Code Style' section covers rustfmt, clippy, unsafe code, thiserror/anyhow error handling and tracing only, and contains no mention of TypeScript, Biome, React or any front-end convention."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
      - "grep(pattern='code style|biome|typescript|prettier|eslint', path='CONTRIBUTING.md', ignore_case=true) -> two hits, both the table-of-contents entry and the section heading 'Code Style'; no front-end term matches"
  - statement: "No ESLint or Prettier configuration exists in the repository outside node_modules: a search for .eslintrc*, eslint.config* at depth 3 returns nothing, and Biome is the sole JavaScript/TypeScript formatter and linter."
    entry_class: FACT
    evidence:
      - "biome.json"
      - "find(maxdepth=3, names=['.eslintrc*','eslint.config*'], excluding='node_modules') -> no results"
  - statement: "Because neither desktop's nor web's package 'check' script runs tsc, and no CI job runs a standalone typecheck step, a TypeScript type error in desktop or web is caught in CI only by the build step's leading tsc invocation -- and in web's case by nothing at all before push, since lefthook has no web lane."
    entry_class: INFERENCE
    evidence:
      - "desktop/package.json"
      - "web/package.json"
      - "Justfile"
      - "lefthook.yml"
      - ".github/workflows/ci.yml"
    confidence: 0.9
  - statement: "Since admin-web has no biome.json of its own while its 'lint' and 'check' scripts invoke 'biome check .', Biome most likely resolves the root biome.json by upward configuration discovery, giving admin-web the same formatter and linter rules as desktop and web; this was reasoned from the configuration layout rather than observed by running Biome."
    entry_class: INFERENCE
    evidence:
      - "admin-web/package.json"
      - "biome.json"
      - "find(maxdepth=3, name='biome*.json*', excluding='node_modules') -> ./biome.json, ./web/biome.json, ./desktop/biome.json"
    confidence: 0.6
  - statement: "At revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90 the development/ directory of the corpus on origin/launchpad contains exactly build.md, debugging.md, hermit.md and prerequisites.md, so no sibling language-style node exists yet to duplicate or contradict."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/build.md"
      - "launchpad/docs/corpus/development/debugging.md"
      - "launchpad/docs/corpus/development/hermit.md"
      - "launchpad/docs/corpus/development/prerequisites.md"
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> development/build.md, development/debugging.md, development/hermit.md, development/prerequisites.md and no other file under development/, at commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "The relationship targets declared by this node resolve on origin/launchpad: development/build.md carries id corpus-development-build, architecture/containers/desktop.md carries id architecture-containers-desktop, architecture/containers/web.md carries id architecture-containers-web, and templates/reference.md carries id corpus-template-reference."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/build.md"
      - "launchpad/docs/corpus/architecture/containers/desktop.md"
      - "launchpad/docs/corpus/architecture/containers/web.md"
      - "launchpad/docs/corpus/templates/reference.md"
      - "git_show(ref='origin/launchpad', paths=['launchpad/docs/corpus/development/build.md','launchpad/docs/corpus/architecture/containers/desktop.md','launchpad/docs/corpus/architecture/containers/web.md','launchpad/docs/corpus/templates/reference.md']) -> id: corpus-development-build, id: architecture-containers-desktop, id: architecture-containers-web, id: corpus-template-reference"
  - statement: "Issue #870 requires this node to be structured for lookup rather than narrative teaching, to contain only facts supported by current source with generated versus authored values labelled, to define scope and omissions, and to link authoritative source/schema/config."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#870 definition of done"
  - statement: "Sibling tasks #854 (development/dart-style.md) and #868 (development/rust-style.md) own the Dart and Rust style surfaces, so this node's language boundary is TypeScript, TSX and the CSS the TypeScript guards also scan."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#870 batch dispatch brief, naming #854 and #868 as siblings"
relationships:
  - type: references
    target: corpus-development-build
  - type: references
    target: architecture-containers-desktop
  - type: references
    target: architecture-containers-web
  - type: references
    target: corpus-template-reference
---

# TypeScript and React style: reference

What this repository actually enforces on TypeScript, TSX and front-end CSS, and
by which mechanism. Every rule below is labelled **script-enforced**,
**compiler-enforced** or **review-only**, because that distinction — not the rule
text — is what decides whether a violation stops a push, fails CI, or ships
unnoticed. Facts here come from the configuration, scripts and workflow files
themselves; where a repository document asserts an enforcement detail that the
script contradicts, the script wins and the contradiction is recorded.

Four TypeScript surfaces exist: `desktop/`, `web/`, `admin-web/`, and the
loose `.mjs` tooling under `scripts/`, `desktop/scripts/` and `web/scripts/`.
They are **not** covered equally, and the coverage table below is the most
load-bearing thing on this page.

## Coverage by surface

Which gates run against which TypeScript surface. "Pre-commit" and "pre-push" are
lefthook stages; "CI" is `.github/workflows/ci.yml`.

| Surface | Biome (pre-commit) | Biome (pre-push) | `tsc` (pre-push) | Biome (CI) | `tsc` (CI) | px-text | pubkey-truncation | file-size ratchet |
|---|---|---|---|---|---|---|---|---|
| `desktop/src` | yes — `desktop-fix`, auto-fix + restage | yes — `desktop-check` | yes — `desktop-typecheck` | yes — Desktop Core | via `desktop-build` (`tsc && vite build`) | yes | yes | yes, listed roots |
| `web/src` | yes — `web-fix`, auto-fix + restage | **no lane** | **no lane** | yes — Web job | via `web-build` (`tsc && vite build`) | **no guard** | yes | yes, three roots |
| `admin-web/src` | **no lane** | **no lane** | **no lane** | **no job** | **no job** | **no guard** | **no guard** | **not governed** |
| `scripts/**.mjs`, `*/scripts/**.mjs` | not matched by `desktop-fix`/`web-fix` globs | no | n/a (not TypeScript) | no | n/a | no | no | no |

`admin-web` is checked only by `just admin-check`, which runs
`pnpm -C admin-web check` and `pnpm -C admin-web test:e2e`. That recipe is not a
dependency of `just check` or `just ci`, and no file under `.github/workflows/`
mentions `admin-web` at all.

## Formatting and lint rules (script-enforced)

All of these come from the single root `biome.json`. `desktop/biome.json` and
`web/biome.json` contain only `{"extends": ["../biome.json"]}` — there is no
second rule set to reconcile.

| Setting | Value | Effect |
|---|---|---|
| `formatter.enabled` | `true` | Biome formats JS/TS/JSON/CSS |
| `formatter.indentStyle` | `"space"` | spaces, not tabs |
| `javascript.formatter.quoteStyle` | `"double"` | double quotes in JS/TS |
| `linter.enabled` | `true` | lint runs as part of `biome check` |
| `linter.rules.recommended` | `true` | Biome's recommended rule set, unmodified |
| `linter.rules.suspicious.noUnknownAtRules` | `"off"` | the **only** rule override; Tailwind at-rules would otherwise trip it |
| `assist.enabled` | `false` | Biome assist actions (import sorting and friends) do not run |
| `files.ignoreUnknown` | `false` | unknown file types are an error, not silently skipped |
| `vcs.useIgnoreFile` | `true` | `.gitignore` is honoured |
| `css.parser.tailwindDirectives` | `true` | Tailwind directives parse in `.css` |

**Version.** Declared once at the workspace root as `"@biomejs/biome": "^2.4.6"`;
`biome.json` pins its `$schema` to the `2.4.14` schema; `pnpm-lock.yaml` resolves
`@biomejs/biome@2.4.16`. The three values are authored independently and are
expected to differ.

**No ESLint, no Prettier.** No `.eslintrc*` or `eslint.config*` exists outside
`node_modules`. Biome is the whole formatter-and-linter surface.

## TypeScript compiler contract (compiler-enforced)

| Option | `desktop` | `web` | `admin-web` |
|---|---|---|---|
| `strict` | `true` | `true` | `true` |
| `noUnusedLocals` | `true` | `true` | **unset** |
| `noUnusedParameters` | `true` | `true` | **unset** |
| `noFallthroughCasesInSwitch` | `true` | `true` | **unset** |
| `forceConsistentCasingInFileNames` | unset | unset | `true` |
| `target` | `ES2020` | `ES2020` | `ES2022` |
| `module` | `ESNext` | `ESNext` | `ESNext` |
| `moduleResolution` | `bundler` | `bundler` | `Bundler` |
| `isolatedModules` | `true` | `true` | `true` |
| `noEmit` | `true` | `true` | `true` |
| `jsx` | `react-jsx` | `react-jsx` | `react-jsx` |
| `allowImportingTsExtensions` | `true` | `true` | unset |
| `skipLibCheck` | `true` | `true` | `true` |
| `include` | `["src"]` | `["src"]` | `["src", "vite.config.ts", "playwright.config.ts"]` |

`admin-web` compiles under a weaker contract than the other two: unused locals,
unused parameters and switch fallthrough are all permitted there.

`desktop` additionally declares path aliases `@/*` → `./src/*`,
`@features-manifest` → `../preview-features.json` and
`@model-capabilities-manifest` → `../scripts/model-capabilities.json`; `web`
declares only `@/*`.

## Repository-specific guards (script-enforced)

Three custom Node scripts enforce rules Biome and `tsc` cannot express. Each has
a shared core under `scripts/` and a per-project entry point that supplies roots
and allowlists.

### rem-not-px text scale

**Why the rule exists.** `desktop/src/app/useWebviewZoomShortcuts.ts` implements
Cmd +/- zoom by assigning `document.documentElement.style.fontSize` and pinning
the native webview zoom with `webview.setZoom(DEFAULT_ZOOM_FACTOR)`. Only text
sized in `rem` follows that root font-size; a hardcoded `px` size is frozen
against zoom.

**What the guard flags** (`scripts/check-px-text-core.mjs`):

| Pattern | Regex | Notes |
|---|---|---|
| Tailwind arbitrary text size | `/\btext-\[\d+(?:\.\d+)?(?:px\|rem\|em)\]/g` | matches `px`, `rem` **and** `em`; color literals like `text-[#fff]` do not match |
| CSS pixel font size | `/(?<!-)\bfont-size:\s*\d+(?:\.\d+)?px/g` | the negative lookbehind deliberately spares custom properties named `--font-size` |

Arbitrary `rem` literals are rejected as well as `px` ones — not because they
break zoom, but because they re-fragment the consolidated scale.

**Origin.** One upstream commit — `c22c54e7a`, "fix(desktop): restore timeline
zoom via rem tokens + chat-as-base type scale (#1052)" — added the guard, its
shared core, the `tailwind.config.js` rem tokens and the `AGENTS.md` "Text
sizing & zoom" section together. The guard's comment attributes the regression
it prevents to an earlier PR, #891.

**Scope.** `desktop/scripts/check-px-text.mjs` scans `desktop/src` recursively
for `.ts`, `.tsx` and `.css`. It is the **only** importer of the shared core in
the repository: `web/` and `admin-web/` have no px-text guard.

**Allowlist shape — a documented claim that is wrong.** The override key is
`` `${relativePath}:${match}` `` — a path paired with the *matched literal*.
`AGENTS.md` states these are "allowlisted by `path:line`". That is false. The
script's own comment explains the choice: matching the literal "keeps these
exceptions stable when unrelated edits move lines." The four current entries are
`text-[6rem]` and `text-[4rem]` decorative avatar and preview glyphs.

Note that the *pubkey-truncation* guard does use `path:line` keys — the two
guards genuinely differ, which is the likely source of the confusion.

**The tokens to use instead** (`desktop/tailwind.config.js`, all derived from
`--buzz-type-rem` in `desktop/src/shared/styles/globals/typography.css`, which is
itself `calc(1rem * var(--buzz-type-scale))`):

| Token | Definition |
|---|---|
| `text-2xs` | `calc(var(--buzz-type-rem) * 0.6875)` |
| `text-3xs` | `calc(var(--buzz-type-rem) * 0.5)` |
| `text-badge` | `calc(var(--buzz-type-rem) * 0.625)` |
| `text-message` | `var(--conversation-message-font-size)` + matching line height |
| `text-message-timestamp` | `var(--conversation-timestamp-font-size)` + matching line height |
| `text-title` | `calc(var(--buzz-type-rem) * 2.5)` |
| `text-nsec-key` | `calc(var(--buzz-type-rem) * 2.25)` |

`--conversation-message-font-size` resolves to `calc(var(--buzz-type-rem) *
0.875)`. The stock Tailwind scale (`text-xs` … `text-5xl`) is likewise redefined
against `--buzz-type-rem` in `typography.css`.

### Pubkey truncation

Truncated pubkey prefixes are forgeable by vanity grinding, so ad-hoc
`pubkey.slice(0, N)` is rejected in favour of the canonical `truncatePubkey` /
`<PubKey>`. Scans `src` for `.ts`/`.tsx`. Allowlist keys are `path:line`; a
separate `allowedFiles` set exempts `src/shared/lib/pubkey.ts` (the helper) and
`src/testing/e2eBridge.ts`. Wired into both `desktop`'s and `web`'s `check`
script.

### File-size ratchet

**It is a ratchet, not a flat ceiling.** `allowedLineCount(baseLines, maxLines)`
returns `maxLines` when the base revision's count is `null` or already within
`maxLines`, and otherwise returns `baseLines`. So a file already above 1000 lines
is permitted to stay at its current size but may not grow by a single line.

`resolveBaseRef` picks the comparison point: `CHECK_FILE_SIZES_BASE` if set, else
`HEAD^1` when `GITHUB_ACTIONS === "true"`, else the merge base of `origin/main`
and `HEAD`.

Governed TypeScript roots, `MAX_LINES = 1000` in both:

| Project | Roots (`.ts`, `.tsx` unless noted) |
|---|---|
| `desktop` | `src/app`, `src/features`, `src/shared/api`, `src/shared/context`, `src/shared/lib`, `src/shared/ui`, plus `src/shared/styles` (`.css`) and the Rust roots `src-tauri/src`, `src-tauri/crates` |
| `web` | `src/app`, `src/features`, `src/shared/api` |

TypeScript outside those roots — `desktop/src/shared/hooks`, `desktop/src/main.tsx`,
all of `web/src/shared` except `api`, all of `admin-web` — is **ungoverned** by
the ratchet.

## Review-only rules

These appear in `AGENTS.md` as prose. No script, workflow or config enforces
them; a violation reaches `launchpad` unless a human catches it.

| Rule | Where stated | Enforcement |
|---|---|---|
| `React.memo` is all-or-nothing — one unstable prop defeats it; depend on `mutation.mutateAsync`, not the mutation object; wrap derived `Map`/array state in a content-equality ref cache | `AGENTS.md` "Common Gotchas" | review only — no script references `React.memo` or `useStableReference` |
| Measure interaction lag with DevTools closed and no per-keystroke `console.log` | `AGENTS.md` "Common Gotchas" | review only |
| Prefer stock rem tokens; add a named rem token rather than an arbitrary literal | `AGENTS.md` "Text sizing & zoom" | **partly** script-enforced — the guard rejects arbitrary literals but cannot require the *right* named token |
| Community-scoped module singletons must be reset in `resetCommunityState()` | `AGENTS.md` "Community Switching" | review only |

`desktop/src/shared/hooks/useStableReference.ts` exists as the helper the memo
guidance points at. It is a utility, not a gate.

**`CONTRIBUTING.md` says nothing about TypeScript.** Its "Code Style" section
covers `rustfmt`, `clippy`, unsafe code, `thiserror`/`anyhow` and `tracing` only.
There is no front-end style section in it at all.

## Commands

| Command | What it runs | Where it runs automatically |
|---|---|---|
| `just desktop-check` | `pnpm check` in `desktop/` = `biome check .` + px-text + pubkey-truncation | pre-push lane, CI Desktop Core, `just check` |
| `just desktop-typecheck` | `pnpm typecheck` = `tsc --noEmit` | pre-push lane only — **not** in `just check` or `just ci` |
| `just desktop-fix` | `pnpm exec biome check --write .` | pre-commit lane (`stage_fixed`) |
| `just desktop-build` | `pnpm build` = `tsc && vite build` | CI Desktop Core, `just ci` |
| `just web-check` | `pnpm check` in `web/` = `biome check .` + pubkey-truncation | CI Web job, `just check` — **no pre-push lane** |
| `just web-typecheck` | `pnpm typecheck` = `tsc --noEmit` | **nothing invokes it** |
| `just web-fix` | `pnpm exec biome check --write .` | pre-commit lane (`stage_fixed`) |
| `just web-build` | `pnpm build` = `tsc && vite build` | CI Web job, `just ci` |
| `just file-size-check` | the ratchet's own tests plus the desktop, web and mobile entry points | unfiltered pre-push lane, CI step, `just check` |
| `just admin-check` | `pnpm -C admin-web check` + `test:e2e`, plus Rust checks | **nothing** — not in `check` or `ci`, no CI job |
| `just fix-all` | `fmt`, `desktop-tauri-fmt`, `desktop-fix`, `web-fix`, `mobile-fix` | manual |
| `just check` | `fmt-check clippy desktop-check desktop-tauri-fmt-check desktop-tauri-clippy web-check mobile-check security-review-check file-size-check` | manual; the local aggregate gate |
| `just ci` | `check test-unit desktop-test desktop-build desktop-tauri-check desktop-tauri-test web-build mobile-test` | manual; the pre-PR gate |

`pnpm check:file-sizes` is declared in both `desktop/package.json` and
`web/package.json` but is invoked by nothing — `just file-size-check` runs the
`.mjs` files directly.

## Pre-push lane scoping

Each globbed pre-push lane sets `files: git diff --name-only origin/main...HEAD`,
so a lane fires only when the branch's merge-base diff touches a path matching
its glob — the same semantics as CI's `dorny/paths-filter`. The `file-size-check`
lane is deliberately unfiltered because the ratchet computes its own merge-base
diff. Lefthook 2.1.x drops deleted paths from push-file discovery, so a
deletion-only change triggers no local lane; CI's paths-filter catches it.

## Boundary

This node does not describe:

- **Rust style** — `#868` owns `development/rust-style.md`; `CONTRIBUTING.md`'s
  Code Style section is the current source for `rustfmt`/`clippy`.
- **Dart and Flutter style** — `#854` owns `development/dart-style.md`. The
  `mobile-check`, `mobile-fmt` and mobile file-size roots are that node's.
- **Why any of these rules exist, argued at length.** Mechanism is described
  where it makes a rule legible (the zoom mechanism, the ratchet's arithmetic);
  motivation beyond that belongs to a concept-shaped node.
- **How to set up or run the toolchain.** `development-hermit` and
  `corpus-development-build` cover activation and building.
- **Accessibility conventions, Playwright spec conventions, screenshot
  workflows, and the desktop E2E mock bridge.** All are documented in `AGENTS.md`
  and none is a TypeScript style rule.
- **Testing conventions and the test commands themselves**, beyond noting where
  a test run sits inside a check script.

## Relationships

Declared: `references` toward `corpus-development-build` (the build commands this
node's gate table depends on), `architecture-containers-desktop` and
`architecture-containers-web` (the two surfaces these rules govern), and
`corpus-template-reference` (the template this node's shape follows). All four
ids were confirmed against `origin/launchpad` with `git show`, not against this
worktree.

Not declared: no edge to `development-hermit`, `development-prerequisites` or
`debugging` — they are named in prose above where relevant but this node neither
depends on nor supersedes them. At the recorded revision, no edge was declared to
`development-dart-style` or `development-rust-style` either, since neither existed
on `origin/launchpad` yet. Both have since landed in this same integration, so the
natural edges now resolve; they are not added here, since wiring them in under the
pressure of a pre-merge fix pass risks the same kind of error this fix pass exists
to catch. Adding them belongs to a dedicated pass across the whole
`development`/`governance`/`releases` shelf once all 37 nodes are stable.

## Scope and omissions

**This node covers** the Biome configuration applied to TypeScript and TSX, the
per-project `tsconfig.json` compiler contracts, the three repository-specific
Node guards (px-text, pubkey-truncation, file-size ratchet) with their exact
match rules and allowlist shapes, which command runs each gate, which lefthook
stage and CI job invokes it, and which style rules are prose-only.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Rust style and its `rustfmt`/`clippy` gates | `#868`, and `CONTRIBUTING.md` §Code Style today |
| Dart/Flutter style and the mobile lanes | `#854` |
| Whether `admin-web`'s absence from CI is intended or a coverage gap | not owned by any node found at this revision; recorded here as a fact, not adjudicated |
| Whether the weaker `admin-web` compiler contract is deliberate | same |
| The corpus front-matter contract | `launchpad/docs/corpus/schema/node.schema.json` |

**Generated versus authored.** Every value in every table above is **authored** —
read from a committed configuration, script or workflow file. Nothing here is
machine-generated, and nothing is derived by running a tool. Two values are
authored in three independent places and are expected to disagree: the Biome
version range (`package.json`), the Biome schema pin (`biome.json`) and the
resolved Biome version (`pnpm-lock.yaml`).

**Expected but not verified when this node was written:**

- **Biome was never executed.** Every rule statement is read from `biome.json`,
  not observed as a failing or passing run. In particular, what
  `linter.rules.recommended: true` expands to at `@biomejs/biome@2.4.16`, and
  what `assist.enabled: false` disables in practice, were not confirmed by
  running the tool — the second is recorded as an INFERENCE.
- **Biome's configuration resolution for `admin-web` was not observed.**
  `admin-web` has no `biome.json`; that its `biome check .` picks up the root
  config by upward discovery is an INFERENCE from the layout, at confidence 0.6.
  If it does not, `admin-web` runs under Biome defaults rather than this
  repository's rules, and the coverage table's `admin-web` row understates the
  divergence.
- **No CI run was inspected.** The coverage table is derived from
  `.github/workflows/ci.yml`'s job definitions and the `Justfile` recipes they
  call, not from an observed workflow run. Required-check configuration on the
  `launchpad` branch was not examined, so a job listed here as running is not
  thereby established as *blocking*.
- **`resolveBaseRef` names `origin/main`,** which is upstream's default branch,
  not this fork's `launchpad`. Whether that mismatch changes the ratchet's
  behaviour for a fork branch was not tested here.
- **The `.mjs` tooling under `scripts/` was not checked for style coverage
  beyond confirming the lefthook globs do not match it.** Whether root-level
  `scripts/*.mjs` is formatted by any invocation of Biome was not established.
