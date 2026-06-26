"use client";

import * as React from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useWatchlistQuotesQuery } from "@/features/watchlists/hooks";
import { ListChecks, ArrowRight, TrendingUp, TrendingDown, Minus } from "lucide-react";
import type { WatchlistQuoteItem } from "@/features/watchlists/types";

interface WatchlistSnapshotProps {
  watchlistId: string | null;
  watchlistName: string;
}

function formatPrice(price: number | null | undefined): string {
  if (price == null) return "--";
  return price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function QuoteChange({ item }: { item: WatchlistQuoteItem }) {
  if (item.price == null || item.previous_close == null || item.error) {
    return <span className="text-xs text-muted-foreground">--</span>;
  }
  const change = item.price - item.previous_close;
  const pct = (change / item.previous_close) * 100;
  const isPositive = change >= 0;
  const color = isPositive ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400";
  const Icon = isPositive ? TrendingUp : TrendingDown;

  return (
    <span className={`text-xs font-medium tabular-nums ${color} flex items-center gap-0.5`}>
      <Icon className="h-3 w-3" />
      {isPositive ? "+" : ""}{change.toFixed(2)} ({(pct >= 0 ? "+" : "")}{pct.toFixed(2)}%)
    </span>
  );
}

export function WatchlistSnapshot({ watchlistId, watchlistName }: WatchlistSnapshotProps) {
  const { data: quotesData, isLoading } = useWatchlistQuotesQuery(watchlistId);

  const quotes = quotesData?.quotes ?? [];

  if (!watchlistId) {
    return null;
  }

  return (
    <Card className="transition-all hover:-translate-y-0.5 hover:shadow-md">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <ListChecks className="h-4 w-4 text-muted-foreground" />
          {watchlistName}
        </CardTitle>
        {quotes.length > 0 && (
          <Link href="/dashboard/watchlists">
            <Button variant="ghost" size="sm" className="text-xs gap-1">
              View all <ArrowRight className="h-3 w-3" />
            </Button>
          </Link>
        )}
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-10 w-full rounded-md" />
            ))}
          </div>
        ) : quotes.length === 0 ? (
          <p className="text-sm text-muted-foreground">No tickers in this watchlist.</p>
        ) : (
          <div className="space-y-1">
            {quotes.slice(0, 5).map((item) => (
              <div
                key={item.ticker}
                className="flex items-center justify-between p-2 rounded-md hover:bg-muted/50 transition-colors animate-fade-in"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <span className="text-sm font-mono font-medium">{item.ticker}</span>
                  {item.name && (
                    <span className="text-xs text-muted-foreground truncate hidden sm:inline max-w-[120px]">
                      {item.name}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <span className="text-sm font-medium tabular-nums">
                    {formatPrice(item.price)}
                  </span>
                  <QuoteChange item={item} />
                </div>
              </div>
            ))}
            {quotes.length > 5 && (
              <p className="text-xs text-muted-foreground text-center pt-1">
                +{quotes.length - 5} more tickers
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
