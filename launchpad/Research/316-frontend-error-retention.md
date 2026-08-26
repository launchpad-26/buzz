# Whether the desktop frontend retains an error after it is dismissed

**Title:** Frontend error retention in the Buzz desktop client
**Summary:** Walks the four error paths in `desktop/src`. Nothing retains error text: no `window.onerror` or `unhandledrejection` handler exists anywhere, nothing writes error text to storage or a file, and error toasts auto-dismiss after 4 seconds on the pinned sonner's default. The root error boundary is worse than not retaining — it never displays the error text at all. One finding cuts the other way: the toast text is selectable while shown, so "cannot be copied" is a timer problem, not a CSS one.
**Tags:** `observability` `desktop` `react` `error-handling` `sonner` `retention`
**Reviewed:** 2026-08-22 · **Source:** `launchpad-26/buzz` at `678008ea4` · **Answers:** [#316](https://github.com/launchpad-26/buzz/issues/316)

---

## Finding

**No. Nothing retains it.** And the root error boundary does not even show the error text in the first place, so for the most serious failure mode there is nothing to copy even while it is on screen.

| Path | Where | Does the text outlive the render? |
|---|---|---|
| React render errors | `desktop/src/app/RootErrorBoundary.tsx` | **No — and it is never shown.** Held in state, `console.error`'d, destroyed by the Reload button |
| Error toasts (115 call sites) | `sonner` via `desktop/src/shared/ui/sonner.tsx` | **No.** In the DOM for 4 s, then gone |
| Unhandled promise rejections | **nowhere** | **No handler exists** |
| Uncaught non-React errors | **nowhere** | **No handler exists** |

One result cuts the other way and should be kept: **the toast text is selectable while shown.** So [#289](https://github.com/launchpad-26/buzz/issues/289)'s "cannot be copied" is a consequence of the four-second timer and of the boundary rendering no text — not of a `user-select` rule. That narrows the work.

---

## Part 1 — The root boundary never shows the error

Full `render()` and `componentDidCatch` from `desktop/src/app/RootErrorBoundary.tsx`:

```tsx
  override componentDidCatch(error: unknown, info: React.ErrorInfo): void {
    console.error("[RootErrorBoundary] uncaught render error:", error, info);
  }

  override render(): ReactNode {
    const { error } = this.state;
    if (error) {
      return (
        <div className="flex h-screen w-screen flex-col items-center justify-center gap-3 bg-background px-6 text-foreground">
          <p className="text-base font-semibold">Buzz failed to start</p>
          <p className="max-w-md text-center text-sm text-muted-foreground">
            Reload Buzz to try again. If this keeps happening, check that Buzz
            can access website data, then contact support.
          </p>
          <button
            type="button"
            className="rounded-md border border-border bg-secondary px-4 py-2 text-sm hover:bg-secondary/80"
            onClick={() => window.location.reload()}
          >
            Reload
          </button>
        </div>
      );
    }
    return this.props.children;
  }
```

`error` is destructured, used only as a boolean, and never rendered. The user sees two static sentences and a Reload button. The only place the text goes is `console.error` — and [#315](https://github.com/launchpad-26/buzz/issues/315) establishes that console output in a packaged build is not retrievable after the fact. The Reload button then destroys the state holding it.

For a render error, criterion 2's "readable, copyable" therefore fails at *readable*.

## Part 2 — No global handlers

```
$ grep -rn "unhandledrejection\|window.onerror\|addEventListener(\"error\"\|addEventListener('error'" desktop/src
desktop/src/features/messages/lib/timelineImagePreload.ts:53:      image.addEventListener("error", release, { once: true });
desktop/src/features/messages/lib/useMediaUpload.ts:86:    element.addEventListener("error", onError, { once: true });
desktop/src/testing/e2eBridge.ts:9721:  ws.addEventListener("error", () => {
desktop/src/testing/e2eBridge.ts:9729:    ws.addEventListener("error", () => resolve(wsId), { once: true });
```

Four hits, all element-scoped: two `<img>`/media handlers and two inside the E2E mock bridge. **No window-level handler of any kind.** An async rejection or a non-React throw is not captured by the application at all. `desktop/src/main.tsx`, read end to end, installs `RootErrorBoundary` and `<Toaster />` and registers no error listener.

## Part 3 — Nothing writes error text to storage

```
$ grep -rn "setItem" desktop/src --include='*.ts' --include='*.tsx' | grep -i "error\|crash\|log"
desktop/src/features/onboarding/ui/IdentityKeyHelpDialog.tsx:30:    window.localStorage.setItem(IDENTITY_KEY_HELP_SEEN_STORAGE_KEY, "true");
```

One hit, and it is a "help dialog seen" flag that matched on `log` inside `Dialog`. There is no error store, no crash log, no ring buffer.

## Part 4 — The toast's lifetime and copyability

From the pinned dependency rather than from documentation:

```
$ grep '"sonner"' desktop/package.json
    "sonner": "^2.0.7",
$ grep '"version"' node_modules/sonner/package.json
  "version": "2.0.7",
$ grep -o "TOAST_LIFETIME *= *[0-9]*" node_modules/sonner/dist/index.mjs
TOAST_LIFETIME = 4000
$ grep -o "user-select: *[a-z]*" node_modules/sonner/dist/styles.css | sort | uniq -c
   1 user-select: none
```

The single `user-select: none` is scoped to a swipe gesture, not the resting toast:

```css
[data-sonner-toast][data-swiped='true'] {
  user-select: none;
```

Buzz's wrapper (`desktop/src/shared/ui/sonner.tsx`, read in full) sets `theme`, `className` and four `classNames` entries — **no `duration`**, so `TOAST_LIFETIME` applies, and **no `select-none`**, so the text stays selectable. The global stylesheet adds no rule either:

```
$ grep -rn "user-select\|select-none" desktop/src/shared/styles/globals.css
(no output)
```

Scale of the surface this governs:

```
$ grep -rn "toast.error(" desktop/src --include='*.ts' --include='*.tsx' | wc -l
     115
```

## Part 5 — Runtime probe: two real errors in the loaded app

The E2E bundle was built (`vite build --mode e2e`, 4780 modules transformed, exit 0), `dist/` served locally, and driven with Playwright. Two genuine errors were raised in the page:

```js
Promise.reject(new Error(MARK_REJ));
setTimeout(() => { throw new Error(MARK_ERR); }, 10);
```

```
=== A. localStorage keys after boot + errors ===
(none)
=== A. sessionStorage keys ===
(none)
=== A. anywhere the error text was retained ===
NOTHING RETAINED — no storage entry and not in the DOM
=== A. what the page surface saw (count 3) ===
[pageerror] BUZZ316-UNHANDLED-REJECTION-c4f1
[pageerror] BUZZ316-UNCAUGHT-ERROR-c4f1
```

Both reached the page surface as `pageerror`, confirming they were genuinely unhandled, and neither string appeared in `localStorage`, `sessionStorage` or the DOM afterwards.

A second run seeded the community and onboarding keys that `main.tsx` seeds in its DEV path, and they persisted:

```
=== localStorage keys after a real boot ===
buzz-onboarding-complete.v1:deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef
buzz-communities
buzz-active-community-id
```

That rules out the trivial explanation that nothing was retained because storage was unavailable.

---

## What this means for #289

1. **Criterion 2 is three changes on the desktop, not one:** a retained record (none exists), a global capture point for async errors (no handler exists), and a UI that shows the error text at all (the boundary shows none). A child scoped as "export frontend errors" would miss the third — which is the one the witnessed fault actually describes.
2. **The four-second toast is "cannot be read in time", quantified.** 4000 ms, from a library default nobody chose. Worth stating as a number in the PRD.
3. **"Cannot be copied" is not a CSS problem.** The text is selectable. The obstacles are the timer and the boundary's silence.
4. **A global handler is the cheapest single step.** One `window.addEventListener('unhandledrejection' | 'error')` writing to a bounded local buffer captures the entire fourth row of the table, which today is captured by nothing.
5. **With [#315](https://github.com/launchpad-26/buzz/issues/315), the webview console is a dead end on both sides.** `console.error` in the boundary is the only record of a render error, and console output is unretrievable in a packaged build. The app's single diagnostic for its most serious failure reaches nobody.

---

## Confidence, and what was not checked

**High confidence** on the five code findings: each is a quoted command with its full output, or a file read end to end.

**The runtime step is partially complete, and the limitation is specific.** Two real errors were raised in the real built bundle and nothing retained them — but **the app's UI never rendered** in this harness. The desktop app needs the E2E mock Tauri bridge to render, and the ad-hoc script set `window.__BUZZ_E2E__` without the rest of what the repo's own `installMockBridge` (`desktop/tests/helpers/bridge.ts`) installs. So "no handler retains an unhandled error in the loaded application" is demonstrated; "a toast appeared, was dismissed, and left nothing behind in a rendered app" is not.

**What would complete it:** a spec in `desktop/tests/e2e/` using `installMockBridge(page)`, registered in `playwright.config.ts`'s `smoke` `testMatch`, that triggers a real `toast.error`, asserts the text is visible and selectable, waits past 4 s, then asserts absence from the DOM and both storages. Roughly 20 lines against the existing harness; it needs a change to a tracked config file, which is why it is not part of this document.

**Also not checked:** the `RootErrorBoundary` was not exercised in a rendered app — an attempt that made `window.localStorage` throw pre-boot produced a blank page and no boundary log, but that simulation is more aggressive than WebKit's real deny-storage behaviour, so it is not reported as a finding. IndexedDB was not inspected beyond confirming the API exists. Whether the Tauri side persists anything on the frontend's behalf was not examined. Which of the 115 `toast.error` sites pass an `Error.message` through versus a static string was not enumerated, and that affects how useful a retained record would be. The web client and mobile are out of scope.
