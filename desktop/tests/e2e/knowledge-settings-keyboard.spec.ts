import { expect, test } from "@playwright/test";

import { installMockBridge } from "../helpers/bridge";
import { openSettings } from "../helpers/settings";

/**
 * Keyboard/focus verification for the cohort-registered "Help" (knowledge)
 * Settings section (#551 STEP 7). This is a nav item + static panel, not a
 * custom interactive widget — the done-when is that it is reachable and
 * behaves the same as an existing upstream section (e.g. `updates`), not
 * that it introduces new focus-management behavior no other section has.
 */
test("Help settings entry is Tab-reachable, activates via keyboard, and does not trap focus", async ({
  page,
}) => {
  await installMockBridge(page);
  await page.goto("/");
  await openSettings(page);

  const backToApp = page.getByTestId("settings-back-to-app");
  const knowledgeNav = page.getByTestId("settings-nav-knowledge");
  const updatesNav = page.getByTestId("settings-nav-updates");

  // Baseline: an existing upstream section's own keyboard-activation focus
  // behavior, to compare the new entry against rather than assuming a shape.
  // Neither upstream nor the new panel move focus on selection (confirmed
  // pre-existing, not a regression — see commit 49b757268's review-a11y
  // note) — each nav button simply keeps focus after activating its panel.
  await updatesNav.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByTestId("settings-updates")).toBeVisible();
  await expect(updatesNav).toBeFocused();

  // Real Tab-order reachability: starting from a known sidebar anchor,
  // sequential Tab presses (no mouse) must reach the Help nav button.
  await backToApp.focus();
  let reachedViaTab = false;
  for (let i = 0; i < 60; i++) {
    const testId = await page.evaluate(
      () => document.activeElement?.getAttribute("data-testid") ?? null,
    );
    if (testId === "settings-nav-knowledge") {
      reachedViaTab = true;
      break;
    }
    await page.keyboard.press("Tab");
  }
  expect(reachedViaTab).toBe(true);

  // Activate via keyboard (native <button> semantics: Enter and Space both
  // fire a click) and confirm the panel renders.
  await page.keyboard.press("Enter");
  await expect(page.getByTestId("settings-knowledge")).toBeVisible();
  await expect(
    page.getByTestId("settings-knowledge").getByText("Help", { exact: true }),
  ).toBeVisible();

  // Focus parity with the existing section: activating the new panel keeps
  // focus on its own nav button, matching `updates`'s behavior above — no
  // new regression introduced by this panel.
  await expect(knowledgeNav).toBeFocused();

  // No focus trap: Tab away from the nav button lands on a different
  // element instead of staying pinned or throwing.
  await page.keyboard.press("Tab");
  const afterTabTestId = await page.evaluate(
    () => document.activeElement?.getAttribute("data-testid") ?? null,
  );
  expect(afterTabTestId).not.toBe("settings-nav-knowledge");

  // Shift+Tab returns focus to the nav button without getting stuck either.
  await page.keyboard.press("Shift+Tab");
  await expect(knowledgeNav).toBeFocused();
});

/**
 * Accessibility pass on #552's real corpus rendering (plan STEP 8, deferred
 * past STEP 6/7 and picked up here). The panel content is a static,
 * non-interactive list -- group headings (`<h2>`) and node headings (`<h3>`)
 * inside plain, unfocusable containers (see SettingsOptionGroup/
 * SettingsOptionRow, both bare `<div>`s with no tabindex/role). There is no
 * expand/collapse, no custom menu, and therefore no new ARIA role or
 * focus-management contract to satisfy beyond a plain heading/list structure
 * -- confirmed by reading the components rather than assumed.
 *
 * Because nothing here is a Tab stop, "keyboard-only navigation reaches
 * every rendered node" means: reaching the panel via Tab (already proven
 * above) is sufficient, since the content is then present in the
 * accessibility tree in document order for a screen reader's virtual cursor
 * -- no further keyboard interaction is needed or possible. This test proves
 * the content is actually there (not "coming soon") and that the heading
 * hierarchy has no level skip (h1 "Help" -> h2 group -> h3 node), which is
 * the concrete, checkable half of that claim.
 */
test("Help settings panel renders real corpus content as a static, non-interactive heading structure", async ({
  page,
}) => {
  await installMockBridge(page);
  await page.goto("/");
  await openSettings(page);

  const knowledgeNav = page.getByTestId("settings-nav-knowledge");
  await knowledgeNav.click();

  const panel = page.getByTestId("settings-knowledge");
  await expect(panel).toBeVisible();

  // Real content, not the #551 placeholder.
  await expect(panel.getByText("coming soon")).toHaveCount(0);

  // All three types the current corpus actually contains (verified against
  // the committed corpus.json, not the two the packaging plan's OPEN item 1
  // guessed at) render as h2 group headings, with a presentable label
  // (Title Case), not the raw lowercase `type` field. Asserting each one by
  // name -- not just a >= bound on the total -- means the singleton `agent`
  // group disappearing would fail this test instead of hiding behind a
  // loose count.
  await expect(
    panel.getByRole("heading", { level: 2, name: "Agent", exact: true }),
  ).toBeVisible();
  await expect(
    panel.getByRole("heading", {
      level: 2,
      name: "Architecture",
      exact: true,
    }),
  ).toBeVisible();
  await expect(
    panel.getByRole("heading", { level: 2, name: "Governance", exact: true }),
  ).toBeVisible();

  // Page title is the sole h1; group titles are h2; each node's own title is
  // h3 -- no level is skipped. One h3 per group heading above.
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Help");
  const nodeHeadings = panel.getByRole("heading", { level: 3 });
  expect(await nodeHeadings.count()).toBe(3);

  // Each rendered node carries its id/origin provenance text, unmodified by
  // the packaging boundary -- the DoD's "provenance survives" claim, made
  // concrete in the frontend rendering itself.
  const provenanceRows = page.locator(
    '[data-testid$="-provenance"][data-testid^="settings-knowledge-node-"]',
  );
  expect(await provenanceRows.count()).toBe(3);
  for (const row of await provenanceRows.all()) {
    await expect(row).toHaveText(/^id: \S+ · origin: \S+$/);
  }

  // Nothing in this panel is a Tab stop. A single Tab hop from the nav
  // button only proves the *next* element isn't panel content -- it can't
  // rule out a focusable element added anywhere else in the panel, and it
  // is blind to any testid that doesn't start with the one prefix it
  // checks. Count every focusable element inside the panel directly instead.
  const focusableInPanel = panel.locator(
    'a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"])',
  );
  expect(await focusableInPanel.count()).toBe(0);
});
