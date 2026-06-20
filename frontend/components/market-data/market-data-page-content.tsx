"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { TickerSearchForm } from "@/components/shared/ticker-search-form";
import { TickerNavPills } from "@/components/shared/ticker-nav-pills";
import { MarketDataEmptyState } from "@/components/market-data/market-data-empty-state";
import { MarketDataSkeleton } from "@/components/market-data/market-data-skeleton";
import { MarketDataErrorState } from "@/components/market-data/market-data-error-state";
import { MarketDataQuoteDisplay } from "@/components/market-data/market-data-quote-display";
import { useQuoteQuery } from "@/features/market-data/hooks";
import { useTickerContext } from "@/features/ticker/ticker-context";

interface MarketDataPageContentProps {
  initialTicker: string | null;
}

export function MarketDataPageContent({ initialTicker }: MarketDataPageContentProps) {
  const { activeTicker, setActiveTicker } = useTickerContext();
  const router = useRouter();
  const query = useQuoteQuery(activeTicker);
  const isFirstLoad = activeTicker !== null && query.isLoading;
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
      router.replace(`/dashboard/market-data?ticker=${encodeURIComponent(ticker)}`);
    },
    [setActiveTicker, router]
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Market Data</h1>
          <p className="text-muted-foreground">
            {activeTicker
              ? `Real-time quote for ${activeTicker}`
              : "Look up real-time market data for any ticker"}
          </p>
        </div>
        {activeTicker && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => query.refetch()}
            disabled={query.isFetching}
          >
            <RefreshCw className={`mr-1.5 h-3.5 w-3.5 ${query.isFetching ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        )}
      </div>

      <TickerSearchForm
        isLoading={isFirstLoad}
        placeholder="Search ticker (e.g. AAPL)"
        buttonLabel="Lookup"
        onSubmit={handleSearch}
      />

      {activeTicker && <TickerNavPills />}

      {!activeTicker ? (
        <MarketDataEmptyState />
      ) : query.isLoading ? (
        <MarketDataSkeleton />
      ) : query.isError ? (
        <MarketDataErrorState
          message={query.error?.message || "Failed to load quote"}
          onRetry={() => query.refetch()}
        />
      ) : query.data ? (
        <MarketDataQuoteDisplay data={query.data} />
      ) : null}
    </div>
  );
}
