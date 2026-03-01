"use client";

import { Card } from "@/components/ui";
import { Heading, Body, Label } from "@/components/typography";
import {
    Activity,
    TrendingUp,
    AlertTriangle,
    CheckCircle,
    ShieldAlert,
    Lightbulb,
    DollarSign,
    Leaf,
    Loader2,
    XCircle,
} from "lucide-react";
import { Badge } from "@/components/ui";
import type { PathwayAnomaly, PathwayDeviceStats, LLMInsight } from "@/lib/api";

interface PathwayPanelProps {
    anomalies: PathwayAnomaly[];
    statistics: { [device_type: string]: PathwayDeviceStats };
    isActive: boolean;
    insight: LLMInsight | null;
}

const SEVERITY_CONFIG = {
    normal: {
        badge: "success" as const,
        label: "Normal",
        border: "",
        icon: CheckCircle,
    },
    warning: {
        badge: "warning" as const,
        label: "Warning",
        border: "border-l-4 border-amber-500",
        icon: AlertTriangle,
    },
    critical: {
        badge: "critical" as const,
        label: "Critical",
        border: "border-l-4 border-red-500",
        icon: ShieldAlert,
    },
};

function timeAgo(timestamp: number): string {
    const seconds = Math.floor(Date.now() / 1000 - timestamp);
    if (seconds < 5) return "just now";
    if (seconds < 60) return `${seconds}s ago`;
    return `${Math.floor(seconds / 60)}m ago`;
}

