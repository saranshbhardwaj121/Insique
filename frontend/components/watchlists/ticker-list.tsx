"use client";

import * as React from "react";
import { Loader2, X } from "lucide-react";
import { useRemoveTickerMutation } from "@/features/watchlists/hooks";
import { TickerActions } from "@/components/shared/ticker-actions";
import type { WatchlistItem } from "@/features/watchlists/types";
import { TickerEmptyState } from "@/components/watchlists/watchlist-empty-state";

interface TickerListProps {
  watchlistId: string;
  items: WatchlistItem[];
}

export function TickerList({ watchlistId, items }: TickerListProps) {
  const removeTickerMutation = useRemoveTickerMutation();
  const [removingTicker, setRemovingTicker] = React.useState<string | null>(null);

  if (!items || items.length === 0) {
    return <TickerEmptyState />;
  }

  const handleRemove = async (ticker: string) => {
    setRemovingTicker(ticker);
    try {
      await removeTickerMutation.mutateAsync({ watchlistId, ticker });
    } catch {
      // Error toast handled by hook
    } finally {
      setRemovingTicker(null);
    }
  };

  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item) => (
        <div
          key={item.ticker}
          className="inline-flex items-center gap-1 rounded-md border bg-card px-2.5 py-1.5 text-sm"
        >
          <span className="font-medium">{item.ticker}</span>
          <TickerActions ticker={item.ticker} />
          <button
            onClick={() => handleRemove(item.ticker)}
            disabled={removingTicker === item.ticker}
            className="ml-0.5 rounded-sm text-muted-foreground hover:text-destructive transition-colors disabled:opacity-50"
            title={`Remove ${item.ticker}`}
          >
            {removingTicker === item.ticker ? (
              <Loader2 className="h-3 w-3 animate-spin" />
            ) : (
              <X className="h-3 w-3" />
            )}
          </button>
        </div>
      ))}
    </div>
  );
}
