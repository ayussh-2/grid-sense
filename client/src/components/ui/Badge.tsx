import { type ReactNode } from "react";

type BadgeVariant = "success" | "warning" | "critical" | "default";

interface BadgeProps {
    children: ReactNode;
    variant?: BadgeVariant;
    className?: string;
}

export function Badge({ children, variant = "default", className = "" }: BadgeProps) {
    const variantStyles = {
        success: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
        warning: "bg-amber-500/10 text-amber-400 border-amber-500/20",
        critical: "bg-red-500/10 text-red-400 border-red-500/20",
        default: "bg-slate-500/10 text-slate-400 border-slate-500/20",
    };

    return (
        <span className={`inline-flex items-center px-3 py-1 text-xs font-medium rounded-full border ${variantStyles[variant]} ${className}`}>
            {children}
        </span>
    );
}
