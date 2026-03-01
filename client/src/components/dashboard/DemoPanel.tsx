"use client";

import { useState } from "react";
import { Card, Badge, Button } from "@/components/ui";
import { Heading, Body } from "@/components/typography";
import { apiClient } from "@/lib/api";
import {
    Play,
    RotateCcw,
    Zap,
    AlertTriangle,
    Activity,
    Gauge,
    ChevronDown,
    ChevronUp,
} from "lucide-react";

const SCENARIOS = [
    {
        id: "surge",
        name: "Surge All",
        icon: Zap,
        color: "text-red-400",
        bg: "bg-red-500/10 border-red-500/20 hover:bg-red-500/20",
        badge: "critical" as const,
        description: "All devices on + motor fault (110A sustained)",
        showcases: [
            "Pathway anomaly detection",
            "Fault alerts",
            "LLM recommendations",
            "Critical status",
        ],
    },
    {
        id: "motor_inrush",
        name: "Motor Inrush",
        icon: Activity,
        color: "text-amber-400",
        bg: "bg-amber-500/10 border-amber-500/20 hover:bg-amber-500/20",
        badge: "warning" as const,
        description: "120A peak inrush, decaying to 45A over 3.5s",
        showcases: [
            "Transient spike detection",
            "Real-time chart spike",
            "Inrush profiling",
        ],
    },
    {
        id: "high_load",
        name: "High Load",
        icon: Gauge,
        color: "text-orange-400",
        bg: "bg-orange-500/10 border-orange-500/20 hover:bg-orange-500/20",
        badge: "warning" as const,
        description: "Motor + HVAC + Compressor (~90A warning zone)",
        showcases: [
            "Warning status",
            "LLM cost optimization",
            "Device statistics",
        ],
    },
    {
        id: "normal",
        name: "Normal Ops",
        icon: Play,
        color: "text-emerald-400",
        bg: "bg-emerald-500/10 border-emerald-500/20 hover:bg-emerald-500/20",
        badge: "success" as const,
        description: "HVAC + Lighting only (~22A stable)",
        showcases: [
            "Normal status",
            "Optimal grid recommendations",
            "Steady baselines",
        ],
    },
    {
        id: "fault",
        name: "Inject Fault",
        icon: AlertTriangle,
        color: "text-red-400",
        bg: "bg-red-500/10 border-red-500/20 hover:bg-red-500/20",
        badge: "critical" as const,
        description: "Locked rotor fault on motor (110A sustained)",
        showcases: ["Fault detection", "Anomaly alerts", "Critical status"],
    },
    {
        id: "reset",
        name: "Reset",
        icon: RotateCcw,
        color: "text-slate-400",
        bg: "bg-slate-500/10 border-slate-500/20 hover:bg-slate-500/20",
        badge: "default" as const,
        description: "All devices off, return to idle",
        showcases: ["Normal status", "Zero baseline"],
    },
] as const;

export function DemoPanel() {
    const [activeScenario, setActiveScenario] = useState<string | null>(null);
    const [loading, setLoading] = useState<string | null>(null);
    const [expanded, setExpanded] = useState(true);

    const runScenario = async (scenarioId: string) => {
        setLoading(scenarioId);
        try {
            await apiClient.runDemoScenario(scenarioId);
            setActiveScenario(scenarioId === "reset" ? null : scenarioId);
        } catch (error) {
            console.error("Failed to run scenario:", error);
        } finally {
            setLoading(null);
        }
    };

    return (
        <Card className="w-full border-dashed border-blue-500/30">
            <button
                type="button"
                className="w-full flex items-center justify-between cursor-pointer"
                onClick={() => setExpanded(!expanded)}
            >
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-blue-500/10">
                        <Play className="w-5 h-5 text-blue-500" />
                    </div>
                    <div className="text-left">
                        <Heading level={3}>Demo Scenarios</Heading>
                        <Body muted className="text-xs">
                            One-click presets to showcase each system aspect
                        </Body>
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    {activeScenario && (
                        <Badge
                            variant={
                                SCENARIOS.find((s) => s.id === activeScenario)
                                    ?.badge ?? "default"
                            }
                        >
                            {SCENARIOS.find((s) => s.id === activeScenario)
                                ?.name ?? ""}
                        </Badge>
                    )}
                    {expanded ? (
                        <ChevronUp className="w-4 h-4 text-slate-400" />
                    ) : (
                        <ChevronDown className="w-4 h-4 text-slate-400" />
                    )}
                </div>
            </button>

            {expanded && (
                <div className="mt-5 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                    {SCENARIOS.map((scenario) => {
                        const Icon = scenario.icon;
                        const isActive = activeScenario === scenario.id;
                        const isLoading = loading === scenario.id;

                        return (
                            <button
                                key={scenario.id}
                                type="button"
                                onClick={() => runScenario(scenario.id)}
                                disabled={isLoading}
                                className={`group relative p-4 rounded-xl border transition-all text-left cursor-pointer
                                    ${scenario.bg}
                                    ${isActive ? "ring-1 ring-blue-500/50" : ""}
                                    ${isLoading ? "opacity-60" : ""}
                                `}
                            >
                                <div className="flex items-center gap-2 mb-2">
                                    <Icon
                                        className={`w-4 h-4 ${scenario.color} ${isLoading ? "animate-spin" : ""}`}
                                    />
                                    <Body
                                        className={`text-xs font-bold ${scenario.color}`}
                                    >
                                        {scenario.name}
                                    </Body>
                                </div>
                                <Body className="text-[10px] text-slate-400 leading-tight">
                                    {scenario.description}
                                </Body>
                                <div className="mt-2 flex flex-wrap gap-1">
                                    {scenario.showcases
                                        .slice(0, 2)
                                        .map((tag) => (
                                            <span
                                                key={tag}
                                                className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800/60 text-slate-500"
                                            >
                                                {tag}
                                            </span>
                                        ))}
                                </div>
                            </button>
                        );
                    })}
                </div>
            )}
        </Card>
    );
}
