import { useEffect, useCallback, useRef, useState } from 'react';
import { useAuth } from './useAuth';

// HIPAA Session Timeout Configuration
const SESSION_TIMEOUT_MS = 15 * 60 * 1000; // 15 minutes (HIPAA requirement)
const WARNING_BEFORE_MS = 5 * 60 * 1000; // 5 minutes warning

export interface SessionMonitorState {
    isIdle: boolean;
    showWarning: boolean;
    timeRemaining: number; // seconds
    extendSession: () => void;
}

export function useSessionMonitor(): SessionMonitorState {
    const { user, signOut } = useAuth();
    const [isIdle, setIsIdle] = useState(false);
    const [showWarning, setShowWarning] = useState(false);
    const [timeRemaining, setTimeRemaining] = useState(SESSION_TIMEOUT_MS / 1000);

    const lastActivityRef = useRef(Date.now());
    const warningTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const logoutTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const countdownRef = useRef<ReturnType<typeof setInterval> | null>(null);

    const clearTimers = useCallback(() => {
        if (warningTimerRef.current) {
            clearTimeout(warningTimerRef.current);
            warningTimerRef.current = null;
        }
        if (logoutTimerRef.current) {
            clearTimeout(logoutTimerRef.current);
            logoutTimerRef.current = null;
        }
        if (countdownRef.current) {
            clearInterval(countdownRef.current);
            countdownRef.current = null;
        }
    }, []);

    const resetTimers = useCallback(() => {
        if (!user) return;

        clearTimers();
        lastActivityRef.current = Date.now();
        setIsIdle(false);
        setShowWarning(false);
        setTimeRemaining(SESSION_TIMEOUT_MS / 1000);

        // Set warning timer (triggers 5 min before timeout)
        warningTimerRef.current = setTimeout(() => {
            setIsIdle(true);
            setShowWarning(true);

            // Start countdown
            let remaining = WARNING_BEFORE_MS / 1000;
            setTimeRemaining(remaining);

            countdownRef.current = setInterval(() => {
                remaining -= 1;
                setTimeRemaining(remaining);

                if (remaining <= 0) {
                    clearInterval(countdownRef.current!);
                }
            }, 1000);
        }, SESSION_TIMEOUT_MS - WARNING_BEFORE_MS);

        // Set logout timer
        logoutTimerRef.current = setTimeout(() => {
            signOut();
        }, SESSION_TIMEOUT_MS);
    }, [user, clearTimers, signOut]);

    const extendSession = useCallback(() => {
        resetTimers();
    }, [resetTimers]);

    // Activity listeners
    useEffect(() => {
        if (!user) return;

        const handleActivity = () => {
            // Only reset if not in warning state
            if (!showWarning) {
                resetTimers();
            }
        };

        const events = ['mousedown', 'keydown', 'scroll', 'touchstart'];
        events.forEach((event) => {
            window.addEventListener(event, handleActivity);
        });

        // Initial timer setup
        resetTimers();

        return () => {
            events.forEach((event) => {
                window.removeEventListener(event, handleActivity);
            });
            clearTimers();
        };
    }, [user, resetTimers, clearTimers, showWarning]);

    return {
        isIdle,
        showWarning,
        timeRemaining,
        extendSession,
    };
}
