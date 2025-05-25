import { Injectable } from '@angular/core';

export interface DemoDataPoint {
  timestamp: number;
  value: number;
  label: string;
}

@Injectable({
  providedIn: 'root'
})
export class DemoDataService {
  constructor() {
    try {
      console.log('DemoDataService initialized');
    } catch (error) {
      console.error('Error initializing DemoDataService:', error);
    }
  }

  /**
   * Generate demo time series data with proper error handling
   * @param count Number of data points to generate
   * @param minValue Minimum value
   * @param maxValue Maximum value
   * @param startTime Optional start timestamp
   * @param intervalMs Optional interval between points in milliseconds
   * @returns Array of data points or empty array on error
   */
  generateTimeSeriesData(
    count: number | undefined | null, 
    minValue: number | undefined | null = 0, 
    maxValue: number | undefined | null = 100, 
    startTime?: number,
    intervalMs: number | undefined | null = 3600000 // 1 hour default
  ): DemoDataPoint[] {
    try {
      // Validate inputs
      const safeCount = count && count > 0 ? Math.min(count, 1000) : 10; // Default to 10, max 1000
      const safeMinValue = minValue !== undefined && minValue !== null ? minValue : 0;
      const safeMaxValue = maxValue !== undefined && maxValue !== null ? maxValue : 100;
      const safeStartTime = startTime || Date.now() - (safeCount * (intervalMs || 3600000));
      const safeIntervalMs = intervalMs && intervalMs > 0 ? intervalMs : 3600000;
      
      // Ensure min is less than max
      if (safeMinValue >= safeMaxValue) {
        throw new Error('minValue must be less than maxValue');
      }
      
      const result: DemoDataPoint[] = [];
      const valueRange = safeMaxValue - safeMinValue;
      
      for (let i = 0; i < safeCount; i++) {
        const timestamp = safeStartTime + (i * safeIntervalMs);
        const value = safeMinValue + Math.random() * valueRange;
        const roundedValue = Math.round(value * 100) / 100; // Round to 2 decimal places
        
        result.push({
          timestamp,
          value: roundedValue,
          label: new Date(timestamp).toISOString()
        });
      }
      
      return result;
    } catch (error) {
      console.error('Error generating time series data:', error);
      return []; // Return empty array on error
    }
  }

  /**
   * Generate random distribution data with proper error handling
   * @param count Number of data points
   * @param categories Array of category labels
   * @returns Object mapping categories to values or empty object on error
   */
  generateDistributionData(
    count: number | undefined | null,
    categories: string[] | undefined | null
  ): Record<string, number> {
    try {
      // Validate inputs
      if (!count || count <= 0 || !categories || !Array.isArray(categories) || categories.length === 0) {
        throw new Error('Invalid inputs for generateDistributionData');
      }

      const safeCount = Math.min(count, 10000); // Cap at 10000 to prevent excessive processing
      const safeCategories = categories.filter(c => typeof c === 'string' && c.length > 0);
      
      if (safeCategories.length === 0) {
        throw new Error('No valid categories provided');
      }
      
      // Initialize result with zeros
      const result: Record<string, number> = {};
      safeCategories.forEach(cat => {
        result[cat] = 0;
      });
      
      // Generate random distribution
      for (let i = 0; i < safeCount; i++) {
        const randomIndex = Math.floor(Math.random() * safeCategories.length);
        const category = safeCategories[randomIndex];
        result[category] = (result[category] || 0) + 1;
      }
      
      return result;
    } catch (error) {
      console.error('Error generating distribution data:', error);
      return {}; // Return empty object on error
    }
  }
}