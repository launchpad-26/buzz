import type { LucideIcon } from "lucide-react";
import { knowledgeSettingsSection } from "./knowledge/KnowledgeSettingsPanel";

/**
 * The registration seam #1502 grants (decision pending merge in PR #1503,
 * "ADR-0051 — cohort Settings sections register via a seam"): a cohort
 * Settings section is added here, under `launchpad/`-owned code, never by
 * editing `SettingsPanels.tsx`'s four upstream registration sites directly.
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
