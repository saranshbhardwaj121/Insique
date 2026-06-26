"use client";

import * as React from "react";
import Link from "next/link";
import { useIsFetching } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useWatchlistsQuery } from "@/features/watchlists/hooks";
import { useHoldingsQuery } from "@/features/portfolio/hooks";
import { useTickerContext } from "@/features/ticker/ticker-context";
import { MarketLoader } from "@/components/loading/market-loader";
import { DashboardStats } from "@/components/dashboard/dashboard-stats";
import { MarketOverview } from "@/components/dashboard/market-overview";
import { PortfolioSummary } from "@/components/dashboard/portfolio-summary";
import { LatestSignals } from "@/components/dashboard/latest-signals";
import { WatchlistSnapshot } from "@/components/dashboard/watchlist-snapshot";
import { TopMovers } from "@/components/dashboard/top-movers";
import {
  ListChecks,
  BarChart3,
  Signal,
  TrendingUp,
  PieChart,
  Plus,
  History,
  X,
} from "lucide-react";

export function DashboardContent() {
  const { data: watchlists, isLoading: wlLoading } = useWatchlistsQuery();
  const { data: holdings, isLoading: holdingsLoading } = useHoldingsQuery();
  const { recentTickers, clearRecentTickers } = useTickerContext();

  const fetchingWatchlists = useIsFetching({ queryKey: ["watchlists"] });
  const fetchingPortfolio = useIsFetching({ queryKey: ["portfolio"] });
  const fetchingMarketData = useIsFetching({ queryKey: ["market-data", "quote"] });

  const isDashboardReady = !wlLoading && !holdingsLoading
    && fetchingWatchlists === 0
    && fetchingPortfolio === 0
    && fetchingMarketData === 0;

  const totalWatchlists = watchlists?.length ?? 0;
  const totalTickers = watchlists?.reduce((sum, wl) => sum + wl.items.length, 0) ?? 0;
  const totalHoldings = holdings?.length ?? 0;
  const firstWatchlistId = watchlists?.[0]?.id ?? null;
  const firstWatchlistName = watchlists?.[0]?.name ?? "";
  const hasWatchlists = totalWatchlists > 0;
  const hasRecentTickers = recentTickers.length > 0;

  return (
    <MarketLoader isLoading={!isDashboardReady}>
      <div className="space-y-6">
        <div className="animate-fade-in">
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome to Insique. Your market intelligence platform.
          </p>
        </div>

        <div className="animate-in animate-in-stagger-1">
          <MarketOverview />
        </div>

        <DashboardStats
          totalWatchlists={totalWatchlists}
          totalTickers={totalTickers}
          totalHoldings={totalHoldings}
          isLoading={wlLoading}
        />

        <div className="grid gap-4 lg:grid-cols-2">
          <div className="animate-in animate-in-stagger-1">
            <PortfolioSummary />
          </div>
          <div className="animate-in animate-in-stagger-2">
            <LatestSignals watchlistId={firstWatchlistId} />
          </div>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <div className="animate-in animate-in-stagger-1">
            <WatchlistSnapshot
              watchlistId={firstWatchlistId}
              watchlistName={firstWatchlistName}
            />
          </div>
          <div className="animate-in animate-in-stagger-2">
            <TopMovers watchlistId={firstWatchlistId} />
          </div>
        </div>

        <div className="animate-in animate-in-stagger-1">
          <div>
            <h2 className="text-lg font-semibold mb-3">Quick Actions</h2>
            <div className="grid gap-3 grid-cols-2 md:grid-cols-5">
              <Link href="/dashboard/watchlists">
                <Card className="hover:bg-accent cursor-pointer h-full transition-all hover:-translate-y-0.5 hover:shadow-md">
                  <CardContent className="flex flex-col items-center justify-center py-4 text-center">
                    <ListChecks className="h-6 w-6 text-muted-foreground mb-2" />
                    <p className="text-sm font-medium">Watchlists</p>
                    <p className="text-xs text-muted-foreground">Manage your lists</p>
                  </CardContent>
                </Card>
              </Link>
              <Link href="/dashboard/analytics">
                <Card className="hover:bg-accent cursor-pointer h-full transition-all hover:-translate-y-0.5 hover:shadow-md">
                  <CardContent className="flex flex-col items-center justify-center py-4 text-center">
                    <BarChart3 className="h-6 w-6 text-muted-foreground mb-2" />
                    <p className="text-sm font-medium">Analytics</p>
                    <p className="text-xs text-muted-foreground">Technical indicators</p>
                  </CardContent>
                </Card>
              </Link>
              <Link href="/dashboard/signals">
                <Card className="hover:bg-accent cursor-pointer h-full transition-all hover:-translate-y-0.5 hover:shadow-md">
                  <CardContent className="flex flex-col items-center justify-center py-4 text-center">
                    <Signal className="h-6 w-6 text-muted-foreground mb-2" />
                    <p className="text-sm font-medium">Signals</p>
                    <p className="text-xs text-muted-foreground">BUY / SELL ratings</p>
                  </CardContent>
                </Card>
              </Link>
              <Link href="/dashboard/market-data">
                <Card className="hover:bg-accent cursor-pointer h-full transition-all hover:-translate-y-0.5 hover:shadow-md">
                  <CardContent className="flex flex-col items-center justify-center py-4 text-center">
                    <TrendingUp className="h-6 w-6 text-muted-foreground mb-2" />
                    <p className="text-sm font-medium">Market Data</p>
                    <p className="text-xs text-muted-foreground">Real-time quotes</p>
                  </CardContent>
                </Card>
              </Link>
              <Link href="/dashboard/portfolio">
                <Card className="hover:bg-accent cursor-pointer h-full transition-all hover:-translate-y-0.5 hover:shadow-md">
                  <CardContent className="flex flex-col items-center justify-center py-4 text-center">
                    <PieChart className="h-6 w-6 text-muted-foreground mb-2" />
                    <p className="text-sm font-medium">Portfolio</p>
                    <p className="text-xs text-muted-foreground">Track holdings</p>
                  </CardContent>
                </Card>
              </Link>
            </div>
          </div>
        </div>

        {hasRecentTickers && (
          <div className="animate-in animate-in-stagger-1">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <History className="h-4 w-4 text-muted-foreground" />
                <h2 className="text-lg font-semibold">Recently Viewed</h2>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={clearRecentTickers}
                className="text-muted-foreground"
              >
                <X className="h-3.5 w-3.5 mr-1" />
                Clear
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {recentTickers.map((rt) => (
                <Link
                  key={rt.ticker}
                  href={`/dashboard/analytics?ticker=${encodeURIComponent(rt.ticker)}`}
                >
                  <Button
                    variant="outline"
                    size="sm"
                    className="font-mono text-xs h-8"
                  >
                    {rt.ticker}
                  </Button>
                </Link>
              ))}
            </div>
          </div>
        )}

        {!hasWatchlists && !wlLoading && (
          <div className="animate-in animate-in-stagger-1">
            <Card className="border-dashed">
              <CardContent className="flex flex-col items-center justify-center py-10 text-center">
                <ListChecks className="h-10 w-10 text-muted-foreground mb-3" />
                <h3 className="text-base font-semibold mb-1">No watchlists yet</h3>
                <p className="text-sm text-muted-foreground mb-4 max-w-sm">
                  Create your first watchlist to start tracking stocks and receiving signals
                </p>
                <Link href="/dashboard/watchlists">
                  <Button className="gap-1.5">
                    <Plus className="h-4 w-4" />
                    Create watchlist
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </MarketLoader>
  );
}
