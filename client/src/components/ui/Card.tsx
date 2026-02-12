import { type ReactNode } from "react";

interface CardProps {
    children: ReactNode;
    className?: string;
    critical?: boolean;
}

export function Card({ children, className = "", critical = false }: CardProps) {
    const criticalStyles = critical ? "border-red-500" : "";
    
    return (
        <div className={`card-base ${criticalStyles} ${className}`}>
            {children}
        </div>
    );
}
