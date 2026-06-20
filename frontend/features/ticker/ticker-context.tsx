"use client";

import * as React from "react";
import { useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/lib/api/query-keys";
import { useRecentTickers } from "./use-recent-tickers";
import type { TickerContextValue } from "./types";

const TickerContext = React.createContext<TickerContextValue | undefined>(undefined);

export function TickerProvider({ children }: { children: React.ReactNode }) {
  const [activeTicker, setActiveTickerState] = React.useState<string | null>(null);
  const { recentTickers, pushRecentTicker, clearRecentTickers } = useRecentTickers();
  const queryClient = useQueryClient();

  const setActiveTicker = React.useCallback(
    (ticker: string | null) => {
      setActiveTickerState(ticker);
      if (ticker) {
        pushRecentTicker(ticker);
        queryClient.prefetchQuery({
          queryKey: queryKeys.signals.ticker(ticker),
          staleTime: 30_000,
        });
        queryClient.prefetchQuery({
          queryKey: queryKeys.marketData.quote(ticker),
          staleTime: 30_000,
        });
        queryClient.prefetchQuery({
          queryKey: queryKeys.analytics.rsi(ticker),
          staleTime: 30_000,
        });
      }
    },
    [pushRecentTicker, queryClient]
  );

  const value = React.useMemo<TickerContextValue>(
    () => ({
      activeTicker,
      setActiveTicker,
      recentTickers,
      clearRecentTickers,
    }),
    [activeTicker, setActiveTicker, recentTickers, clearRecentTickers]
  );

  return React.createElement(TickerContext.Provider, { value }, children);
}

export function useTickerContext(): TickerContextValue {
  const context = React.useContext(TickerContext);
  if (!context) {
    throw new Error("useTickerContext must be used within a TickerProvider");
  }
  return context;
}
