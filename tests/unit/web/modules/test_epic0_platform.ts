/**
 * Tests para EPIC 0: Platform Foundation
 */

import { describe, it, expect } from 'vitest';
import { featureFlags, isFeatureEnabled, getEnabledModules } from '@/modules/shared/lib/feature-flags';
import { moduleRegistry, MODULE_REGISTRY } from '@/modules/shared/lib/module-registry';

describe('Feature Flags', () => {
  it('should have all required flags', () => {
    expect(featureFlags.AI_CENTER).toBeDefined();
    expect(featureFlags.ANALYTICS).toBeDefined();
    expect(featureFlags.KNOWLEDGE_BASE).toBeDefined();
    expect(featureFlags.REPORTS).toBeDefined();
    expect(featureFlags.NOTIFICATIONS).toBeDefined();
    expect(featureFlags.OPERATIONS).toBeDefined();
    expect(featureFlags.ADMINISTRATION).toBeDefined();
    expect(featureFlags.CONNECTORS).toBeDefined();
    expect(featureFlags.WORKSPACE).toBeDefined();
  });

  it('should check if feature is enabled', () => {
    expect(isFeatureEnabled('AI_CENTER')).toBe(true);
    expect(isFeatureEnabled('CONNECTORS')).toBe(false);
  });

  it('should get enabled modules count', () => {
    const enabled = getEnabledModules();
    expect(enabled.length).toBeGreaterThan(0);
    expect(enabled).toContain('AI_CENTER');
    expect(enabled).not.toContain('CONNECTORS');
  });
});

describe('Module Registry', () => {
  it('should have all modules registered', () => {
    expect(MODULE_REGISTRY.length).toBeGreaterThan(0);
  });

  it('should get all enabled modules', () => {
    const enabledModules = moduleRegistry.getEnabledModules();
    expect(enabledModules.length).toBeGreaterThan(0);
  });

  it('should get module by id', () => {
    const dashboard = moduleRegistry.getModule('dashboard');
    expect(dashboard).toBeDefined();
    expect(dashboard?.name).toBe('Dashboard');
  });

  it('should check if module is enabled', () => {
    expect(moduleRegistry.isModuleEnabled('dashboard')).toBe(true);
    expect(moduleRegistry.isModuleEnabled('connectors')).toBe(false);
  });

  it('should have correct module paths', () => {
    const dashboard = moduleRegistry.getModule('dashboard');
    expect(dashboard?.path).toBe('/dashboard');
    
    const ai = moduleRegistry.getModule('ai');
    expect(ai?.path).toBe('/ai');
  });

  it('should have correct module order', () => {
    const modules = moduleRegistry.getEnabledModules();
    const orders = modules.map(m => m.order);
    const sortedOrders = [...orders].sort((a, b) => a - b);
    expect(orders).toEqual(sortedOrders);
  });
});
