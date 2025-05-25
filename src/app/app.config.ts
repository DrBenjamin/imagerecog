
import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { routes } from './app.routes';
import { provideClientHydration } from '@angular/platform-browser';
import { PerformanceMonitorService } from './services/performance-monitor.service';
import { AnalyticsService } from './services/analytics.service';
import { AppMonitoringService } from './services/app-monitoring.service';
import { DemoDataService } from './services/demo-data.service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideClientHydration(),
    provideHttpClient(),
    PerformanceMonitorService,
    AnalyticsService,
    AppMonitoringService,
    DemoDataService
  ]
};
