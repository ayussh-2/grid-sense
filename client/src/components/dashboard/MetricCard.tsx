import { Card } from "@/components/ui";
import { Label, Value } from "@/components/typography";
import { type LucideIcon } from "lucide-react";

interface MetricCardProps {
    label: string;
    value: number;
    unit: string;
    icon?: LucideIcon;
    critical?: boolean;
    trend?: "up" | "down" | "stable";
    decimals?: number;
}

export function MetricCard({ 
    label, 
    value, 
    unit, 
    icon: Icon,
    critical = false,
    decimals = 1 
}: MetricCardProps) {
    return (
        <Card critical={critical}>
            <div className="flex items-start justify-between">
                <div className="flex-1">
                    <Label>{label}</Label>
                    <div className="mt-2 flex items-baseline gap-2">
                        <Value size="lg">
                            {value.toFixed(decimals)}
                        </Value>
                        <span className="text-sm text-slate-500">{unit}</span>
                    </div>
                </div>
                {Icon && (
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        critical ? "bg-red-500/10" : "bg-slate-800"
                    }`}>
                        <Icon className={`w-5 h-5 ${critical ? "text-red-500" : "text-slate-400"}`} />
                    </div>
                )}
            </div>
        </Card>
    );
}
