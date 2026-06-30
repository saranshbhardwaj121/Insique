"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import {
  SignalsMockup,
  AnalyticsMockup,
  MarketDataMockup,
  WatchlistsMockup,
} from "@/components/landing/showcase-tab-content";

interface Tab {
  id: string;
  label: string;
  component: React.ReactNode;
  description: string;
}

const tabs: Tab[] = [
  {
    id: "signals",
    label: "Signals",
    component: <SignalsMockup />,
    description:
      "Every signal is the weighted vote of four technical indicators. Clear BUY, SELL, or NEUTRAL with a confidence score.",
  },
  {
    id: "analytics",
    label: "Analytics",
    component: <AnalyticsMockup />,
    description:
      "Visualize momentum, trends, and crossovers. RSI, MACD, SMA, and EMA with clean, interactive charts that make patterns visible.",
  },
  {
    id: "market-data",
    label: "Market Data",
    component: <MarketDataMockup />,
    description:
      "Live and historical data for every supported ticker. Price, volume, and day range give you full context before a decision.",
  },
  {
    id: "watchlists",
    label: "Watchlists",
    component: <WatchlistsMockup />,
    description:
      "Organize tickers into focused groups. Monitor your portfolio, sector bets, or watch candidates side by side.",
  },
];

export function InteractiveShowcase() {
  const [activeTab, setActiveTab] = React.useState<string>("signals");
  const [isRotating, setIsRotating] = React.useState(true);
  const [isPaused, setIsPaused] = React.useState(false);
  const containerRef = React.useRef<HTMLDivElement>(null);
  const rotationTimerRef = React.useRef<ReturnType<typeof setTimeout> | null>(null);
  const cooldownRef = React.useRef(false);

  const activeIndex = tabs.findIndex((t) => t.id === activeTab);

  const resetRotation = React.useCallback(
    (cooldown = 8000) => {
      if (rotationTimerRef.current) clearTimeout(rotationTimerRef.current);
      cooldownRef.current = true;
      setIsRotating(false);
      rotationTimerRef.current = setTimeout(() => {
        cooldownRef.current = false;
        setIsRotating(true);
      }, cooldown);
    },
    []
  );

  React.useEffect(() => {
    if (!isRotating || isPaused) return;
    const interval = setInterval(() => {
      setActiveTab((prev) => {
        const currentIndex = tabs.findIndex((t) => t.id === prev);
        const nextIndex = (currentIndex + 1) % tabs.length;
        return tabs[nextIndex].id;
      });
    }, 5000);
    return () => clearInterval(interval);
  }, [isRotating, isPaused]);

  React.useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const onMouseEnter = () => setIsPaused(true);
    const onMouseLeave = () => setIsPaused(false);
    container.addEventListener("mouseenter", onMouseEnter);
    container.addEventListener("mouseleave", onMouseLeave);
    return () => {
      container.removeEventListener("mouseenter", onMouseEnter);
      container.removeEventListener("mouseleave", onMouseLeave);
    };
  }, []);

  React.useEffect(() => {
    return () => {
      if (rotationTimerRef.current) clearTimeout(rotationTimerRef.current);
    };
  }, []);

  const handleTabClick = (id: string) => {
    setActiveTab(id);
    resetRotation(12000);
  };

  return (
    <section className="py-24" id="features">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mb-12 text-center">
          <h2 className="text-balance text-2xl font-semibold tracking-tight sm:text-3xl">
            See what clarity looks like
          </h2>
          <p className="mt-3 text-muted-foreground">
            Every feature is built around one question: what do you need to know before you trade?
          </p>
        </div>

        <div ref={containerRef}>
          <div className="mb-6 flex gap-1 rounded-lg bg-secondary/50 p-1 overflow-x-auto">
            {tabs.map((tab, index) => (
              <button
                key={tab.id}
                onClick={() => handleTabClick(tab.id)}
                className={cn(
                  "relative flex-1 rounded-md px-4 py-2 text-sm font-medium transition-all duration-200",
                  activeTab === tab.id
                    ? "bg-background text-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                {tab.label}
                {!cooldownRef.current && isRotating && activeIndex === index && (
                  <span className="absolute bottom-0.5 left-1/2 h-0.5 w-4 -translate-x-1/2 rounded-full bg-primary" />
                )}
              </button>
            ))}
          </div>

          <div className="relative mb-6 overflow-hidden rounded-xl border border-border/50 bg-card shadow-xl transition-all duration-500">
            <div className="p-4 sm:p-6">
              {tabs.map((tab) => (
                <div
                  key={tab.id}
                  className={cn(
                    "transition-all duration-500",
                    activeTab === tab.id
                      ? "block animate-fade-in"
                      : "hidden"
                  )}
                >
                  {tab.component}
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-start justify-between gap-6">
            <div className="flex-1">
              <h3 className="text-lg font-semibold">
                Know your position before you take it.
              </h3>
              {tabs.map((tab) => (
                <p
                  key={tab.id}
                  className={cn(
                    "mt-2 text-sm leading-relaxed text-muted-foreground transition-opacity duration-500",
                    activeTab === tab.id ? "opacity-100" : "hidden opacity-0"
                  )}
                >
                  {tab.description}
                </p>
              ))}
            </div>
            <div className="hidden items-center gap-2 sm:flex">
              {tabs.map((tab, index) => (
                <button
                  key={tab.id}
                  onClick={() => handleTabClick(tab.id)}
                  className={cn(
                    "h-2 w-2 rounded-full transition-all duration-300",
                    activeTab === tab.id
                      ? "bg-primary"
                      : "bg-border hover:bg-muted-foreground/40"
                  )}
                  aria-label={`Switch to ${tab.label}`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
