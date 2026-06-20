"use client";

import * as React from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useWatchlistsQuery } from "@/features/watchlists/hooks";
import { useTickerContext } from "@/features/ticker/ticker-context";
import {
  ListChecks,
  BarChart3,
  Signal,
  TrendingUp,
  Plus,
  History,
  X,
} from "lucide-react";

export function DashboardContent() {
  const { data: watchlists, isLoading, isError } = useWatchlistsQuery();
  const { recentTickers, clearRecentTickers } = useTickerContext();

  const totalWatchlists = watchlists?.length ?? 0;
  const totalTickers = watchlists?.reduce((sum, wl) => sum + wl.items.length, 0) ?? 0;
  const recentWatchlists = watchlists?.slice(0, 3) ?? [];
  const hasWatchlists = totalWatchlists > 0;
  const hasRecentTickers = recentTickers.length > 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome to Insique. Your market intelligence platform.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Watchlists</CardTitle>
            <ListChecks className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold">{totalWatchlists}</div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tracked Tickers</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold">{totalTickers}</div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Signals</CardTitle>
            <Signal className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {hasWatchlists ? (
              <Link href="/dashboard/signals">
                <Button variant="outline" size="sm" className="gap-1.5">
                  <Signal className="h-3.5 w-3.5" />
                  View signals
                </Button>
              </Link>
            ) : (
              <>
                <div className="text-2xl font-bold text-muted-foreground">--</div>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Add tickers to see signals
                </p>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-3">Quick Actions</h2>
        <div className="grid gap-3 grid-cols-2 md:grid-cols-4">
          <Link href="/dashboard/watchlists">
            <Card className="hover:bg-accent transition-colors cursor-pointer h-full">
              <CardContent className="flex flex-col items-center justify-center py-4 text-center">
                <ListChecks className="h-6 w-6 text-muted-foreground mb-2" />
                <p className="text-sm font-medium">Watchlists</p>
                <p className="text-xs text-muted-foreground">Manage your lists</p>
              </CardContent>
            </Card>
          </Link>
          <Link href="/dashboard/analytics">
            <Card className="hover:bg-accent transition-colors cursor-pointer h-full">
              <CardContent className="flex flex-col items-center justify-center py-4 text-center">
                <BarChart3 className="h-6 w-6 text-muted-foreground mb-2" />
                <p className="text-sm font-medium">Analytics</p>
                <p className="text-xs text-muted-foreground">Technical indicators</p>
              </CardContent>
            </Card>
          </Link>
          <Link href="/dashboard/signals">
            <Card className="hover:bg-accent transition-colors cursor-pointer h-full">
              <CardContent className="flex flex-col items-center justify-center py-4 text-center">
                <Signal className="h-6 w-6 text-muted-foreground mb-2" />
                <p className="text-sm font-medium">Signals</p>
                <p className="text-xs text-muted-foreground">BUY / SELL ratings</p>
              </CardContent>
            </Card>
          </Link>
          <Link href="/dashboard/market-data">
            <Card className="hover:bg-accent transition-colors cursor-pointer h-full">
              <CardContent className="flex flex-col items-center justify-center py-4 text-center">
                <TrendingUp className="h-6 w-6 text-muted-foreground mb-2" />
                <p className="text-sm font-medium">Market Data</p>
                <p className="text-xs text-muted-foreground">Real-time quotes</p>
              </CardContent>
            </Card>
          </Link>
        </div>
      </div>

      {hasRecentTickers && (
        <div>
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

      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold">Recent Watchlists</h2>
          {hasWatchlists && (
            <Link href="/dashboard/watchlists">
              <Button variant="ghost" size="sm">View all</Button>
            </Link>
          )}
        </div>
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-16 w-full rounded-lg" />
            ))}
          </div>
        ) : isError ? (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-8 text-center">
              <p className="text-sm text-muted-foreground">Failed to load watchlists</p>
              <p className="text-xs text-muted-foreground mt-1">Try refreshing the page</p>
            </CardContent>
          </Card>
        ) : !hasWatchlists ? (
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
        ) : (
          <div className="space-y-2">
            {recentWatchlists.map((wl) => (
              <Link key={wl.id} href="/dashboard/watchlists">
                <Card className="hover:bg-accent transition-colors cursor-pointer">
                  <CardContent className="flex items-center justify-between py-3">
                    <div className="flex items-center gap-3">
                      <div>
                        <p className="font-medium">{wl.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {wl.items.length} {wl.items.length === 1 ? "ticker" : "tickers"}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {wl.items.length > 0 && (
                        <div className="hidden sm:flex gap-1">
                          {wl.items.slice(0, 3).map((item) => (
                            <span key={item.ticker} className="text-xs bg-muted px-1.5 py-0.5 rounded font-mono">
                              {item.ticker}
                            </span>
                          ))}
                          {wl.items.length > 3 && (
                            <span className="text-xs text-muted-foreground">+{wl.items.length - 3}</span>
                          )}
                        </div>
                      )}
                      <p className="text-xs text-muted-foreground shrink-0">
                        {new Date(wl.updated_at).toLocaleDateString()}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
