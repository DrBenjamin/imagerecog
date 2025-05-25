import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { PerformanceMonitorService } from './performance-monitor.service';
import { AnalyticsService } from './analytics.service';

export interface SystemState {
  memoryUsage?: number;
  cpuUsage?: number;
  networkLatency?: number;
  timestamp: number;
}

@Injectable({
  providedIn: 'root'
})
export class AppMonitoringService {
  private systemStateSubject = new BehaviorSubject<SystemState | null>(null);
  private monitoringEnabled = false;
  private monitoringInterval: any = null;

  constructor(
    private performanceService: PerformanceMonitorService,
    private analyticsService: AnalyticsService
  ) {
    try {
      // Initialize with default state
      this.systemStateSubject.next({
        timestamp: Date.now()
      });
      console.log('AppMonitoringService initialized');
    } catch (error) {
      console.error('Error initializing AppMonitoringService:', error);
      // Ensure we always have a valid initial state
      this.systemStateSubject.next({
        timestamp: Date.now()
      });
    }
  }

  startMonitoring(intervalMs: number = 30000): void {
    try {
      if (this.monitoringEnabled) {
        console.log('Monitoring already active');
        return;
      }

      this.monitoringEnabled = true;
      
      // Use a safe interval value
      const safeInterval = intervalMs > 0 ? intervalMs : 30000;
      
      // Track monitoring start event
      this.analyticsService.trackEvent('monitoring_started', { interval: safeInterval });
      
      // Immediately collect initial metrics
      this.collectMetrics();
      
      // Set up interval for collecting metrics
      this.monitoringInterval = setInterval(() => {
        this.collectMetrics();
      }, safeInterval);
    } catch (error) {
      console.error('Error starting monitoring:', error);
      this.stopMonitoring(); // Ensure monitoring is stopped if there's an error
    }
  }

  stopMonitoring(): void {
    try {
      if (!this.monitoringEnabled) {
        return;
      }

      if (this.monitoringInterval) {
        clearInterval(this.monitoringInterval);
        this.monitoringInterval = null;
      }
      
      this.monitoringEnabled = false;
      this.analyticsService.trackEvent('monitoring_stopped');
    } catch (error) {
      console.error('Error stopping monitoring:', error);
      // Force clear interval to prevent memory leaks
      if (this.monitoringInterval) {
        clearInterval(this.monitoringInterval);
        this.monitoringInterval = null;
      }
    }
  }

  getSystemState(): Observable<SystemState | null> {
    return this.systemStateSubject.asObservable();
  }

  private collectMetrics(): void {
    try {
      // Memory usage estimation (this is a rough approximation)
      let memoryUsage: number | undefined;
      if (performance && 'memory' in performance) {
        const memoryInfo = (performance as any).memory;
        if (memoryInfo && typeof memoryInfo.usedJSHeapSize === 'number') {
          memoryUsage = memoryInfo.usedJSHeapSize / (1024 * 1024); // Convert to MB
        }
      }

      // Create a new system state
      const systemState: SystemState = {
        memoryUsage,
        timestamp: Date.now()
      };

      // Update system state
      this.systemStateSubject.next(systemState);

      // Log metrics to performance service if memory usage is available
      if (memoryUsage !== undefined) {
        this.performanceService.addMetric('memory_usage_mb', memoryUsage);
      }
    } catch (error) {
      console.error('Error collecting metrics:', error);
      // Don't update the system state if there was an error
    }
  }
}