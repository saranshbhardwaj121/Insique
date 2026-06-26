"use client";

import * as React from "react";
import Link from "next/link";
import { BarChart3, TrendingUp, Signal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface TickerActionsProps {
  ticker: string;
  className?: string;
}

export function TickerActions({ ticker, className }: TickerActionsProps) {
  return (
    <div className={cn("flex items-center gap-0.5", className)}>
      <Link
        href={`/dashboard/analytics?ticker=${encodeURIComponent(ticker)}`}
        title="View Analytics"
      >
        <Button variant="ghost" size="icon" className="h-7 w-7 sm:h-9 sm:w-9">
          <BarChart3 className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
          <span className="sr-only">Analytics for {ticker}</span>
        </Button>
      </Link>
      <Link
        href={`/dashboard/market-data?ticker=${encodeURIComponent(ticker)}`}
        title="View Market Data"
      >
        <Button variant="ghost" size="icon" className="h-7 w-7 sm:h-9 sm:w-9">
          <TrendingUp className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
          <span className="sr-only">Market Data for {ticker}</span>
        </Button>
      </Link>
      <Link
        href={`/dashboard/signals?ticker=${encodeURIComponent(ticker)}`}
        title="View Signals"
      >
        <Button variant="ghost" size="icon" className="h-7 w-7 sm:h-9 sm:w-9">
          <Signal className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
          <span className="sr-only">Signals for {ticker}</span>
        </Button>
      </Link>
    </div>
  );
}
