import { Injectable } from '@angular/core';

export interface PerformanceMetric {
  name: string;
  value: number;
  type: string;
  timestamp: number;
}

@Injectable({
  providedIn: 'root'
})
export class PerformanceMonitorService {
  private metrics: PerformanceMetric[] = [];
  private observer: PerformanceObserver | null = null;

  constructor() {
    this.initializePerformanceObserver();
  }

  private initializePerformanceObserver(): void {
    if (typeof PerformanceObserver !== 'undefined') {
      this.observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          const metric: PerformanceMetric = {
            name: entry.name || 'unknown',
            value: entry.startTime || 0,
            type: entry.entryType || 'unknown',
            timestamp: Date.now()
          };
          this.metrics.push(metric);
          const entryType = entry.entryType || 'unknown';
          const entryName = entry.name || 'unknown';
          const startTime = entry.startTime || 0;
          console.log(`Performance Metric - ${entryType}: ${entryName} at ${startTime.toFixed(2)}ms`);
        });
      });

      // Observe paint, navigation, and measure events
      this.observer.observe({ entryTypes: ['paint', 'navigation', 'measure', 'mark'] });
    }
  }

  // Mark a custom performance point
  markPerformance(name: string): void {
    if (typeof performance !== 'undefined' && performance.mark) {
      performance.mark(name);
    }
  }

  // Measure time between two marks
  measurePerformance(name: string, startMark: string, endMark: string): void {
    if (typeof performance !== 'undefined' && performance.measure) {
      performance.measure(name, startMark, endMark);
    }
  }

  // Get navigation timing metrics
  getNavigationTiming(): any {
    if (typeof performance !== 'undefined' && performance.timing) {
      const timing = performance.timing;
      return {
        domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
        loadComplete: timing.loadEventEnd - timing.navigationStart,
        domInteractive: timing.domInteractive - timing.navigationStart,
        firstByte: timing.responseStart - timing.navigationStart
      };
    }
    return null;
  }

  // Get memory usage (if available)
  getMemoryUsage(): any {
    if (typeof performance !== 'undefined' && (performance as any).memory) {
      const memory = (performance as any).memory;
      return {
        usedJSHeapSize: memory.usedJSHeapSize,
        totalJSHeapSize: memory.totalJSHeapSize,
        jsHeapSizeLimit: memory.jsHeapSizeLimit
      };
    }
    return null;
  }

  // Get all collected metrics
  getMetrics(): PerformanceMetric[] {
    return [...this.metrics];
  }

  // Clear metrics
  clearMetrics(): void {
    this.metrics = [];
  }

  // Get FCP (First Contentful Paint) specifically
  getFirstContentfulPaint(): number | null {
    const fcpEntry = this.metrics.find(metric => 
      metric.type === 'paint' && metric.name === 'first-contentful-paint'
    );
    return fcpEntry ? fcpEntry.value : null;
  }

  // Get LCP (Largest Contentful Paint) if available
  getLargestContentfulPaint(): number | null {
    const lcpEntry = this.metrics.find(metric => 
      metric.type === 'largest-contentful-paint'
    );
    return lcpEntry ? lcpEntry.value : null;
  }

  // Log performance summary
  logPerformanceSummary(): void {
    const navigationTiming = this.getNavigationTiming();
    const memoryUsage = this.getMemoryUsage();
    const fcp = this.getFirstContentfulPaint();

    console.group('🚀 Performance Summary');
    
    if (navigationTiming) {
      console.log('📊 Navigation Timing:', navigationTiming);
    }
    
    if (memoryUsage) {
      console.log('💾 Memory Usage:', memoryUsage);
    }
    
    if (fcp) {
      console.log('🎨 First Contentful Paint:', `${fcp.toFixed(2)}ms`);
    }
    
    console.log('📋 All Metrics:', this.getMetrics());
    console.groupEnd();
  }

  // Cleanup observer
  destroy(): void {
    if (this.observer) {
      this.observer.disconnect();
    }
  }
}
