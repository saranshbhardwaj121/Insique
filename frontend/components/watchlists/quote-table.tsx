"use client";

import * as React from "react";
import { AlertCircle, RefreshCw, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { TickerActions } from "@/components/shared/ticker-actions";
import { useWatchlistQuotesQuery } from "@/features/watchlists/hooks";
import type { WatchlistQuoteItem } from "@/features/watchlists/types";

interface QuoteTableProps {
  watchlistId: string;
}

function formatPrice(value: number | null | undefined): string {
  if (value == null) return "--";
  return value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatVolume(value: number | null | undefined): string {
  if (value == null) return "--";
  if (value >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(1)}B`;
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return value.toString();
}

function QuoteTableSkeleton() {
  return (
    <div className="space-y-2">
      {Array.from({ length: 3 }).map((_, i) => (
        <Skeleton key={i} className="h-12 w-full rounded-lg" />
      ))}
    </div>
  );
}

function QuoteRowDesktop({ quote }: { quote: WatchlistQuoteItem }) {
  if (quote.error) {
    return (
      <tr className="border-b">
        <td className="py-2.5 px-3">
          <span className="font-medium">{quote.ticker}</span>
        </td>
        <td colSpan={6} className="py-2.5 px-3">
          <span className="text-sm text-muted-foreground flex items-center gap-1.5">
            <AlertCircle className="h-3.5 w-3.5 text-destructive" />
            {quote.error}
          </span>
        </td>
        <td className="py-2.5 px-3">
          <TickerActions ticker={quote.ticker} />
        </td>
      </tr>
    );
  }

  const change = quote.price != null && quote.previous_close != null
    ? quote.price - quote.previous_close
    : null;
  const changePercent = change != null && quote.previous_close != null && quote.previous_close !== 0
    ? (change / quote.previous_close) * 100
    : null;

  return (
    <tr className="border-b hover:bg-muted/50 transition-colors">
      <td className="py-2.5 px-3">
        <div>
          <span className="font-medium">{quote.ticker}</span>
          {quote.name && (
            <span className="ml-1.5 text-xs text-muted-foreground hidden lg:inline">
              {quote.name.length > 20 ? `${quote.name.slice(0, 20)}...` : quote.name}
            </span>
          )}
        </div>
      </td>
      <td className="py-2.5 px-3 text-right">
        {quote.price != null ? (
          <span className="font-medium tabular-nums">
            {quote.currency === "INR" ? "₹" : "$"}{formatPrice(quote.price)}
          </span>
        ) : (
          <span className="text-muted-foreground">--</span>
        )}
      </td>
      <td className="py-2.5 px-3 text-right tabular-nums">
        {change != null ? (
          <span className={change >= 0 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}>
            {change >= 0 ? "+" : ""}{formatPrice(change)}
          </span>
        ) : (
          <span className="text-muted-foreground">--</span>
        )}
      </td>
      <td className="py-2.5 px-3 text-right tabular-nums">
        {changePercent != null ? (
          <span className={changePercent >= 0 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}>
            {changePercent >= 0 ? "+" : ""}{changePercent.toFixed(2)}%
          </span>
        ) : (
          <span className="text-muted-foreground">--</span>
        )}
      </td>
      <td className="py-2.5 px-3 text-right hidden md:table-cell tabular-nums text-sm text-muted-foreground">
        {quote.day_low != null && quote.day_high != null
          ? `${formatPrice(quote.day_low)} - ${formatPrice(quote.day_high)}`
          : "--"}
      </td>
      <td className="py-2.5 px-3 text-right hidden lg:table-cell tabular-nums text-sm text-muted-foreground">
        {formatVolume(quote.volume)}
      </td>
      <td className="py-2.5 px-3 hidden lg:table-cell">
        {quote.exchange && (
          <Badge variant="outline" className="text-xs font-normal">
            {quote.exchange}
          </Badge>
        )}
      </td>
      <td className="py-2.5 px-3">
        <TickerActions ticker={quote.ticker} />
      </td>
    </tr>
  );
}

function QuoteCardMobile({ quote }: { quote: WatchlistQuoteItem }) {
  if (quote.error) {
    return (
      <div className="rounded-lg border p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <span className="font-medium">{quote.ticker}</span>
            <AlertCircle className="h-3.5 w-3.5 text-destructive" />
          </div>
          <TickerActions ticker={quote.ticker} />
        </div>
        <p className="text-xs text-muted-foreground mt-1">{quote.error}</p>
      </div>
    );
  }

  const change = quote.price != null && quote.previous_close != null
    ? quote.price - quote.previous_close
    : null;
  const changePercent = change != null && quote.previous_close != null && quote.previous_close !== 0
    ? (change / quote.previous_close) * 100
    : null;
  const isUp = change != null && change >= 0;

  return (
    <div className="rounded-lg border p-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 min-w-0">
          <span className="font-medium">{quote.ticker}</span>
          {quote.name && (
            <span className="text-xs text-muted-foreground truncate">{quote.name}</span>
          )}
        </div>
        <div className="flex items-center gap-1">
          <Badge variant="outline" className="text-xs">{quote.exchange || "--"}</Badge>
          <TickerActions ticker={quote.ticker} />
        </div>
      </div>
      <div className="flex items-baseline justify-between mt-2">
        <span className="text-lg font-semibold tabular-nums">
          {quote.price != null
            ? `${quote.currency === "INR" ? "₹" : "$"}${formatPrice(quote.price)}`
            : "--"}
        </span>
        {change != null && (
          <span className={`text-sm font-medium tabular-nums ${isUp ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>
            {isUp ? "+" : ""}{formatPrice(change)} ({isUp ? "+" : ""}{changePercent?.toFixed(2)}%)
          </span>
        )}
      </div>
      <div className="flex justify-between text-xs text-muted-foreground mt-1.5">
        <span>Day: {quote.day_low != null ? formatPrice(quote.day_low) : "--"} - {quote.day_high != null ? formatPrice(quote.day_high) : "--"}</span>
        <span>Vol: {formatVolume(quote.volume)}</span>
      </div>
    </div>
  );
}

