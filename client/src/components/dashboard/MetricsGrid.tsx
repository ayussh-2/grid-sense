"use client";

import { MetricCard } from "./MetricCard";
import { Zap, Activity, Gauge, DollarSign, Leaf, TrendingUp } from "lucide-react";
import type { GridContext } from "@/lib/api";

interface MetricsGridProps {
    totalCurrent: number;
    totalPower: number;
    avgVoltage: number;
    estimatedCost: number;
    criticalCurrent?: boolean;
    gridContext?: GridContext | null;
}

export function MetricsGrid({ 
    totalCurrent, 
    totalPower, 
    avgVoltage, 
    estimatedCost,
    criticalCurrent = false,
    gridContext = null
}: MetricsGridProps) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Primary Metrics */}
            <MetricCard
                label="Total Current"
                value={totalCurrent}
                unit="A"
                icon={Zap}
                critical={criticalCurrent}
                decimals={2}
            />
            <MetricCard
                label="Total Power"
                value={totalPower}
                unit="W"
                icon={Activity}
                decimals={0}
            />
            <MetricCard
                label="Average Voltage"
                value={avgVoltage}
                unit="V"
                icon={Gauge}
                decimals={1}
            />
            
            {/* Grid Context Metrics */}
            <MetricCard
                label="Carbon Intensity"
                value={gridContext?.carbon_intensity ?? 0}
                unit="gCO₂/kWh"
                icon={Leaf}
                decimals={0}
                critical={gridContext?.carbon_level === "HIGH"}
            />
            <MetricCard
                label="Grid Renewable"
                value={gridContext?.grid_renewable_percentage ?? 0}
                unit="%"
                icon={TrendingUp}
                decimals={1}
            />
            <MetricCard
                label="Electricity Price"
                value={gridContext?.electricity_price ?? 0}
                unit="$/kWh"
                icon={DollarSign}
                decimals={4}
                critical={gridContext?.pricing_tier === "HIGH"}
            />
        </div>
    );
}
