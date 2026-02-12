"use client";

import { LayoutDashboard, BarChart3, Settings, Zap } from "lucide-react";
import { Heading } from "@/components/typography";

const navItems = [
    { icon: LayoutDashboard, label: "Dashboard", href: "/", active: true },
    { icon: BarChart3, label: "Analytics", href: "/analytics", active: false },
    { icon: Settings, label: "Settings", href: "/settings", active: false },
];

export function Sidebar() {
    return (
        <aside className="fixed left-0 top-0 h-screen w-64 bg-slate-950 border-r border-slate-800 flex flex-col">
            {/* Logo Section */}
            <div className="h-16 flex items-center gap-3 px-6 border-b border-slate-800">
                <div className="w-8 h-8 bg-blue-500/10 rounded-lg flex items-center justify-center">
                    <Zap className="w-5 h-5 text-blue-500" />
                </div>
                <Heading level={3} className="text-lg">
                    GridSense AI
                </Heading>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-4">
                <ul className="space-y-2">
                    {navItems.map((item) => (
                        <li key={item.label}>
                            <a
                                href={item.href}
                                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                                    item.active
                                        ? "bg-slate-800 text-slate-100"
                                        : "text-slate-400 hover:text-slate-100 hover:bg-slate-900"
                                }`}
                            >
                                <item.icon className="w-5 h-5" />
                                <span className="text-sm font-medium">{item.label}</span>
                            </a>
                        </li>
                    ))}
                </ul>
            </nav>

            {/* Footer */}
            <div className="p-4 border-t border-slate-800">
                <div className="text-xs text-slate-500 text-center">
                    v1.0.0 • Real-time Monitoring
                </div>
            </div>
        </aside>
    );
}
