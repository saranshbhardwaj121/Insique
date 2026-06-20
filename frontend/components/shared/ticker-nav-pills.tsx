"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, TrendingUp, Signal } from "lucide-react";
import { cn } from "@/lib/utils";
import { useTickerContext } from "@/features/ticker/ticker-context";

interface NavPill {
  label: string;
  href: string;
  icon: React.ReactNode;
}

const pills: NavPill[] = [
  { label: "Analytics", href: "/dashboard/analytics", icon: <BarChart3 className="h-3.5 w-3.5" /> },
  { label: "Market Data", href: "/dashboard/market-data", icon: <TrendingUp className="h-3.5 w-3.5" /> },
  { label: "Signals", href: "/dashboard/signals", icon: <Signal className="h-3.5 w-3.5" /> },
];

export function TickerNavPills() {
  const { activeTicker } = useTickerContext();
  const pathname = usePathname();

  if (!activeTicker) return null;

  return (
    <div className="flex items-center gap-2 flex-wrap">
      <span className="text-xs font-medium text-muted-foreground mr-1">
        {activeTicker}:
      </span>
      {pills.map((pill) => {
        const isActive = pathname === pill.href;
        return (
          <Link
            key={pill.href}
            href={`${pill.href}?ticker=${encodeURIComponent(activeTicker)}`}
            className={cn(
              "inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 text-xs font-medium transition-colors",
              isActive
                ? "border-primary bg-primary/10 text-primary cursor-default pointer-events-none"
                : "border-border bg-card hover:bg-accent hover:text-accent-foreground text-muted-foreground"
            )}
            aria-disabled={isActive}
            tabIndex={isActive ? -1 : undefined}
          >
            {pill.icon}
            {pill.label}
          </Link>
        );
      })}
    </div>
  );
}
