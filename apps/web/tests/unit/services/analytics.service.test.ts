import { describe, it, expect } from 'vitest';
import { analyticsService } from '@/modules/analytics/services/analytics.service';
import type { DateRange } from '@/modules/analytics/types/analytics.types';

describe('AnalyticsService', () => {
  const mockDateRange: DateRange = {
    start: new Date('2024-01-01'),
    end: new Date('2024-01-31'),
  };

  describe('getDashboardMetrics', () => {
    it('returns metrics array', async () => {
      const result = await analyticsService.getDashboardMetrics(mockDateRange);
      expect(Array.isArray(result)).toBe(true);
    });
  });

  describe('getChartData', () => {
    it('returns chart data for valid chart id', async () => {
      const result = await analyticsService.getChartData('test-chart', mockDateRange);
      expect(result).toBeDefined();
    });
  });

  describe('getKPIs', () => {
    it('returns kpis array', async () => {
      const result = await analyticsService.getKPIs(mockDateRange);
      expect(Array.isArray(result)).toBe(true);
    });
  });

  describe('getTrends', () => {
    it('returns trends array', async () => {
      const result = await analyticsService.getTrends(mockDateRange);
      expect(Array.isArray(result)).toBe(true);
    });
  });
});
