import type { Metadata } from "next";
import fonts from "@/fonts";
import "./globals.css";

export const metadata: Metadata = {
    title: "GRID SENSE AI",
    description:
        "Grid Sense AI is a platform for monitoring and analyzing grid power systems.",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body className={`${fonts} antialiased`}>{children}</body>
        </html>
    );
}
