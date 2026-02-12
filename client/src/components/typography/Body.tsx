import { type ReactNode } from "react";

interface BodyProps {
    children: ReactNode;
    muted?: boolean;
    className?: string;
}

export function Body({ children, muted = false, className = "" }: BodyProps) {
    const colorClass = muted ? "text-slate-400" : "text-slate-100";
    
    return (
        <p className={`text-sm ${colorClass} ${className}`}>
            {children}
        </p>
    );
}
