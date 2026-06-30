import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { AppProviders } from "@/components/providers/app-providers";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Insique — Decide with evidence",
  description:
    "Market intelligence platform. Real-time analytics, technical signals, and evidence-based insights — so every decision has a reason.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} overflow-x-hidden`}>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
