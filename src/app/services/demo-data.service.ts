import { Injectable } from '@angular/core';
import { AnalyticsService } from './analytics.service';
import { PerformanceMonitorService } from './performance-monitor.service';

@Injectable({
  providedIn: 'root'
})
export class DemoDataService {
  
  constructor(
    private analytics: AnalyticsService,
    private performanceMonitor: PerformanceMonitorService
  ) {}

  // Generate sample performance metrics for demo purposes
  generateSampleMetrics(): void {
    console.log('🎭 Generating sample metrics for demo...');
    
    // Simulate various user interactions
    this.analytics.trackEvent('demo_page_view', { 
      page: 'home',
      source: 'demo'
    });

    this.analytics.trackButtonClick('Demo Button 1', { 
      feature: 'demo',
      timestamp: Date.now()
    });

    this.analytics.trackButtonClick('Demo Button 2', { 
      feature: 'demo',
      timestamp: Date.now() + 1000
    });

    // Simulate iframe loads
    this.analytics.trackIframeLoad('demo-url-1', 1);
    this.analytics.trackIframeLoad('demo-url-2', 2);

    // Track some performance metrics
    this.analytics.trackPerformanceMetric('demo_load_time', 1250);
    this.analytics.trackPerformanceMetric('demo_render_time', 850);
    this.analytics.trackPerformanceMetric('demo_api_response_time', 450);

    // Add some performance marks for demo
    this.performanceMonitor.markPerformance('demo-start');
    setTimeout(() => {
      this.performanceMonitor.markPerformance('demo-end');
      this.performanceMonitor.measurePerformance('demo-duration', 'demo-start', 'demo-end');
    }, 100);

    console.log('✅ Sample metrics generated successfully');
  }

  // Simulate a user session with multiple interactions
  simulateUserSession(): void {
    console.log('👤 Simulating user session...');
    
    const buttonNames = [
      'Country Code Lookup',
      'Static Image', 
      'Variable Image',
      'Review Code',
      'Image Recognition',
      'Navigator',
      'OpenAI Agents'
    ];

    let delay = 0;
    
    // Simulate user clicking through different features
    buttonNames.forEach((buttonName, index) => {
      setTimeout(() => {
        this.analytics.trackButtonClick(buttonName, {
          sessionType: 'simulated',
          sequence: index + 1,
          totalButtons: buttonNames.length
        });
        
        // Simulate iframe load after button click
        setTimeout(() => {
          this.analytics.trackIframeLoad(`simulated-url-${index}`, index);
        }, 200);

      }, delay);
      
      delay += 1500; // 1.5 seconds between clicks
    });

    // Add some errors for testing
    setTimeout(() => {
      this.analytics.trackError(new Error('Simulated network timeout'), 'demo_simulation');
    }, delay + 500);

    setTimeout(() => {
      this.analytics.trackEvent('user_session_complete', {
        totalInteractions: buttonNames.length,
        sessionType: 'simulated',
        duration: delay + 1000
      });
    }, delay + 1000);

    console.log('✅ User session simulation completed');
  }

  // Generate Core Web Vitals data for demo
  simulateCoreWebVitals(): void {
    console.log('🌐 Simulating Core Web Vitals...');
    
    // Simulate realistic Core Web Vitals metrics
    this.analytics.trackPerformanceMetric('first_contentful_paint', 1200);
    this.analytics.trackPerformanceMetric('largest_contentful_paint', 2100);
    this.analytics.trackPerformanceMetric('first_input_delay', 85);
    this.analytics.trackPerformanceMetric('cumulative_layout_shift', 0.05);

    // Simulate some memory usage tracking
    this.analytics.trackPerformanceMetric('js_heap_used', 15728640, 'bytes'); // ~15MB
    this.analytics.trackPerformanceMetric('dom_nodes', 1247, 'count');
    this.analytics.trackPerformanceMetric('event_listeners', 89, 'count');

    console.log('✅ Core Web Vitals simulation completed');
  }

  // Clear all demo data
  clearDemoData(): void {
    console.log('🗑️ Clearing demo data...');
    this.analytics.clearEvents();
    this.performanceMonitor.clearMetrics();
    console.log('✅ Demo data cleared');
  }

  // Generate a comprehensive demo dataset
  generateComprehensiveDemo(): void {
    console.log('🚀 Generating comprehensive demo dataset...');
    
    this.generateSampleMetrics();
    
    setTimeout(() => {
      this.simulateCoreWebVitals();
    }, 500);
    
    setTimeout(() => {
      this.simulateUserSession();
    }, 1000);

    console.log('✅ Comprehensive demo dataset generation started');
  }
}
