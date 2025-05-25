import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: number;
}

@Injectable({
  providedIn: 'root'
})
export class PerformanceMonitorService {
  private metricsSubject = new BehaviorSubject<PerformanceMetric[]>([]);
  
  constructor() {
    try {
      // Initialize with empty metrics
      this.metricsSubject.next([]);
      console.log('PerformanceMonitorService initialized');
    } catch (error) {
      console.error('Error initializing PerformanceMonitorService:', error);
      // Ensure we always have a valid initial state
      this.metricsSubject.next([]);
    }
  }

  addMetric(name: string | undefined | null, value: number | undefined | null): void {
    try {
      // Validate inputs to prevent undefined errors
      if (name === undefined || name === null) {
        console.warn('Attempted to add metric with undefined/null name, skipping');
        return;
      }
      
      if (value === undefined || value === null || isNaN(value)) {
        console.warn(`Attempted to add metric ${name} with invalid value, skipping`);
        return;
      }

      const metric: PerformanceMetric = {
        name,
        value,
        timestamp: Date.now()
      };

      const currentMetrics = this.metricsSubject.getValue();
      this.metricsSubject.next([...currentMetrics, metric]);
    } catch (error) {
      console.error('Error adding performance metric:', error);
      // Don't update the metrics if there was an error
    }
  }

  getMetrics(): Observable<PerformanceMetric[]> {
    return this.metricsSubject.asObservable();
  }

  clearMetrics(): void {
    try {
      this.metricsSubject.next([]);
    } catch (error) {
      console.error('Error clearing metrics:', error);
    }
  }
}