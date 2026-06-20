"use client";

import * as React from "react";
import { SignalsEmptyState } from "@/components/signals/signals-empty-state";
import { SignalsHeroSkeleton, SignalsBreakdownSkeleton } from "@/components/signals/signals-skeleton";
import { SignalsErrorState } from "@/components/signals/signals-error-state";
import { SignalHeroCard } from "@/components/signals/signal-hero-card";
import { SignalIndicatorBreakdown } from "@/components/signals/signal-indicator-breakdown";
import { IndicatorConfidenceChart } from "@/components/charts/indicator-confidence-chart";
import type { SignalSummary } from "@/features/signals/types";

interface SingleTickerViewProps {
  activeTicker: string | null;
  onSearch: (ticker: string) => void;
  query: {
    data: SignalSummary | undefined;
    isLoading: boolean;
    isError: boolean;
    error: Error | null;
    refetch: () => void;
  };
}

export function SingleTickerView({ activeTicker, onSearch, query }: SingleTickerViewProps) {
  return (
    <div className="space-y-6">
      {!activeTicker ? (
        <SignalsEmptyState />
      ) : query.isLoading ? (
        <div className="space-y-4">
          <SignalsHeroSkeleton />
          <SignalsBreakdownSkeleton />
        </div>
      ) : query.isError ? (
        <SignalsErrorState
          message={query.error?.message || "Failed to load signals"}
          onRetry={() => query.refetch()}
        />
      ) : query.data ? (
        <>
          <SignalHeroCard data={query.data} />
          <IndicatorConfidenceChart signals={query.data.signals} />
          <div className="grid gap-4 md:grid-cols-2">
            {query.data.signals.map((detail) => (
              <SignalIndicatorBreakdown key={detail.name} detail={detail} />
            ))}
          </div>
        </>
      ) : null}
    </div>
  );
}