export function QuoteTable({ watchlistId }: QuoteTableProps) {
  const { data, isLoading, isError, error, refetch, isFetching } = useWatchlistQuotesQuery(watchlistId);

  if (isLoading) {
    return <QuoteTableSkeleton />;
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <AlertCircle className="h-8 w-8 text-destructive mb-2" />
        <p className="text-sm text-muted-foreground mb-2">
          {error instanceof Error ? error.message : "Failed to load quotes"}
        </p>
        <Button variant="outline" size="sm" onClick={() => refetch()}>
          <RefreshCw className="mr-1.5 h-3.5 w-3.5" />
          Retry
        </Button>
      </div>
    );
  }

  const quotes = data?.quotes ?? [];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">
          {data?.fetched_at
            ? `Updated ${new Date(data.fetched_at).toLocaleTimeString()}`
            : ""}
        </p>
        <Button variant="ghost" size="sm" onClick={() => refetch()} disabled={isFetching}>
          <RefreshCw className={`mr-1.5 h-3.5 w-3.5 ${isFetching ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {quotes.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <p className="text-sm text-muted-foreground">No quote data available</p>
        </div>
      ) : (
        <>
          <div className="hidden sm:block overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-muted-foreground text-xs uppercase tracking-wider">
                  <th className="text-left py-2 px-3 font-medium">Ticker</th>
                  <th className="text-right py-2 px-3 font-medium">Price</th>
                  <th className="text-right py-2 px-3 font-medium">Change</th>
                  <th className="text-right py-2 px-3 font-medium">Change%</th>
                  <th className="text-right py-2 px-3 font-medium hidden md:table-cell">Day Range</th>
                  <th className="text-right py-2 px-3 font-medium hidden lg:table-cell">Volume</th>
                  <th className="py-2 px-3 font-medium hidden lg:table-cell">Exch</th>
                  <th className="py-2 px-3 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {quotes.map((quote) => (
                  <QuoteRowDesktop key={quote.ticker} quote={quote} />
                ))}
              </tbody>
            </table>
          </div>

          <div className="sm:hidden space-y-2">
            {quotes.map((quote) => (
              <QuoteCardMobile key={quote.ticker} quote={quote} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
