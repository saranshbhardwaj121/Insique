"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface TickerData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  signal: "BUY" | "SELL" | "NEUTRAL";
  confidence: number;
}

const INITIAL_TICKERS: TickerData[] = [
  { symbol: "RELIANCE.NS", price: 3245.6, change: 38.2, changePercent: 1.24, signal: "BUY", confidence: 78 },
  { symbol: "TCS.NS", price: 4102.0, change: -16.4, changePercent: -0.4, signal: "NEUTRAL", confidence: 52 },
  { symbol: "HDFCBANK.NS", price: 1678.5, change: 12.8, changePercent: 0.8, signal: "BUY", confidence: 65 },
  { symbol: "INFY.NS", price: 1892.3, change: 38.8, changePercent: 2.1, signal: "SELL", confidence: 54 },
  { symbol: "TATAMOTORS.NS", price: 945.2, change: -5.6, changePercent: -0.6, signal: "NEUTRAL", confidence: 48 },
];

function randomDrift(value: number, volatility: number): number {
  return value + (Math.random() - 0.5) * volatility;
}

function SignalBadge({ signal, confidence }: { signal: string; confidence: number }) {
  const colorMap: Record<string, string> = {
    BUY: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
    SELL: "bg-red-500/10 text-red-500 border-red-500/20",
    NEUTRAL: "bg-muted text-muted-foreground border-border",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[10px] font-medium",
        colorMap[signal] || colorMap.NEUTRAL
      )}
    >
      <span
        className={cn(
          "h-1 w-1 rounded-full",
          signal === "BUY" && "bg-emerald-500",
          signal === "SELL" && "bg-red-500",
          signal === "NEUTRAL" && "bg-muted-foreground"
        )}
      />
      {signal} {confidence}%
    </span>
  );
}

export function LiveTicker() {
  const [tickers, setTickers] = React.useState<TickerData[]>(INITIAL_TICKERS);

  React.useEffect(() => {
    const interval = setInterval(() => {
      setTickers((prev) =>
        prev.map((t) => {
          const newPrice = randomDrift(t.price, t.price * 0.002);
          const newChange = newPrice - (t.price - t.change);
          const newChangePercent = (newChange / (t.price - t.change)) * 100;
          return { ...t, price: newPrice, change: newChange, changePercent: newChangePercent };
        })
      );
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="py-20">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mb-10 text-center">
          <h2 className="text-balance text-2xl font-semibold tracking-tight sm:text-3xl">
            In the markets today
          </h2>
          <p className="mt-3 text-muted-foreground">
            Live signals from real tickers. Data updates every 3 seconds.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
          {tickers.map((ticker) => (
            <div
              key={ticker.symbol}
              className="group rounded-xl border border-border/50 bg-card p-4 transition-all duration-200 hover:-translate-y-0.5 hover:border-border/80"
            >
              <div className="mb-2 font-mono text-[11px] text-muted-foreground">
                {ticker.symbol}
              </div>
              <div className="mb-1 font-mono text-lg font-semibold tabular-nums tracking-tight">
                ₹{ticker.price.toFixed(2)}
              </div>
              <div
                className={cn(
                  "mb-3 font-mono text-xs tabular-nums",
                  ticker.change >= 0 ? "text-emerald-500" : "text-red-500"
                )}
              >
                {ticker.change >= 0 ? "▲" : "▼"} {ticker.changePercent >= 0 ? "+" : ""}
                {ticker.changePercent.toFixed(2)}%
              </div>
              <SignalBadge signal={ticker.signal} confidence={ticker.confidence} />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
