"use client";

import { useCallback, useState } from "react";
import { Header, DemoPanel } from "@/components/dashboard";
import { MetricsGrid } from "@/components/dashboard/MetricsGrid";
import { LiveChart } from "@/components/dashboard/LiveChart";
import { DeviceTable } from "@/components/dashboard/DeviceTable";
import { PathwayPanel } from "@/components/dashboard/PathwayPanel";
import {
    apiClient,
    type DeviceTelemetry,
    type GridContext,
    type PathwayAnomaly,
    type PathwayDeviceStats,
    type LLMInsight,
    type WsMessage,
} from "@/lib/api";
import { useWebSocket } from "@/hooks/useWebSocket";

interface ChartDataPoint {
    timestamp: number;
    current: number;
}

const ANOMALY_RECENCY_WINDOW_MS = 60_000;

function getSystemStatus(
    totalCurrent: number,
    hasFault: boolean,
    hasRecentAnomalies: boolean,
): "normal" | "warning" | "critical" {
    if (hasFault || (totalCurrent > 100 && hasRecentAnomalies))
        return "critical";
    if (totalCurrent > 100 || hasRecentAnomalies) return "warning";
    if (totalCurrent > 80) return "warning";
    return "normal";
}

export default function DashboardPage() {
    const [devices, setDevices] = useState<DeviceTelemetry[]>([]);
    const [gridContext, setGridContext] = useState<GridContext | null>(null);
    const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
    const [pathwayAnomalies, setPathwayAnomalies] = useState<PathwayAnomaly[]>(
        [],
    );
    const [pathwayActive, setPathwayActive] = useState(false);
    const [pathwayStatistics, setPathwayStatistics] = useState<{
        [device_type: string]: PathwayDeviceStats;
    }>({});
    const [llmInsight, setLlmInsight] = useState<LLMInsight | null>(null);

    const totalCurrent = devices.reduce(
        (sum, device) => sum + device.current,
        0,
    );
    const totalPower = devices.reduce((sum, device) => sum + device.power, 0);
    const avgVoltage =
        devices.length > 0
            ? devices.reduce((sum, device) => sum + device.voltage, 0) /
              devices.length
            : 0;
    const estimatedCost = gridContext
        ? (totalPower / 1000) * gridContext.electricity_price
        : 0;

    const hasFault = devices.some((device) => device.status === "fault");
    const criticalCurrent = totalCurrent > 100;

    const now = Date.now();
    const recentAnomalies = pathwayAnomalies.filter(
        (a) => now - a.timestamp * 1000 < ANOMALY_RECENCY_WINDOW_MS,
    );
    const hasRecentAnomalies = recentAnomalies.length > 0;

    const systemStatus = getSystemStatus(
        totalCurrent,
        hasFault,
        hasRecentAnomalies,
    );

    const handleWsMessage = useCallback((msg: WsMessage) => {
        switch (msg.type) {
            case "live_data": {
                const deviceArray = Object.values(msg.data);
                setDevices(deviceArray);
                const current = deviceArray.reduce(
                    (sum, d) => sum + d.current,
                    0,
                );
                setChartData((prev) => {
                    const next = [...prev, { timestamp: Date.now(), current }];
                    return next.slice(-30);
                });
                break;
            }
            case "grid_context":
                setGridContext(msg.data);
                break;
            case "pathway_data": {
                const { pathway_active, anomalies, statistics } = msg.data;
                setPathwayActive(pathway_active);
                if (anomalies) setPathwayAnomalies(anomalies);
                if (statistics) setPathwayStatistics(statistics);
                break;
            }
            case "llm_insight":
                setLlmInsight(msg.data);
                break;
        }
    }, []);

    const { connected } = useWebSocket(handleWsMessage);

    const handleDeviceControl = async (
        deviceId: string,
        action: "on" | "off",
    ) => {
        try {
            if (action === "on") {
                await apiClient.turnDeviceOn(deviceId);
            } else {
                await apiClient.turnDeviceOff(deviceId);
            }
        } catch (error) {
            console.error(`Failed to ${action} device:`, error);
        }
    };

    return (
        <div className="min-h-screen">
            <div className="">
                <Header systemStatus={systemStatus} connected={connected} />

                <main className="p-6 space-y-6">
                    <DemoPanel />

                    <MetricsGrid
                        totalCurrent={totalCurrent}
                        totalPower={totalPower}
                        avgVoltage={avgVoltage}
                        estimatedCost={estimatedCost}
                        criticalCurrent={criticalCurrent}
                        gridContext={gridContext}
                    />

                    <div className="flex flex-row gap-6">
                        <LiveChart
                            data={chartData}
                            critical={criticalCurrent || hasFault}
                        />
                    </div>

                    <PathwayPanel
                        anomalies={pathwayAnomalies}
                        statistics={pathwayStatistics}
                        isActive={pathwayActive}
                        insight={llmInsight}
                    />

                    <div className="w-full flex flex-row gap-6">
                        <DeviceTable
                            devices={devices}
                            onDeviceControl={handleDeviceControl}
                        />
                    </div>
                </main>
            </div>
        </div>
    );
}
