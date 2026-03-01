"use client";

import { Card, Badge } from "@/components/ui";
import { Heading, Body } from "@/components/typography";
import {
    Bot,
    AlertTriangle,
    CheckCircle,
    ShieldAlert,
    Lightbulb,
    DollarSign,
    Leaf,
    Loader2,
} from "lucide-react";
import type { LLMInsight } from "@/lib/api";

interface InsightPanelProps {
    insight: LLMInsight | null;
}

const SEVERITY_CONFIG = {
    normal: {
        badge: "success" as const,
        label: "Normal",
        border: "",
        icon: CheckCircle,
        iconColor: "text-emerald-400",
    },
    warning: {
        badge: "warning" as const,
        label: "Warning",
        border: "border-l-4 border-amber-500",
        icon: AlertTriangle,
        iconColor: "text-amber-400",
    },
    critical: {
        badge: "critical" as const,
        label: "Critical",
        border: "border-l-4 border-red-500",
        icon: ShieldAlert,
        iconColor: "text-red-400",
    },
};

function timeAgo(timestamp: number): string {
    const seconds = Math.floor(Date.now() / 1000 - timestamp);
    if (seconds < 5) return "just now";
    if (seconds < 60) return `${seconds}s ago`;
    return `${Math.floor(seconds / 60)}m ago`;
}

export function InsightPanel({ insight }: InsightPanelProps) {
    if (!insight) {
        return (
            <Card className="w-full">
                <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-blue-500/10">
                        <Bot className="w-5 h-5 text-blue-500" />
                    </div>
                    <div>
                        <Heading level={3}>GridSense AI</Heading>
                        <Body muted className="text-xs">
                            Powered by Gemini
                        </Body>
                    </div>
                </div>
                <div className="flex flex-col items-center justify-center py-12 gap-3">
                    <Loader2 className="w-6 h-6 text-blue-400 animate-spin" />
                    <Body className="text-sm text-slate-400">
                        Analyzing grid conditions...
                    </Body>
                    <Body muted className="text-xs">
                        First insight arrives in ~30 seconds
                    </Body>
                </div>
            </Card>
        );
    }

    const config = SEVERITY_CONFIG[insight.severity];
    const SeverityIcon = config.icon;

    return (
        <Card className={`w-full ${config.border}`}>
            {/* Header */}
            <div className="flex items-center justify-between mb-5">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-blue-500/10">
                        <Bot className="w-5 h-5 text-blue-500" />
                    </div>
                    <div>
                        <Heading level={3}>GridSense AI</Heading>
                        <Body muted className="text-xs">
                            Powered by Gemini -- updated{" "}
                            {timeAgo(insight.timestamp)}
                        </Body>
                    </div>
                </div>
                <Badge variant={config.badge}>
                    <SeverityIcon className="w-3 h-3 mr-1" />
                    {config.label}
                </Badge>
            </div>

            {/* Summary */}
            <div className="p-4 rounded-xl bg-slate-800/50 mb-5">
                <Body className="text-sm leading-relaxed">
                    {insight.summary}
                </Body>
            </div>

            {/* Observations + Actions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-5">
                {/* Observations */}
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

                {/* Actions */}
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

            {/* Cost + Carbon footer */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-4 border-t border-slate-800">
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
        </Card>
    );
}
