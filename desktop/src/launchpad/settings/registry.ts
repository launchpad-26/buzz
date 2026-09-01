import type { LucideIcon } from "lucide-react";
import { knowledgeSettingsSection } from "./knowledge/KnowledgeSettingsPanel";

/**
 * The registration seam ADR-0051 grants (accepted; see
 * `launchpad/decisions/ADR-0051-cohort-settings-registration-seam.md`), amended
 * by ADR-0053 to also own sidebar nav-group membership (see
 * `launchpad/decisions/ADR-0053-settings-seam-owns-nav-groups.md`): a
 * cohort Settings section is added here, under `launchpad/`-owned code, never
 * by editing `SettingsPanels.tsx`'s four upstream registration sites directly.
 *
 * Adding a new cohort section: widen this union, add its descriptor's import
 * and a matching key to `cohortSettingsSectionRegistry` below. Both edits
 * stay in this file.
 */
export type CohortSettingsSectionId = "knowledge";

export type CohortSettingsSectionDescriptor = {
  value: CohortSettingsSectionId;
  label: string;
  icon: LucideIcon;
  render: () => React.ReactNode;
  /**
   * Sidebar nav group this section is synthesized into (review-final finding
   * on #551: this used to be hardcoded to one panel's own label in
   * `SettingsView.tsx`, so a second registrant would have landed under a
   * group named after the first panel).
   */
  navGroup: string;
};

/**
 * Keyed by `CohortSettingsSectionId` so widening that union without adding a
 * matching entry here is a compile error, not a panel that silently renders
 * `null` at runtime (review-code finding on #551: the seam had no equivalent
 * of `renderSettingsSection`'s upstream exhaustiveness check).
 *
 * The mapped-type value narrows each entry's `value` to its own key
 * (review panel finding on #1935: a key/descriptor mismatch is now a compile
 * error, not just the runtime check below — the compiler is the first line,
 * the throw is a defensible second one if that guarantee is ever bypassed,
 * e.g. via an unsafe cast).
 */
const cohortSettingsSectionRegistry: {
  [K in CohortSettingsSectionId]: CohortSettingsSectionDescriptor & {
    value: K;
  };
} = {
  knowledge: knowledgeSettingsSection,
};

for (const [key, descriptor] of Object.entries(cohortSettingsSectionRegistry)) {
  if (descriptor.value !== key) {
    throw new Error(
      `Cohort Settings section registered under key "${key}" but its descriptor's value is "${descriptor.value}" — they must match.`,
    );
  }
}

export const cohortSettingsSections: CohortSettingsSectionDescriptor[] =
  Object.values(cohortSettingsSectionRegistry);
