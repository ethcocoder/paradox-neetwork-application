import { AppState, AppStateStatus } from 'react-native';
import * as Battery from 'expo-battery';
import { setLowPowerMode } from './message-service';

/**
 * Performance Monitor
 * 
 * Automatically adjusts app performance based on:
 * - Battery level and charging state
 * - App background/foreground state
 * - Available memory
 * - Network conditions
 */

class PerformanceMonitor {
    private batteryLevel: number = 1.0;
    private isCharging: boolean = false;
    private appState: AppStateStatus = 'active';
    private batterySubscription: any = null;
    private appStateSubscription: any = null;

    /**
     * Start monitoring device state
     */
    async start() {
        console.log('[PerformanceMonitor] Starting...');

        // Monitor battery
        try {
            this.batteryLevel = await Battery.getBatteryLevelAsync();
            const batteryState = await Battery.getBatteryStateAsync();
            this.isCharging = batteryState === Battery.BatteryState.CHARGING;

            // Subscribe to battery updates
            this.batterySubscription = Battery.addBatteryLevelListener(({ batteryLevel }) => {
                this.batteryLevel = batteryLevel;
                this.updatePerformanceMode();
            });

            Battery.addBatteryStateListener(({ batteryState }) => {
                this.isCharging = batteryState === Battery.BatteryState.CHARGING;
                this.updatePerformanceMode();
            });
        } catch (error) {
            console.warn('[PerformanceMonitor] Battery API not available:', error);
        }

        // Monitor app state (foreground/background)
        this.appStateSubscription = AppState.addEventListener('change', (nextAppState) => {
            this.appState = nextAppState;
            this.updatePerformanceMode();
        });

        // Initial performance mode
        this.updatePerformanceMode();

        console.log('[PerformanceMonitor] ✓ Started');
    }

    /**
     * Stop monitoring
     */
    stop() {
        if (this.batterySubscription) {
            this.batterySubscription.remove();
        }
        if (this.appStateSubscription) {
            this.appStateSubscription.remove();
        }
        console.log('[PerformanceMonitor] Stopped');
    }

    /**
     * Update performance mode based on current device state
     */
    private updatePerformanceMode() {
        const shouldUseLowPower = this.shouldEnableLowPower();
        setLowPowerMode(shouldUseLowPower);

        console.log('[PerformanceMonitor] Update:', {
            battery: `${(this.batteryLevel * 100).toFixed(0)}%`,
            charging: this.isCharging,
            appState: this.appState,
            lowPowerMode: shouldUseLowPower,
        });
    }

    /**
     * Determine if low power mode should be enabled
     */
    private shouldEnableLowPower(): boolean {
        // Enable low power mode if:
        // 1. Battery is low (<20%) and not charging
        // 2. App is in background

        if (this.appState !== 'active') {
            return true; // Always use low power in background
        }

        if (!this.isCharging && this.batteryLevel < 0.20) {
            return true; // Low battery and not charging
        }

        return false;
    }

    /**
     * Get current device state
     */
    getState() {
        return {
            batteryLevel: this.batteryLevel,
            isCharging: this.isCharging,
            appState: this.appState,
            lowPowerRecommended: this.shouldEnableLowPower(),
        };
    }
}

// Singleton instance
export const performanceMonitor = new PerformanceMonitor();

/**
 * React hook for performance monitoring
 */
export function usePerformanceMonitoring() {
    const [state, setState] = React.useState(performanceMonitor.getState());

    React.useEffect(() => {
        performanceMonitor.start();

        // Update state periodically
        const interval = setInterval(() => {
            setState(performanceMonitor.getState());
        }, 5000); // Update every 5 seconds

        return () => {
            clearInterval(interval);
            performanceMonitor.stop();
        };
    }, []);

    return state;
}

/**
 * Memory management utilities
 */
export const MemoryManager = {
    /**
     * Estimate current memory usage (approximate)
     */
    getMemoryUsage(): { used: number; total: number } {
        // Note: React Native doesn't provide direct memory APIs
        // This is an approximation
        if (global.performance && (performance as any).memory) {
            const memory = (performance as any).memory;
            return {
                used: memory.usedJSHeapSize / (1024 * 1024), // MB
                total: memory.totalJSHeapSize / (1024 * 1024), // MB
            };
        }
        return { used: 0, total: 0 };
    },

    /**
     * Force garbage collection (if available)
     */
    forceGC() {
        if (global.gc) {
            console.log('[MemoryManager] Forcing garbage collection...');
            global.gc();
        }
    },

    /**
     * Check if memory is constrained
     */
    isMemoryConstrained(): boolean {
        const { used, total } = this.getMemoryUsage();
        if (total === 0) return false;
        return used / total > 0.8; // 80% memory usage
    },
};

/**
 * Network condition monitoring
 */
export const NetworkMonitor = {
    /**
     * Check if network is slow
     */
    async isSlowNetwork(): Promise<boolean> {
        try {
            // Simple fetch test with timeout
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 2000);

            const start = Date.now();
            await fetch('https://www.google.com/favicon.ico', {
                signal: controller.signal,
                cache: 'no-store',
            });
            clearTimeout(timeout);

            const duration = Date.now() - start;
            return duration > 1000; // Slow if >1s for tiny file
        } catch {
            return true; // Assume slow if fetch fails
        }
    },

    /**
     * Get recommended quality based on network
     */
    async getRecommendedQuality(): Promise<'high' | 'medium' | 'low'> {
        const isSlow = await this.isSlowNetwork();
        if (isSlow) return 'low';
        return 'high';
    },
};

/**
 * Performance optimization recommendations
 */
export function getOptimizationRecommendations() {
    const memoryConstrained = MemoryManager.isMemoryConstrained();
    const deviceState = performanceMonitor.getState();

    return {
        // Cache settings
        maxCacheSize: memoryConstrained ? 20 : 50,

        // Parallel processing
        maxParallelTasks: deviceState.lowPowerRecommended ? 2 : 5,

        // Image quality
        imageQuality: deviceState.lowPowerRecommended ? 'medium' : 'high',

        // Chunk size for encoding
        chunkSize: deviceState.lowPowerRecommended ? 1024 : 2048,

        // Throttle delays
        throttleMs: deviceState.lowPowerRecommended ? 1000 : 500,
    };
}

// Auto-import React for hooks
import React from 'react';
