import { type ReactNode } from "react";

interface ValueProps {
    children: ReactNode;
    size?: "sm" | "md" | "lg" | "xl";
    className?: string;
}

export function Value({ children, size = "md", className = "" }: ValueProps) {
    const sizeStyles = {
        sm: "text-xl",
        md: "text-2xl",
        lg: "text-3xl",
        xl: "text-4xl",
    };

    return (
        <span className={`value-mono text-slate-100 font-semibold ${sizeStyles[size]} ${className}`}>
            {children}
        </span>
    );
}
