import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "fuckLLM - Open Source AI Provenance & Watermark Removal System",
  description: "Production-ready system targeting statistical LLM text watermarks, visible/invisible image watermarks, and video metadata.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-cyber-dark text-gray-100 selection:bg-purple-500/30 selection:text-purple-200">
        {children}
      </body>
    </html>
  );
}
