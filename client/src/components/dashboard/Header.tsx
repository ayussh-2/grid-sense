"use client";

import { Badge } from "@/components/ui";
import { Body } from "@/components/typography";
import { Clock } from "lucide-react";
import { useEffect, useState } from "react";

interface HeaderProps {
    systemStatus?: "normal" | "warning" | "critical";
    connected?: boolean;
}

export function Header({
    systemStatus = "normal",
    connected = false,
}: HeaderProps) {
    const [currentTime, setCurrentTime] = useState(new Date());

    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentTime(new Date());
        }, 1000);

        return () => clearInterval(timer);
    }, []);

    const statusVariant = {
        normal: "success" as const,
        warning: "warning" as const,
        critical: "critical" as const,
    };

    const statusText = {
        normal: "All Systems Operational",
        warning: "Warning Detected",
        critical: "Critical Alert",
    };

    return (
        <header className="sticky top-0 h-16 backdrop-blur-md bg-slate-950/80 border-b border-slate-800 flex items-center justify-between px-6 z-10">
            <div className="flex items-center gap-4">
                <Body className="text-slate-400">Grid Status:</Body>
                <Badge variant={statusVariant[systemStatus]}>
                    {statusText[systemStatus]}
                </Badge>
                <span
                    className={`inline-block w-2 h-2 rounded-full ${connected ? "bg-emerald-400" : "bg-red-400 animate-pulse"}`}
                    title={connected ? "WebSocket connected" : "Reconnecting..."}
                />
            </div>

            <div className="flex items-center gap-2 text-slate-400">
                <Clock className="w-4 h-4" />
                <Body muted className="font-mono text-xs">
                    {currentTime.toLocaleTimeString()}
                </Body>
            </div>
        </header>
    );
}
