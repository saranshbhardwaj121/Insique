"use client";

import * as React from "react";
import { ThemeProvider } from "@/components/providers/theme-provider";
import { QueryProvider } from "@/components/providers/query-provider";
import { AuthProvider } from "@/features/auth/context";
import { TickerProvider } from "@/features/ticker/ticker-context";
import { Toaster } from "@/components/ui/sonner";

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <QueryProvider>
        <AuthProvider>
          <TickerProvider>
            {children}
            <Toaster />
          </TickerProvider>
        </AuthProvider>
      </QueryProvider>
    </ThemeProvider>
  );
}
