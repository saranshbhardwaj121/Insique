"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { TickerSearchForm } from "@/components/shared/ticker-search-form";
import { TickerNavPills } from "@/components/shared/ticker-nav-pills";
import { SingleTickerView } from "@/components/signals/single-ticker-view";
import { WatchlistSignalsView } from "@/components/signals/watchlist-signals-view";
import { useTickerSignalQuery, useWatchlistSignalsQuery } from "@/features/signals/hooks";
import { useTickerContext } from "@/features/ticker/ticker-context";

type Tab = "ticker" | "watchlist";

interface SignalsPageContentProps {
  initialTicker: string | null;
}

export function SignalsPageContent({ initialTicker }: SignalsPageContentProps) {
  const { activeTicker, setActiveTicker } = useTickerContext();
  const router = useRouter();
  const [activeTab, setActiveTab] = React.useState<Tab>(activeTicker ? "ticker" : "ticker");
  const [selectedWatchlistId, setSelectedWatchlistId] = React.useState<string | null>(null);
  const initialized = React.useRef(false);

  React.useEffect(() => {
    if (initialTicker && !initialized.current) {
      initialized.current = true;
      setActiveTicker(initialTicker);
      setActiveTab("ticker");
    }
  }, [initialTicker, setActiveTicker]);

  const handleSearch = React.useCallback(
    (ticker: string) => {
      setActiveTicker(ticker);
      setActiveTab("ticker");
      router.replace(`/dashboard/signals?ticker=${encodeURIComponent(ticker)}`);
    },
    [setActiveTicker, router]
  );

  const tickerQuery = useTickerSignalQuery(
    activeTab === "ticker" ? activeTicker : null
  );
  const watchlistQuery = useWatchlistSignalsQuery(
    activeTab === "watchlist" ? selectedWatchlistId : null
  );

  const isRefreshing =
    activeTab === "ticker" ? tickerQuery.isFetching : watchlistQuery.isFetching;

  const showRefresh =
    (activeTab === "ticker" && activeTicker !== null) ||
    (activeTab === "watchlist" && selectedWatchlistId !== null);

  const handleRefresh = () => {
    if (activeTab === "ticker" && activeTicker) {
      tickerQuery.refetch();
    } else if (activeTab === "watchlist" && selectedWatchlistId) {
      watchlistQuery.refetch();
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Signals</h1>
          <p className="text-muted-foreground">
            {activeTab === "ticker"
              ? "Analyze buy and sell signals for any ticker"
              : "View aggregated signals across your watchlists"}
          </p>
        </div>
        {showRefresh && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            <RefreshCw
              className={`mr-1.5 h-3.5 w-3.5 ${isRefreshing ? "animate-spin" : ""}`}
            />
            Refresh
          </Button>
        )}
      </div>

      <div className="flex border-b">
        <button
          onClick={() => setActiveTab("ticker")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "ticker"
              ? "border-primary text-foreground"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          Single Ticker
        </button>
        <button
          onClick={() => setActiveTab("watchlist")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === "watchlist"
              ? "border-primary text-foreground"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          Watchlist Signals
        </button>
      </div>

      {activeTab === "ticker" ? (
        <div className="space-y-6">
          <TickerSearchForm
            placeholder="Search ticker (e.g. AAPL)"
            buttonLabel="Analyze"
            onSubmit={handleSearch}
          />
          {activeTicker && <TickerNavPills />}
          <SingleTickerView
            activeTicker={activeTicker}
            onSearch={handleSearch}
            query={tickerQuery}
          />
        </div>
      ) : (
        <WatchlistSignalsView
          selectedWatchlistId={selectedWatchlistId}
          onSelectWatchlist={setSelectedWatchlistId}
          query={watchlistQuery}
        />
      )}
    </div>
  );
}
