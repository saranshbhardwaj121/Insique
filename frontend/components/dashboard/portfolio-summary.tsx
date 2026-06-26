"use client";

import * as React from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { usePortfolioSummaryQuery } from "@/features/portfolio/hooks";
import { useCountUp } from "@/lib/hooks/use-count-up";
import { PieChart, TrendingUp, TrendingDown, ArrowUpRight, ArrowDownRight } from "lucide-react";

function formatCurrency(value: number | null | undefined): string {
  if (value == null) return "--";
  return value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export function PortfolioSummary() {
  const { data: summary, isLoading } = usePortfolioSummaryQuery();
  const hasHoldings = (summary?.total_holdings ?? 0) > 0;

  const animatedValue = useCountUp(summary?.total_market_value ?? 0, 800, !isLoading);
  const animatedPnL = useCountUp(Math.abs(summary?.total_profit_loss ?? 0), 800, !isLoading);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <PieChart className="h-4 w-4 text-muted-foreground" />
            Portfolio
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Skeleton className="h-8 w-32" />
          <Skeleton className="h-4 w-24" />
        </CardContent>
      </Card>
    );
  }

  if (!hasHoldings) {
    return (
      <Card className="border-dashed">
        <CardHeader>
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <PieChart className="h-4 w-4 text-muted-foreground" />
            Portfolio
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-3">No holdings tracked yet.</p>
          <Link href="/dashboard/portfolio">
            <Button variant="outline" size="sm">Add holdings</Button>
          </Link>
        </CardContent>
      </Card>
    );
  }

  const isProfitable = (summary?.total_profit_loss ?? 0) >= 0;
  const bestHolding = [...(summary?.holdings ?? [])].sort(
    (a, b) => (b.profit_loss_percent ?? 0) - (a.profit_loss_percent ?? 0)
  )[0];
  const worstHolding = [...(summary?.holdings ?? [])].sort(
    (a, b) => (a.profit_loss_percent ?? 0) - (b.profit_loss_percent ?? 0)
  )[0];

  return (
    <Card className="transition-all hover:-translate-y-0.5 hover:shadow-md">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <PieChart className="h-4 w-4 text-muted-foreground" />
          Portfolio
        </CardTitle>
        {summary && (
          <span className={`text-xs font-medium ${isProfitable ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>
            {isProfitable ? "+" : ""}{summary.total_profit_loss_percent.toFixed(2)}%
          </span>
        )}
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="text-2xl font-bold tabular-nums">
          ${formatCurrency(animatedValue)}
        </div>
        <div className={`text-sm font-medium tabular-nums flex items-center gap-1 ${isProfitable ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>
          {isProfitable ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
          {isProfitable ? "+" : ""}${formatCurrency(animatedPnL)}
          <span className="text-muted-foreground font-normal">
            ({(summary?.total_profit_loss_percent ?? 0) >= 0 ? "+" : ""}{summary?.total_profit_loss_percent.toFixed(2)}%)
          </span>
        </div>

        {bestHolding && (
          <div className="flex items-center gap-2 text-xs pt-1 border-t">
            <ArrowUpRight className="h-3 w-3 text-green-600 dark:text-green-400" />
            <span className="text-muted-foreground">Best:</span>
            <span className="font-medium font-mono">{bestHolding.ticker}</span>
            <span className="text-green-600 dark:text-green-400">
              +{bestHolding.profit_loss_percent?.toFixed(2)}%
            </span>
          </div>
        )}
        {worstHolding && worstHolding.ticker !== bestHolding?.ticker && (
          <div className="flex items-center gap-2 text-xs -mt-1">
            <ArrowDownRight className="h-3 w-3 text-red-600 dark:text-red-400" />
            <span className="text-muted-foreground">Worst:</span>
            <span className="font-medium font-mono">{worstHolding.ticker}</span>
            <span className="text-red-600 dark:text-red-400">
              {worstHolding.profit_loss_percent?.toFixed(2)}%
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
