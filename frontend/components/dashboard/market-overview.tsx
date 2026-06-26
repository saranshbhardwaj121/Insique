"use client";

import * as React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useQuoteQuery } from "@/features/market-data/hooks";
import { TrendingUp, TrendingDown, Minus, Clock } from "lucide-react";
import type { Quote } from "@/features/market-data/types";

function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

function getMarketStatus(quote: Quote | undefined): {
  label: string;
  color: string;
  pulse: boolean;
} {
  if (!quote?.price) {
    return { label: "Market data unavailable", color: "text-muted-foreground", pulse: false };
  }

  const change = quote.price && quote.previous_close
    ? ((quote.price - quote.previous_close) / quote.previous_close) * 100
    : 0;

  if (change > 0.5) return { label: "Market is Bullish", color: "text-green-600 dark:text-green-400", pulse: false };
  if (change > 0) return { label: "Market is Slightly Up", color: "text-green-500 dark:text-green-400", pulse: false };
  if (change < -0.5) return { label: "Market is Bearish", color: "text-red-600 dark:text-red-400", pulse: false };
  if (change < 0) return { label: "Market is Slightly Down", color: "text-red-500 dark:text-red-400", pulse: false };

  return { label: "Market is Neutral", color: "text-muted-foreground", pulse: false };
}

function getTimeAgo(dateStr: string | null | undefined): string {
  if (!dateStr) return "";
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "Just now";
  if (mins === 1) return "1 min ago";
  return `${mins} min ago`;
}

function formatPrice(price: number | null | undefined): string {
  if (price == null) return "--";
  return price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatChange(quote: Quote): { text: string; color: string; icon: React.ElementType } {
  if (quote.price == null || quote.previous_close == null) {
    return { text: "--", color: "text-muted-foreground", icon: Minus };
  }
  const change = quote.price - quote.previous_close;
  const pct = (change / quote.previous_close) * 100;
  const color = change > 0
    ? "text-green-600 dark:text-green-400"
    : change < 0
    ? "text-red-600 dark:text-red-400"
    : "text-muted-foreground";
  const Icon = change > 0 ? TrendingUp : change < 0 ? TrendingDown : Minus;
  return {
    text: `${change >= 0 ? "+" : ""}${change.toFixed(2)} (${pct >= 0 ? "+" : ""}${pct.toFixed(2)}%)`,
    color,
    icon: Icon,
  };
}

export function MarketOverview() {
  const { data: quote, isLoading } = useQuoteQuery("^NSEI");
  const status = getMarketStatus(quote);
  const change = quote ? formatChange(quote) : null;
  const greeting = getGreeting();

  return (
    <Card className="transition-all hover:-translate-y-0.5 hover:shadow-md">
      <CardContent className="py-5">
        {isLoading ? (
          <div className="space-y-3">
            <Skeleton className="h-5 w-48" />
            <Skeleton className="h-4 w-36" />
            <Skeleton className="h-7 w-40" />
          </div>
        ) : (
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">{greeting}</p>
              <div className="flex items-center gap-2">
                <span className={`text-lg font-semibold ${status.color}`}>
                  {status.label}
                </span>
              </div>
              <div className="flex items-center gap-3 text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  Updated {getTimeAgo(quote?.fetched_at)}
                </span>
              </div>
            </div>
            {quote && change && (
              <div className="text-right">
                <p className="text-xl font-bold tabular-nums">
                  {formatPrice(quote.price)}
                </p>
                {quote.name && (
                  <p className="text-xs text-muted-foreground">{quote.name}</p>
                )}
                <p className={`text-sm font-medium tabular-nums ${change.color}`}>
                  <change.icon className="h-3.5 w-3.5 inline mr-0.5" />
                  {change.text}
                </p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
