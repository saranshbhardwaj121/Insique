"use client";

import * as React from "react";
import { AlertCircle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TickerActions } from "@/components/shared/ticker-actions";
import type { WatchlistSignalItem } from "@/features/signals/types";

interface SignalTickerRowCardProps {
  item: WatchlistSignalItem;
}

function formatConfidence(value: number): string {
  return `${(value * 100).toFixed(0)}%`;
}

export function SignalTickerRowCard({ item }: SignalTickerRowCardProps) {
  if (item.error && !item.summary) {
    return (
      <Card>
        <CardContent className="flex items-center justify-between py-3">
          <div className="flex items-center gap-2 min-w-0">
            <span className="font-medium">{item.ticker}</span>
            <AlertCircle className="h-4 w-4 shrink-0 text-destructive" />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground truncate">
              {item.error}
            </span>
            <TickerActions ticker={item.ticker} />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!item.summary) {
    return null;
  }

  const { summary } = item;
  const isBuy = summary.rating === "BUY";
  const isSell = summary.rating === "SELL";
  const confidencePercent = (summary.confidence * 100).toFixed(0);

  const badgeClass = isBuy
    ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100"
    : isSell
    ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100"
    : "bg-muted text-muted-foreground";

  const barColor = isBuy
    ? "bg-green-500 dark:bg-green-400"
    : isSell
    ? "bg-red-500 dark:bg-red-400"
    : "bg-muted-foreground";

  return (
    <Card>
      <CardContent className="flex items-center justify-between py-3">
        <div className="flex items-center gap-3 min-w-0">
          <span className="font-medium">{summary.ticker}</span>
          <Badge className={badgeClass}>{summary.rating}</Badge>
        </div>
        <div className="flex items-center gap-3 text-sm text-muted-foreground shrink-0">
          <span className="tabular-nums">{Math.abs(summary.score)}/6</span>
          <div className="flex flex-col items-end">
            <span className="font-medium tabular-nums">
              {formatConfidence(summary.confidence)}
            </span>
            <div className="w-14 h-1 bg-muted rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${barColor}`}
                style={{ width: `${confidencePercent}%` }}
              />
            </div>
          </div>
          <TickerActions ticker={summary.ticker} />
        </div>
      </CardContent>
    </Card>
  );
}
