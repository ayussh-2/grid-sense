"use client";

import { useEffect, useState, useCallback } from "react";
import { Sidebar, Header } from "@/components/dashboard";
import { MetricsGrid } from "@/components/dashboard/MetricsGrid";
import { LiveChart } from "@/components/dashboard/LiveChart";
import { DeviceTable } from "@/components/dashboard/DeviceTable";
import { AIPanel } from "@/components/dashboard/AIPanel";
import { apiClient, type DeviceTelemetry, type GridContext } from "@/lib/api";

interface ChartDataPoint {
    timestamp: number;
    current: number;
}

export default function DashboardPage() {
    const [devices, setDevices] = useState<DeviceTelemetry[]>([]);
    const [gridContext, setGridContext] = useState<GridContext | null>(null);
    const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
    const [systemStatus, setSystemStatus] = useState<"normal" | "warning" | "critical">("normal");

    // Calculate aggregate metrics
    const totalCurrent = devices.reduce((sum, device) => sum + device.current, 0);
    const totalPower = devices.reduce((sum, device) => sum + device.power, 0);
    const avgVoltage = devices.length > 0
        ? devices.reduce((sum, device) => sum + device.voltage, 0) / devices.length
        : 0;
    const estimatedCost = gridContext
        ? (totalPower / 1000) * gridContext.electricity_price
        : 0;

    // Check for critical conditions
    const criticalCurrent = totalCurrent > 100; // Threshold for critical current
    const hasFault = devices.some(device => device.status === "fault");

    useEffect(() => {
        if (criticalCurrent || hasFault) {
            setSystemStatus("critical");
        } else if (totalCurrent > 80) {
            setSystemStatus("warning");
        } else {
            setSystemStatus("normal");
        }
    }, [criticalCurrent, hasFault, totalCurrent]);

    // Fetch live data from devices
    const fetchLiveData = useCallback(async () => {
        try {
            const data = await apiClient.getLiveData();
            const deviceArray = Object.values(data);
            setDevices(deviceArray);

            // Update chart data (keep last 30 points)
            const now = Date.now();
            const current = deviceArray.reduce((sum, device) => sum + device.current, 0);
            
            setChartData(prev => {
                const newData = [...prev, { timestamp: now, current }];
                return newData.slice(-30); // Keep last 30 data points
            });
        } catch (error) {
            console.error("Failed to fetch live data:", error);
        }
    }, []);

    // Fetch grid context
    const fetchGridContext = useCallback(async () => {
        try {
            const context = await apiClient.getGridContext();
            setGridContext(context);
        } catch (error) {
            console.error("Failed to fetch grid context:", error);
        }
    }, []);

    // Handle device control
    const handleDeviceControl = async (deviceId: string, action: "on" | "off") => {
        try {
            if (action === "on") {
                await apiClient.turnDeviceOn(deviceId);
            } else {
                await apiClient.turnDeviceOff(deviceId);
            }
            // Refresh data after control action
            await fetchLiveData();
        } catch (error) {
            console.error(`Failed to ${action} device:`, error);
        }
    };

    // Setup polling for live data (every 1 second)
    useEffect(() => {
        fetchLiveData();
        const interval = setInterval(fetchLiveData, 1000);
        return () => clearInterval(interval);
    }, [fetchLiveData]);

    // Setup polling for grid context (every 15 minutes)
    useEffect(() => {
        fetchGridContext();
        const interval = setInterval(fetchGridContext, 15 * 60 * 1000);
        return () => clearInterval(interval);
    }, [fetchGridContext]);

    return (
        <div className="min-h-screen">
            <Sidebar />
            
            <div className="ml-64">
                <Header systemStatus={systemStatus} />
                
                <main className="p-6 space-y-6">
                    {/* KPI Metrics */}
                    <MetricsGrid
                        totalCurrent={totalCurrent}
                        totalPower={totalPower}
                        avgVoltage={avgVoltage}
                        estimatedCost={estimatedCost}
                        criticalCurrent={criticalCurrent}
                        gridContext={gridContext}
                    />

                    {/* Live Chart */}
                    <LiveChart 
                        data={chartData} 
                        critical={criticalCurrent || hasFault}
                    />

                    {/* Bottom Grid: Device Table + AI Panel */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div className="lg:col-span-2">
                            <DeviceTable 
                                devices={devices} 
                                onDeviceControl={handleDeviceControl}
                            />
                        </div>
                        <div>
                            <AIPanel 
                                critical={criticalCurrent || hasFault} 
                                gridContext={gridContext}
                                totalCurrent={totalCurrent}
                            />
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}
