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
