import { Inter, JetBrains_Mono } from "next/font/google";

const inter = Inter({
    variable: "--font-inter",
    subsets: ["latin"],
});

const jetBrainsMono = JetBrains_Mono({
    variable: "--font-jetbrains-mono",
    subsets: ["latin"],
});

const fonts = ` ${inter.variable} ${jetBrainsMono.variable}`;

export default fonts;
