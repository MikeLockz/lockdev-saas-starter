/**
 * useAnalytics - Behavioral Analytics Hook
 *
 * Provides a simple interface for tracking user behavior and events.
 * Events are sent to the backend telemetry API for CloudWatch ingestion.
 */

import { useCallback, useRef, useEffect } from 'react';
import { useAuth } from './useAuth';

interface AnalyticsEvent {
    event_name: string;
    properties?: Record<string, unknown>;
}

interface UseAnalyticsOptions {
    /** Enable/disable analytics tracking */
    enabled?: boolean;
    /** Batch events instead of sending immediately */
    batchEvents?: boolean;
    /** Flush interval for batched events (ms) */
    flushInterval?: number;
}

const API_BASE = import.meta.env.VITE_API_URL || '';

/**
 * Hook for tracking user behavior and analytics events.
 *
 * @example
 * ```tsx
 * const { track, pageView } = useAnalytics();
 *
 * // Track a button click
 * track('button_clicked', { button_id: 'submit_form' });
 *
 * // Track a page view
 * pageView('/dashboard');
 * ```
 */
export function useAnalytics(options: UseAnalyticsOptions = {}) {
    const { enabled = true, batchEvents = false, flushInterval = 5000 } = options;
    const { user } = useAuth();
    const eventQueue = useRef<AnalyticsEvent[]>([]);
    const flushTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

    /**
     * Send a single event to the telemetry API
     */
    const sendEvent = useCallback(
        async (event: AnalyticsEvent): Promise<void> => {
            if (!enabled) return;

            try {
                const response = await fetch(`${API_BASE}/api/v1/telemetry`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',
                    body: JSON.stringify(event),
                });

                if (!response.ok) {
                    console.warn('[Analytics] Failed to send event:', response.status);
                }
            } catch (error) {
                // Silently fail - analytics should never break the app
                console.warn('[Analytics] Error sending event:', error);
            }
        },
        [enabled]
    );

    /**
     * Send batched events to the telemetry API
     */
    const flushEvents = useCallback(async (): Promise<void> => {
        if (!enabled || eventQueue.current.length === 0) return;

        const events = [...eventQueue.current];
        eventQueue.current = [];

        try {
            const response = await fetch(`${API_BASE}/api/v1/telemetry/batch`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify(events),
            });

            if (!response.ok) {
                console.warn('[Analytics] Failed to send batch:', response.status);
            }
        } catch (error) {
            console.warn('[Analytics] Error sending batch:', error);
        }
    }, [enabled]);

    /**
     * Track a custom event
     */
    const track = useCallback(
        (eventName: string, properties?: Record<string, unknown>): void => {
            if (!enabled) return;

            const event: AnalyticsEvent = {
                event_name: eventName,
                properties: {
                    ...properties,
                    timestamp: new Date().toISOString(),
                    user_id: user?.uid,
                },
            };

            if (batchEvents) {
                eventQueue.current.push(event);
            } else {
                sendEvent(event);
            }
        },
        [enabled, batchEvents, sendEvent, user?.uid]
    );

    /**
     * Track a page view event
     */
    const pageView = useCallback(
        (path: string, properties?: Record<string, unknown>): void => {
            track('page_view', {
                path,
                referrer: document.referrer,
                ...properties,
            });
        },
        [track]
    );

    /**
     * Track a click event
     */
    const trackClick = useCallback(
        (elementId: string, properties?: Record<string, unknown>): void => {
            track('element_clicked', {
                element_id: elementId,
                ...properties,
            });
        },
        [track]
    );

    /**
     * Track an error event
     */
    const trackError = useCallback(
        (error: Error, context?: Record<string, unknown>): void => {
            track('error', {
                error_name: error.name,
                error_message: error.message,
                ...context,
            });
        },
        [track]
    );

    /**
     * Identify the current user (for when auth state changes)
     */
    const identify = useCallback(
        (userId: string, traits?: Record<string, unknown>): void => {
            track('user_identified', {
                user_id: userId,
                ...traits,
            });
        },
        [track]
    );

    // Set up flush timer for batched events
    useEffect(() => {
        if (batchEvents && enabled) {
            flushTimerRef.current = setInterval(flushEvents, flushInterval);
        }

        return () => {
            if (flushTimerRef.current) {
                clearInterval(flushTimerRef.current);
            }
            // Flush remaining events on unmount
            if (eventQueue.current.length > 0) {
                flushEvents();
            }
        };
    }, [batchEvents, enabled, flushInterval, flushEvents]);

    // Flush events on page unload
    useEffect(() => {
        const handleUnload = () => {
            if (eventQueue.current.length > 0) {
                // Use sendBeacon for reliability on page unload
                navigator.sendBeacon(
                    `${API_BASE}/api/v1/telemetry/batch`,
                    JSON.stringify(eventQueue.current)
                );
            }
        };

        window.addEventListener('beforeunload', handleUnload);
        return () => window.removeEventListener('beforeunload', handleUnload);
    }, []);

    return {
        track,
        pageView,
        trackClick,
        trackError,
        identify,
        flush: flushEvents,
    };
}
