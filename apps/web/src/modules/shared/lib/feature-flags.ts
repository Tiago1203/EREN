/**
 * Feature Flags para PHASE 6
 * Controla qué módulos están habilitados
 */

export interface FeatureFlags {
  AI_CENTER: boolean;
  ANALYTICS: boolean;
  KNOWLEDGE_BASE: boolean;
  REPORTS: boolean;
  NOTIFICATIONS: boolean;
  OPERATIONS: boolean;
  ADMINISTRATION: boolean;
  CONNECTORS: boolean;
  WORKSPACE: boolean;
}

export const featureFlags: FeatureFlags = {
  AI_CENTER: true,
  ANALYTICS: true,
  KNOWLEDGE_BASE: true,
  REPORTS: true,
  NOTIFICATIONS: true,
  OPERATIONS: true,
  ADMINISTRATION: true,
  CONNECTORS: false, // Preparado pero no habilitado
  WORKSPACE: true,
};

export function isFeatureEnabled(flag: keyof FeatureFlags): boolean {
  return featureFlags[flag];
}

export function getEnabledModules(): string[] {
  return Object.entries(featureFlags)
    .filter(([, enabled]) => enabled)
    .map(([name]) => name);
}
