"use client";

import * as React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCountUp } from "@/lib/hooks/use-count-up";
import { ListChecks, TrendingUp, PieChart } from "lucide-react";

interface DashboardStatsProps {
  totalWatchlists: number;
  totalTickers: number;
  totalHoldings: number;
  isLoading: boolean;
}

function StatCard({
  title,
  value,
  icon: Icon,
  isLoading,
}: {
  title: string;
  value: number;
  icon: React.ElementType;
  isLoading: boolean;
}) {
  const count = useCountUp(value, 800, !isLoading);

  return (
    <Card className="transition-all hover:-translate-y-0.5 hover:shadow-md">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <Skeleton className="h-8 w-16" />
        ) : (
          <div className="text-2xl font-bold tabular-nums">{count}</div>
        )}
      </CardContent>
    </Card>
  );
}

export function DashboardStats({
  totalWatchlists,
  totalTickers,
  totalHoldings,
  isLoading,
}: DashboardStatsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      <div className="animate-in animate-in-stagger-1">
        <StatCard
          title="Watchlists"
          value={totalWatchlists}
          icon={ListChecks}
          isLoading={isLoading}
        />
      </div>
      <div className="animate-in animate-in-stagger-2">
        <StatCard
          title="Tracked Tickers"
          value={totalTickers}
          icon={TrendingUp}
          isLoading={isLoading}
        />
      </div>
      <div className="animate-in animate-in-stagger-3">
        <StatCard
          title="Holdings"
          value={totalHoldings}
          icon={PieChart}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}
