import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface AnalyticsEvent {
  name: string;
  properties?: Record<string, string | number | boolean>;
  timestamp: number;
}

@Injectable({
  providedIn: 'root'
})
export class AnalyticsService {
  private eventsSubject = new BehaviorSubject<AnalyticsEvent[]>([]);
  private isEnabled = true;

  constructor() {
    try {
      console.log('AnalyticsService initialized');
      // Initialize with empty events
      this.eventsSubject.next([]);
    } catch (error) {
      console.error('Error initializing AnalyticsService:', error);
      // Ensure we always have a valid initial state
      this.eventsSubject.next([]);
    }
  }

  trackEvent(name: string | undefined | null, properties?: Record<string, any>): void {
    try {
      // Early return if analytics is disabled
      if (!this.isEnabled) return;

      // Validate inputs to prevent undefined errors
      if (name === undefined || name === null) {
        console.warn('Attempted to track event with undefined/null name, skipping');
        return;
      }

      // Clean properties to ensure they're serializable
      const cleanProperties: Record<string, string | number | boolean> = {};
      
      if (properties) {
        Object.entries(properties).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
              cleanProperties[key] = value;
            } else {
              try {
                // Try to stringify objects, but use a fallback if it fails
                cleanProperties[key] = JSON.stringify(value);
              } catch {
                cleanProperties[key] = String(value);
              }
            }
          }
        });
      }

      const event: AnalyticsEvent = {
        name,
        properties: cleanProperties,
        timestamp: Date.now()
      };

      const currentEvents = this.eventsSubject.getValue();
      this.eventsSubject.next([...currentEvents, event]);
    } catch (error) {
      console.error('Error tracking analytics event:', error);
      // Don't update the events if there was an error
    }
  }

  getEvents(): Observable<AnalyticsEvent[]> {
    return this.eventsSubject.asObservable();
  }

  clearEvents(): void {
    try {
      this.eventsSubject.next([]);
    } catch (error) {
      console.error('Error clearing events:', error);
    }
  }

  enable(): void {
    this.isEnabled = true;
  }

  disable(): void {
    this.isEnabled = false;
  }
}