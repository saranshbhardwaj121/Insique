"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { TickerSearchForm } from "@/components/shared/ticker-search-form";
import { TickerNavPills } from "@/components/shared/ticker-nav-pills";
import { AnalyticsEmptyState } from "@/components/analytics/analytics-empty-state";
import { IndicatorCard } from "@/components/analytics/indicator-card";
import { MacdCard } from "@/components/analytics/macd-card";
import { useAnalyticsQueries } from "@/features/analytics/hooks";
import { useTickerContext } from "@/features/ticker/ticker-context";

interface AnalyticsPageContentProps {
  initialTicker: string | null;
}

export function AnalyticsPageContent({ initialTicker }: AnalyticsPageContentProps) {
  const { activeTicker, setActiveTicker } = useTickerContext();
  const router = useRouter();
  const queries = useAnalyticsQueries(activeTicker);
  const isFirstLoad = activeTicker !== null && queries.smaQuery.isLoading;
  const initialized = React.useRef(false);

  React.useEffect(() => {
    if (initialTicker && !initialized.current) {
      initialized.current = true;
      setActiveTicker(initialTicker);
    }
  }, [initialTicker, setActiveTicker]);

  const handleSearch = React.useCallback(
    (ticker: string) => {
      setActiveTicker(ticker);
      router.replace(`/dashboard/analytics?ticker=${encodeURIComponent(ticker)}`);
    },
    [setActiveTicker, router]
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">
            {activeTicker
              ? `Technical indicators for ${activeTicker}`
              : "View technical indicators for any ticker"}
          </p>
        </div>
        {activeTicker && (
          <Button
            variant="outline"
            size="sm"
            onClick={queries.refetchAll}
            disabled={queries.isFetching}
          >
            <RefreshCw className={`mr-1.5 h-3.5 w-3.5 ${queries.isFetching ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        )}
      </div>

      <TickerSearchForm
        isLoading={isFirstLoad}
        placeholder="Search ticker (e.g. AAPL)"
        buttonLabel="Analyze"
        onSubmit={handleSearch}
      />

      {activeTicker && <TickerNavPills />}

      {!activeTicker ? (
        <AnalyticsEmptyState />
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          <IndicatorCard title="RSI (14)" type="rsi" query={queries.rsiQuery} />
          <IndicatorCard title="SMA (20)" type="sma" query={queries.smaQuery} />
          <IndicatorCard title="EMA (20)" type="ema" query={queries.emaQuery} />
          <MacdCard query={queries.macdQuery} />
        </div>
      )}
    </div>
  );
}
