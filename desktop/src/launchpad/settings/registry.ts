import type { LucideIcon } from "lucide-react";
import { knowledgeSettingsSection } from "./knowledge/KnowledgeSettingsPanel";

/**
 * Cohort Settings registry for the seam in `SettingsPanels.tsx` (ADR-0051 as
 * amended by ADR-0053). A section is added here, under `launchpad/`-owned
 * code, never by editing upstream registration sites or `SettingsView.tsx`.
 *
 * Adding a new cohort section: widen this union, add its descriptor's import
 * and a matching key to `cohortSettingsSectionRegistry` below. Both edits
 * stay in this file. `navGroup` is how the seam synthesizes sidebar groups.
 */
export type CohortSettingsSectionId = "knowledge";

export type CohortSettingsSectionDescriptor = {
  value: CohortSettingsSectionId;
  label: string;
  icon: LucideIcon;
  render: () => React.ReactNode;
  /**
   * Sidebar nav group synthesized in `SettingsPanels.tsx` (`settingsNavGroups`).
   * A second registrant with the same label joins this group; a new label
   * becomes its own group. Do not hardcode the group name in `SettingsView.tsx`.
   */
  navGroup: string;
};

/**
 * Keyed by `CohortSettingsSectionId` so widening that union without adding a
 * matching entry here is a compile error, not a panel that silently renders
 * `null` at runtime (review-code finding on #551: the seam had no equivalent
 * of `renderSettingsSection`'s upstream exhaustiveness check).
 */
const cohortSettingsSectionRegistry: Record<
  CohortSettingsSectionId,
  CohortSettingsSectionDescriptor
> = {
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
