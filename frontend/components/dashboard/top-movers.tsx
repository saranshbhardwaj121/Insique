"use client";

import * as React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useWatchlistQuotesQuery } from "@/features/watchlists/hooks";
import { TrendingUp, TrendingDown, ArrowUpRight, ArrowDownRight } from "lucide-react";
import type { WatchlistQuoteItem } from "@/features/watchlists/types";

interface TopMoversProps {
  watchlistId: string | null;
}

interface Mover {
  ticker: string;
  changePercent: number;
  price: number;
}

function computeMovers(quotes: WatchlistQuoteItem[]): { gainers: Mover[]; losers: Mover[] } {
  const withChange = quotes.filter(
    (q) => q.price != null && q.previous_close != null && !q.error
  );

  const sorted = withChange
    .map((q) => ({
      ticker: q.ticker,
      changePercent: ((q.price! - q.previous_close!) / q.previous_close!) * 100,
      price: q.price!,
    }))
    .sort((a, b) => b.changePercent - a.changePercent);

  return {
    gainers: sorted.filter((m) => m.changePercent > 0).slice(0, 3),
    losers: sorted.filter((m) => m.changePercent < 0).reverse().slice(0, 3),
  };
}

function formatPrice(price: number): string {
  return price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export function TopMovers({ watchlistId }: TopMoversProps) {
  const { data: quotesData, isLoading, isError } = useWatchlistQuotesQuery(watchlistId);
  const { gainers, losers } = React.useMemo(
    () => computeMovers(quotesData?.quotes ?? []),
    [quotesData?.quotes]
  );

  if (!watchlistId) {
    return null;
  }

  const hasMovers = gainers.length > 0 || losers.length > 0;

  return (
    <Card className="transition-all hover:-translate-y-0.5 hover:shadow-md">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">Top Movers</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {isLoading ? (
          <div className="space-y-2">
            <Skeleton className="h-10 w-full rounded-md" />
            <Skeleton className="h-10 w-full rounded-md" />
          </div>
        ) : isError ? (
          <p className="text-sm text-muted-foreground">Failed to load movers</p>
        ) : !hasMovers ? (
          <p className="text-sm text-muted-foreground">No movers data available.</p>
        ) : (
          <>
            {gainers.length > 0 && (
              <div>
                <p className="text-xs font-medium text-green-600 dark:text-green-400 flex items-center gap-1 mb-1">
                  <TrendingUp className="h-3 w-3" />
                  Top Gainers
                </p>
                <div className="space-y-1">
                  {gainers.map((m, i) => (
                    <div
                      key={m.ticker}
                      className={`flex items-center justify-between p-1.5 rounded-md animate-fade-in ${i > 0 ? "" : "bg-green-50 dark:bg-green-950/30"}`}
                    >
                      <div className="flex items-center gap-2">
                        <ArrowUpRight className="h-3 w-3 text-green-600 dark:text-green-400" />
                        <span className="text-sm font-mono font-medium">{m.ticker}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-muted-foreground tabular-nums">
                          {formatPrice(m.price)}
                        </span>
                        <span className="text-xs font-medium tabular-nums text-green-600 dark:text-green-400">
                          +{m.changePercent.toFixed(2)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {losers.length > 0 && (
              <div>
                <p className="text-xs font-medium text-red-600 dark:text-red-400 flex items-center gap-1 mb-1">
                  <TrendingDown className="h-3 w-3" />
                  Top Losers
                </p>
                <div className="space-y-1">
                  {losers.map((m, i) => (
                    <div
                      key={m.ticker}
                      className={`flex items-center justify-between p-1.5 rounded-md animate-fade-in ${i > 0 ? "" : "bg-red-50 dark:bg-red-950/30"}`}
                    >
                      <div className="flex items-center gap-2">
                        <ArrowDownRight className="h-3 w-3 text-red-600 dark:text-red-400" />
                        <span className="text-sm font-mono font-medium">{m.ticker}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-muted-foreground tabular-nums">
                          {formatPrice(m.price)}
                        </span>
                        <span className="text-xs font-medium tabular-nums text-red-600 dark:text-red-400">
                          {m.changePercent.toFixed(2)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
