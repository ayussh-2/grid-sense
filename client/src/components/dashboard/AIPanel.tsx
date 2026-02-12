"use client";

import { Card } from "@/components/ui";
import { Heading, Body } from "@/components/typography";
import { Bot, AlertTriangle, CheckCircle, Info } from "lucide-react";
import type { GridContext } from "@/lib/api";

interface AIPanelProps {
    critical?: boolean;
    insights?: string[];
    gridContext?: GridContext | null;
    totalCurrent?: number;
}

export function AIPanel({ 
    critical = false, 
    insights = [], 
    gridContext = null,
    totalCurrent = 0 
}: AIPanelProps) {
    const defaultInsights = [
        "All systems operating within normal parameters",
        "Power consumption is optimal",
        "No anomalies detected in the last hour",
    ];

    const criticalInsights = [
        "Critical current threshold exceeded",
        "Immediate attention required for fault condition",
        "Consider reducing load or shutting down non-essential devices",
    ];

    // Generate context-aware insights
    const contextInsights: string[] = [];
    
    if (gridContext) {
        // Carbon awareness
        if (gridContext.carbon_level === "HIGH") {
            contextInsights.push(
                `⚠️ High carbon intensity (${Math.round(gridContext.carbon_intensity)} gCO₂/kWh). Consider deferring non-critical loads.`
            );
        } else if (gridContext.carbon_level === "LOW") {
            contextInsights.push(
                `✓ Low carbon intensity period. Good time to run heavy equipment.`
            );
        }

        // Pricing awareness
        if (gridContext.pricing_tier === "HIGH") {
            contextInsights.push(
                `💰 Peak pricing period ($${gridContext.electricity_price.toFixed(4)}/kWh). Running at ${Math.round(totalCurrent)}A costs ~$${((totalCurrent * 230 / 1000) * gridContext.electricity_price).toFixed(2)}/hr.`
            );
        } else if (gridContext.pricing_tier === "LOW") {
            contextInsights.push(
                `✓ Off-peak pricing. Cost-effective time to operate heavy loads.`
            );
        }

        // Renewable percentage
        if (gridContext.grid_renewable_percentage > 60) {
            contextInsights.push(
                `🌱 Grid is ${gridContext.grid_renewable_percentage.toFixed(1)}% renewable. Clean energy period!`
            );
        }
    }

    const displayInsights = insights.length > 0 
        ? insights 
        : (critical ? criticalInsights : [...contextInsights, ...defaultInsights].slice(0, 3));

    return (
        <Card className={critical ? "border-l-4 border-red-500" : ""}>
            <div className="mb-4 flex items-center gap-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    critical ? "bg-red-500/10" : "bg-blue-500/10"
                }`}>
                    <Bot className={`w-5 h-5 ${critical ? "text-red-500" : "text-blue-500"}`} />
                </div>
                <Heading level={3}>AI Insights</Heading>
            </div>

            <div className="space-y-3">
                {displayInsights.map((insight, index) => (
                    <div key={index} className="flex items-start gap-3 p-3 rounded-lg bg-slate-800/50">
                        {critical ? (
                            <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                        ) : (
                            <CheckCircle className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                        )}
                        <Body className="text-xs flex-1">
                            {insight}
                        </Body>
                    </div>
                ))}
            </div>

            <div className="mt-4 pt-4 border-t border-slate-800">
                <Body muted className="text-xs text-center">
                    AI Analysis • Updated in real-time
                </Body>
            </div>
        </Card>
    );
}
