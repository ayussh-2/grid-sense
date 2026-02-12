import { type ReactNode } from "react";

interface HeadingProps {
    children: ReactNode;
    level?: 1 | 2 | 3 | 4;
    className?: string;
}

export function Heading({ children, level = 1, className = "" }: HeadingProps) {
    const baseStyles = "font-semibold text-slate-100";
    
    const sizeStyles = {
        1: "text-3xl",
        2: "text-2xl",
        3: "text-xl",
        4: "text-lg",
    };

    const Component = `h${level}` as keyof JSX.IntrinsicElements;

    return (
        <Component className={`${baseStyles} ${sizeStyles[level]} ${className}`}>
            {children}
        </Component>
    );
}
