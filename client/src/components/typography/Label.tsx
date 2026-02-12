import { type ReactNode } from "react";

interface LabelProps {
    children: ReactNode;
    className?: string;
}

export function Label({ children, className = "" }: LabelProps) {
    return (
        <div className={`text-label ${className}`}>
            {children}
        </div>
    );
}