export function PathwayPanel({
    anomalies = [],
    statistics = {},
    isActive = false,
    insight = null,
}: PathwayPanelProps) {
    const recentAnomalies = anomalies.slice(-5).reverse();
    const severityConfig = insight
        ? SEVERITY_CONFIG[insight.severity]
        : null;

    return (
        <Card className={`w-full ${severityConfig?.border ?? ""}`}>
            {/* Header */}
            <div className="mb-6 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div
                        className={`w-10 h-10 rounded-lg flex items-center justify-center ${isActive ? "bg-purple-500/10" : "bg-gray-500/10"}`}
                    >
                        <Activity
                            className={`w-5 h-5 ${isActive ? "text-purple-500" : "text-gray-500"}`}
                        />
                    </div>
                    <div>
                        <Heading level={3}>Pathway Analytics</Heading>
                        <Body muted className="text-xs">
                            Real-time stream processing
                            {insight &&
                                ` -- updated ${timeAgo(insight.timestamp)}`}
                        </Body>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    {severityConfig && (
                        <Badge variant={severityConfig.badge}>
                            <severityConfig.icon className="w-3 h-3 mr-1" />
                            {severityConfig.label}
                        </Badge>
                    )}
                    <Badge variant={isActive ? "success" : "default"}>
                        {isActive ? "Active" : "Inactive"}
                    </Badge>
                </div>
            </div>

            {/* AI Insight Section */}
            {!insight ? (
                <div className="flex flex-col items-center justify-center py-10 gap-3 rounded-lg bg-slate-800/30 border border-dashed border-slate-700 mb-6">
                    <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
                    <Body className="text-sm text-slate-400">
                        Analyzing grid conditions...
                    </Body>
                </div>
            ) : (
                <div className="space-y-5 mb-6">
                    {/* Summary */}
                    <div className="p-4 rounded-xl bg-slate-800/50">
                        <Body className="text-sm leading-relaxed">
                            {insight.summary}
                        </Body>
                    </div>

                    {/* Observations + Actions */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                        <div>
                            <div className="flex items-center gap-2 mb-3">
                                <Lightbulb className="w-4 h-4 text-blue-400" />
                                <Body className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                                    Key Observations
                                </Body>
                            </div>
                            <div className="space-y-2">
                                {insight.observations.map((obs, i) => (
                                    <div
                                        key={i}
                                        className="flex items-start gap-2.5 p-2.5 rounded-lg bg-slate-800/30"
                                    >
                                        <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-1.5 shrink-0" />
                                        <Body className="text-xs leading-relaxed">
                                            {obs}
                                        </Body>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div>
                            <div className="flex items-center gap-2 mb-3">
                                <AlertTriangle className="w-4 h-4 text-amber-400" />
                                <Body className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                                    Recommended Actions
                                </Body>
                            </div>
                            <div className="space-y-2">
                                {insight.actions.map((action, i) => (
                                    <div
                                        key={i}
                                        className="flex items-start gap-2.5 p-2.5 rounded-lg bg-amber-500/5 border border-amber-500/10"
                                    >
                                        <span className="text-xs font-bold text-amber-400 mt-0.5 shrink-0">
                                            {i + 1}.
                                        </span>
                                        <Body className="text-xs leading-relaxed">
                                            {action}
                                        </Body>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Cost + Carbon */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div className="flex items-start gap-2.5 p-3 rounded-lg bg-slate-800/30">
                            <DollarSign className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                            <Body className="text-xs leading-relaxed">
                                {insight.cost_insight}
                            </Body>
                        </div>
                        <div className="flex items-start gap-2.5 p-3 rounded-lg bg-slate-800/30">
                            <Leaf className="w-4 h-4 text-green-400 mt-0.5 shrink-0" />
                            <Body className="text-xs leading-relaxed">
                                {insight.carbon_insight}
                            </Body>
                        </div>
                    </div>
                </div>
            )}

            {/* Recent Anomalies */}
            <div className="mb-6">
                <div className="flex items-center gap-2 mb-3">
                    <AlertTriangle className="w-4 h-4 text-orange-400" />
                    <Label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                        Recent Anomalies
                    </Label>
                    {anomalies.length > 0 && (
                        <Badge variant="warning" className="ml-auto">
                            {anomalies.length}
                        </Badge>
                    )}
                </div>

                {recentAnomalies.length === 0 ? (
                    <div className="h-[80px] flex items-center justify-center rounded-lg bg-emerald-500/5 border border-emerald-500/10">
                        <div className="flex items-center gap-2">
                            <CheckCircle className="w-4 h-4 text-emerald-500/50" />
                            <Body className="text-xs text-emerald-500/70">
                                System stable -- no anomalies detected
                            </Body>
                        </div>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                        {recentAnomalies.map((anomaly, index) => (
                            <div
                                key={index}
                                className="p-3 rounded-lg bg-red-500/5 border border-red-500/10 hover:bg-red-500/10 transition-colors"
                            >
                                <div className="flex items-start justify-between mb-1">
                                    <div className="flex items-center gap-2">
                                        <XCircle className="w-3 h-3 text-red-400 shrink-0" />
                                        <Body className="text-xs font-bold text-red-400">
                                            {anomaly.device_id}
                                        </Body>
                                    </div>
                                    <Body className="text-xs font-mono text-red-400">
                                        {anomaly.current.toFixed(1)}A
                                    </Body>
                                </div>
                                <Body className="text-[11px] text-slate-400 leading-tight">
                                    {anomaly.alert}
                                </Body>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Device Performance Statistics */}
            {Object.keys(statistics).length > 0 && (
                <div className="pt-4 border-t border-slate-800">
                    <div className="flex items-center gap-2 mb-3">
                        <TrendingUp className="w-4 h-4 text-emerald-400" />
                        <Label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                            Device Performance
                        </Label>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                        {Object.entries(statistics).map(
                            ([deviceType, stats]) => (
                                <div
                                    key={deviceType}
                                    className="p-3 rounded-lg bg-slate-900/50 border border-slate-800"
                                >
                                    <div className="flex justify-between items-center mb-3">
                                        <Body className="text-xs font-bold capitalize text-slate-200">
                                            {deviceType}
                                        </Body>
                                        <Body className="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded text-slate-400">
                                            {stats.total_samples} samples
                                        </Body>
                                    </div>
                                    <div className="grid grid-cols-3 border-t border-slate-800/50 pt-2">
                                        <div className="text-center">
                                            <Body
                                                muted
                                                className="text-[10px]"
                                            >
                                                AVG
                                            </Body>
                                            <Body className="text-xs font-mono">
                                                {stats.avg_current.toFixed(1)}A
                                            </Body>
                                        </div>
                                        <div className="text-center border-x border-slate-800/50">
                                            <Body
                                                muted
                                                className="text-[10px]"
                                            >
                                                MAX
                                            </Body>
                                            <Body className="text-xs font-mono">
                                                {stats.max_current.toFixed(1)}A
                                            </Body>
                                        </div>
                                        <div className="text-center">
                                            <Body
                                                muted
                                                className="text-[10px]"
                                            >
                                                POWER
                                            </Body>
                                            <Body className="text-xs font-mono">
                                                {(
                                                    stats.avg_power / 1000
                                                ).toFixed(1)}
                                                kW
                                            </Body>
                                        </div>
                                    </div>
                                </div>
                            ),
                        )}
                    </div>
                </div>
            )}

            {/* Footer */}
            <div className="mt-6 pt-4 border-t border-slate-800 flex justify-center">
                <Body muted className="text-[10px] flex items-center gap-2">
                    <span
                        className={`w-1.5 h-1.5 rounded-full ${isActive ? "bg-emerald-500 animate-pulse" : "bg-slate-600"}`}
                    />
                    {isActive ? "Pathway Engine Active" : "Engine Standby"}
                </Body>
            </div>
        </Card>
    );
}
