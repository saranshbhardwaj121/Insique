"use client";

import * as React from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useWatchlistSignalsQuery } from "@/features/signals/hooks";
import { Signal, ArrowRight, TrendingUp, TrendingDown, Minus } from "lucide-react";
import type { WatchlistSignalItem } from "@/features/signals/types";

interface LatestSignalsProps {
  watchlistId: string | null;
}

function SignalBadge({ rating }: { rating: string }) {
  if (rating === "BUY") {
    return (
      <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100 border-green-200 dark:border-green-800 text-xs">
        <TrendingUp className="h-3 w-3 mr-0.5" />
        BUY
      </Badge>
    );
  }
  if (rating === "SELL") {
    return (
      <Badge className="bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100 border-red-200 dark:border-red-800 text-xs">
        <TrendingDown className="h-3 w-3 mr-0.5" />
        SELL
      </Badge>
    );
  }
  return (
    <Badge variant="secondary" className="text-xs">
      <Minus className="h-3 w-3 mr-0.5" />
      HOLD
    </Badge>
  );
}

function getSummary(signal: WatchlistSignalItem): string {
  if (signal.error) return signal.error;
  if (!signal.summary || signal.summary.signals.length === 0) return "No signals available";
  const nonNeutral = signal.summary.signals.filter((s) => s.action !== "NEUTRAL");
  const total = signal.summary.signals.length;
  if (signal.summary.rating === "NEUTRAL") {
    return `${total - nonNeutral.length} of ${total} indicators are neutral`;
  }
  return `${nonNeutral.length} of ${total} indicators agree`;
}

export function LatestSignals({ watchlistId }: LatestSignalsProps) {
  const { data: signalsData, isLoading, isError } = useWatchlistSignalsQuery(watchlistId);

  const strongSignals = React.useMemo(() => {
    if (!signalsData?.signals) return [];
    return signalsData.signals
      .filter((s) => s.summary && !s.error)
      .sort((a, b) => (b.summary?.confidence ?? 0) - (a.summary?.confidence ?? 0))
      .slice(0, 4);
  }, [signalsData]);

  if (!watchlistId) {
    return null;
  }

  return (
    <Card className="transition-all hover:-translate-y-0.5 hover:shadow-md">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Signal className="h-4 w-4 text-muted-foreground" />
          Latest Signals
        </CardTitle>
        {signalsData && strongSignals.length > 0 && (
          <Link href="/dashboard/signals">
            <Button variant="ghost" size="sm" className="text-xs gap-1">
              View all <ArrowRight className="h-3 w-3" />
            </Button>
          </Link>
        )}
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-12 w-full rounded-md" />
            ))}
          </div>
        ) : isError ? (
          <p className="text-sm text-muted-foreground">Failed to load signals</p>
        ) : strongSignals.length === 0 ? (
          <p className="text-sm text-muted-foreground">No signals available for your watchlists.</p>
        ) : (
          <div className="space-y-2">
            {strongSignals.map((signal) => (
              <div
                key={signal.ticker}
                className="flex items-center justify-between p-2 rounded-md bg-muted/50 animate-fade-in"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <span className="text-sm font-mono font-medium shrink-0">
                    {signal.ticker}
                  </span>
                  {signal.summary && <SignalBadge rating={signal.summary.rating} />}
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  {signal.summary && (
                    <>
                      <div className="hidden sm:flex items-center gap-1.5">
                        <div className="w-16 h-1.5 rounded-full bg-muted-foreground/20 overflow-hidden">
                          <div
                            className="h-full rounded-full bg-primary transition-all duration-700"
                            style={{ width: `${Math.round(signal.summary.confidence * 100)}%` }}
                          />
                        </div>
                        <span className="text-xs text-muted-foreground tabular-nums w-8 text-right">
                          {Math.round(signal.summary.confidence * 100)}%
                        </span>
                      </div>
                      <span className="text-xs text-muted-foreground hidden lg:inline max-w-[160px] truncate">
                        {getSummary(signal)}
                      </span>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
