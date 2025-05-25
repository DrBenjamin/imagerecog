import { Component, OnInit, OnDestroy } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { CommonModule } from '@angular/common';
import { PerformanceMonitorService } from './services/performance-monitor.service';
import { AnalyticsService } from './services/analytics.service';
import { AppMonitoringService } from './services/app-monitoring.service';
import { MetricsDashboardComponent } from './components/metrics-dashboard.component';
import { DemoDataService } from './services/demo-data.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, MetricsDashboardComponent],
  templateUrl: './app.component.html',
  // Correct property name for styles
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit, OnDestroy {
  title = 'BenBox';

  urlSafe: SafeResourceUrl | null = null;
  buttonsVisible = true;
  baseUrl = 'http://212.227.102.172:8501/?embed=true&angular=true';
  private buttonNames = [
    'Country Code Lookup',
    'Static Image',
    'Variable Image',
    'Review Code',
    'Image Recognition',
    'Navigator',
    'OpenAI Agents'
  ];

  constructor(
    private sanitizer: DomSanitizer,
    private performanceMonitor: PerformanceMonitorService,
    private analytics: AnalyticsService,
    private appMonitoring: AppMonitoringService,
    private demoData: DemoDataService
  ) {
    // Mark app initialization
    this.performanceMonitor.markPerformance('app-init-start');
  }

  ngOnInit(): void {
    // Mark app initialization complete
    this.performanceMonitor.markPerformance('app-init-end');
    this.performanceMonitor.measurePerformance('app-initialization', 'app-init-start', 'app-init-end');

    // Initialize error tracking
    this.analytics.initializeErrorTracking();
    
    // Track user engagement
    this.analytics.trackUserEngagement();

    // Log performance summary after a short delay to capture paint metrics
    setTimeout(() => {
      this.performanceMonitor.logPerformanceSummary();
    }, 2000);

    // Track app load performance metrics
    const navigationTiming = this.performanceMonitor.getNavigationTiming();
    if (navigationTiming) {
      this.analytics.trackPerformanceMetric('dom_content_loaded', navigationTiming.domContentLoaded);
      this.analytics.trackPerformanceMetric('load_complete', navigationTiming.loadComplete);
      this.analytics.trackPerformanceMetric('first_byte', navigationTiming.firstByte);
    }

    // Track memory usage if available
    const memoryUsage = this.performanceMonitor.getMemoryUsage();
    if (memoryUsage) {
      this.analytics.trackPerformanceMetric('used_js_heap_size', memoryUsage.usedJSHeapSize, 'bytes');
    }
  }

  ngOnDestroy(): void {
    this.performanceMonitor.destroy();
  }

  loadQuery(query: number): void {
    // Mark the start of iframe loading
    this.performanceMonitor.markPerformance(`iframe-load-start-${query}`);
    
    // Track button click analytics
    const buttonName = this.buttonNames[query] || `Query ${query}`;
    this.analytics.trackButtonClick(buttonName, { 
      queryNumber: query,
      timestamp: Date.now()
    });

    const url = `${this.baseUrl}&query=${query}`;
    this.urlSafe = this.sanitizer.bypassSecurityTrustResourceUrl(url);
    this.buttonsVisible = false;

    // Track iframe load
    this.analytics.trackIframeLoad(url, query);

    // Mark the end of iframe setup (actual loading will be tracked separately)
    this.performanceMonitor.markPerformance(`iframe-load-end-${query}`);
    this.performanceMonitor.measurePerformance(
      `iframe-setup-${query}`, 
      `iframe-load-start-${query}`, 
      `iframe-load-end-${query}`
    );

    // Track performance metric for iframe setup time
    setTimeout(() => {
      const metrics = this.performanceMonitor.getMetrics();
      const setupMetric = metrics.find(m => m.name === `iframe-setup-${query}`);
      if (setupMetric) {
        this.analytics.trackPerformanceMetric('iframe_setup_time', setupMetric.value);
      }
    }, 100);
  }

  // Method to manually trigger performance summary (useful for debugging)
  showPerformanceSummary(): void {
    this.performanceMonitor.logPerformanceSummary();
    console.log('📊 Analytics Events:', this.analytics.getEvents());
    
    // Show comprehensive monitoring summary
    const summary = this.appMonitoring.getMonitoringSummary();
    console.log('🎯 Monitoring Summary:', summary);
  }

  // Method to export comprehensive monitoring data
  exportMonitoringData(): void {
    const data = this.appMonitoring.exportMonitoringData();
    console.log('📁 Exported Monitoring Data:', data);
    
    // Download as file
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `benbox-monitoring-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  // Method to get current performance score
  getPerformanceScore(): void {
    const score = this.appMonitoring.getPerformanceScore();
    console.log('🏆 Performance Score:', score);
    alert(`Performance Score: ${score.score}/100\nDetails: ${JSON.stringify(score.details, null, 2)}`);
  }

  // Demo methods for testing analytics
  generateDemoData(): void {
    this.demoData.generateComprehensiveDemo();
    console.log('🎭 Demo data generated! Check the metrics dashboard.');
  }

  simulateUserSession(): void {
    this.demoData.simulateUserSession();
    console.log('👤 User session simulation started!');
  }

  clearDemoData(): void {
    this.demoData.clearDemoData();
    console.log('🗑️ All demo data cleared!');
  }
}