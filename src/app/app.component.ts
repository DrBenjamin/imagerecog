import { Component, OnInit } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { CommonModule } from '@angular/common';
import { MetricsDashboardComponent } from './components/metrics-dashboard.component';
import { PerformanceMonitorService } from './services/performance-monitor.service';
import { AnalyticsService } from './services/analytics.service';
import { AppMonitoringService } from './services/app-monitoring.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, MetricsDashboardComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit {
  title = 'BenBox';

  urlSafe: SafeResourceUrl | null = null;
  buttonsVisible = true;
  baseUrl = 'http://212.227.102.172:8501/?embed=true';
  ragOnSnowUrl = 'http://212.227.102.172:8502/?embed=true&angular=true';
  showMetrics = false;

  constructor(
    private sanitizer: DomSanitizer,
    private analyticsService: AnalyticsService,
    private performanceMonitorService: PerformanceMonitorService,
    private appMonitoringService: AppMonitoringService
  ) {
    // defer iframe loading until user clicks a button
  }

  ngOnInit(): void {
    try {
      // Track app initialization
      this.analyticsService.trackEvent('app_initialized');
      
      // Add initial performance metric
      this.performanceMonitorService.addMetric('app_load_time', performance.now());
    } catch (error) {
      console.error('Error during app initialization:', error);
      // Continue app initialization even if metrics fail
    }
  }

  loadQuery(query: number): void {
    try {
      const url = `${this.baseUrl}&query=${query}`;
      this.urlSafe = this.sanitizer.bypassSecurityTrustResourceUrl(url);
      this.buttonsVisible = false;
      
      // Track query selection
      this.analyticsService.trackEvent('load_query', { query: query?.toString() || 'unknown' });
    } catch (error) {
      console.error('Error loading query:', error);
      // Fallback to core functionality without analytics
      const url = `${this.baseUrl}&query=${query}`;
      this.urlSafe = this.sanitizer.bypassSecurityTrustResourceUrl(url);
      this.buttonsVisible = false;
    }
  }

  loadRagOnSnow(): void {
    try {
      this.urlSafe = this.sanitizer.bypassSecurityTrustResourceUrl(this.ragOnSnowUrl);
      this.buttonsVisible = false;
      
      // Track RagOnSnow selection
      this.analyticsService.trackEvent('load_rag_on_snow');
    } catch (error) {
      console.error('Error loading RagOnSnow:', error);
      // Fallback to core functionality without analytics
      this.urlSafe = this.sanitizer.bypassSecurityTrustResourceUrl(this.ragOnSnowUrl);
      this.buttonsVisible = false;
    }
  }

  toggleMetrics(): void {
    try {
      this.showMetrics = !this.showMetrics;
      this.analyticsService.trackEvent('toggle_metrics', { shown: this.showMetrics });
    } catch (error) {
      console.error('Error toggling metrics:', error);
      this.showMetrics = !this.showMetrics;
    }
  }
}