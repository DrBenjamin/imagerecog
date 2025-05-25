import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
import { PerformanceMonitorService } from '../services/performance-monitor.service';
import { AnalyticsService } from '../services/analytics.service';
import { AppMonitoringService } from '../services/app-monitoring.service';
import { DemoDataService } from '../services/demo-data.service';

@Component({
  selector: 'app-metrics-dashboard',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="metrics-container">
      <h2>App Metrics Dashboard</h2>
      <div *ngIf="isError" class="error-message">
        Error loading metrics. Please try again later.
      </div>
      <div *ngIf="!isError">
        <div class="metric-card">
          <h3>System Memory</h3>
          <p>{{ memoryUsage || 'N/A' }}</p>
        </div>
        <div class="metric-card">
          <h3>Events</h3>
          <p>{{ eventCount }}</p>
        </div>
        <div class="metric-card">
          <h3>Performance Metrics</h3>
          <p>{{ metricsCount }}</p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .metrics-container {
      padding: 16px;
      background-color: #f5f5f5;
      border-radius: 8px;
      margin: 16px;
    }
    .metric-card {
      background-color: white;
      border-radius: 4px;
      padding: 16px;
      margin-bottom: 16px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .error-message {
      color: red;
      padding: 16px;
      background-color: #ffeeee;
      border-radius: 4px;
      margin-bottom: 16px;
    }
    h2 {
      margin-top: 0;
      margin-bottom: 16px;
    }
    h3 {
      margin-top: 0;
      margin-bottom: 8px;
    }
  `]
})
export class MetricsDashboardComponent implements OnInit, OnDestroy {
  memoryUsage: string | null = null;
  eventCount = 0;
  metricsCount = 0;
  isError = false;
  
  private subscriptions: Subscription[] = [];

  constructor(
    private performanceService: PerformanceMonitorService,
    private analyticsService: AnalyticsService,
    private monitoringService: AppMonitoringService,
    private demoDataService: DemoDataService
  ) {}

  ngOnInit(): void {
    try {
      // Track dashboard open event
      this.analyticsService.trackEvent('metrics_dashboard_opened');
      
      // Subscribe to system state updates
      this.subscribeToSystemState();
      
      // Subscribe to performance metrics
      this.subscribeToPerformanceMetrics();
      
      // Subscribe to analytics events
      this.subscribeToAnalyticsEvents();
      
      // Start monitoring with a 30-second interval
      this.monitoringService.startMonitoring(30000);
      
      // Generate some demo data for testing
      this.generateDemoData();
    } catch (error) {
      console.error('Error initializing metrics dashboard:', error);
      this.isError = true;
    }
  }

  ngOnDestroy(): void {
    try {
      // Clean up all subscriptions
      this.subscriptions.forEach(sub => sub.unsubscribe());
      this.subscriptions = [];
      
      // Stop monitoring service
      this.monitoringService.stopMonitoring();
      
      // Track dashboard close event
      this.analyticsService.trackEvent('metrics_dashboard_closed');
    } catch (error) {
      console.error('Error cleaning up metrics dashboard:', error);
    }
  }

  private subscribeToSystemState(): void {
    try {
      const sub = this.monitoringService.getSystemState().subscribe(state => {
        if (state && state.memoryUsage !== undefined) {
          this.memoryUsage = `${state.memoryUsage.toFixed(2)} MB`;
        } else {
          this.memoryUsage = null;
        }
      });
      this.subscriptions.push(sub);
    } catch (error) {
      console.error('Error subscribing to system state:', error);
    }
  }

  private subscribeToPerformanceMetrics(): void {
    try {
      const sub = this.performanceService.getMetrics().subscribe(metrics => {
        this.metricsCount = metrics.length;
      });
      this.subscriptions.push(sub);
    } catch (error) {
      console.error('Error subscribing to performance metrics:', error);
    }
  }

  private subscribeToAnalyticsEvents(): void {
    try {
      const sub = this.analyticsService.getEvents().subscribe(events => {
        this.eventCount = events.length;
      });
      this.subscriptions.push(sub);
    } catch (error) {
      console.error('Error subscribing to analytics events:', error);
    }
  }

  private generateDemoData(): void {
    try {
      // Add some demo performance metrics
      this.performanceService.addMetric('page_load', 1200);
      this.performanceService.addMetric('button_click', 50);
      
      // Track some demo events
      this.analyticsService.trackEvent('page_view', { route: '/dashboard' });
      this.analyticsService.trackEvent('user_interaction', { action: 'click', element: 'button' });
      
      // Generate some time series data
      const timeSeriesData = this.demoDataService.generateTimeSeriesData(10, 50, 100);
      console.log('Generated demo time series data:', timeSeriesData);
    } catch (error) {
      console.error('Error generating demo data:', error);
    }
  }
}