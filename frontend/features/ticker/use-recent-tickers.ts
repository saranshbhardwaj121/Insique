"use client";

import * as React from "react";
import type { RecentTicker } from "./types";

const STORAGE_KEY = "insique-recent-tickers";
const MAX_TICKERS = 10;

function isBrowser(): boolean {
  return typeof window !== "undefined";
}

function loadRecent(): RecentTicker[] {
  if (!isBrowser()) return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(
      (t): t is RecentTicker =>
        typeof t === "object" &&
        typeof t.ticker === "string" &&
        typeof t.viewedAt === "string"
    );
  } catch {
    return [];
  }
}

function saveRecent(tickers: RecentTicker[]) {
  if (!isBrowser()) return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tickers));
  } catch {
    // localStorage might be full or unavailable
  }
}

export function useRecentTickers() {
  const [recentTickers, setRecentTickers] = React.useState<RecentTicker[]>(loadRecent);

  React.useEffect(() => {
    saveRecent(recentTickers);
  }, [recentTickers]);

  const pushRecentTicker = React.useCallback((ticker: string) => {
    setRecentTickers((prev) => {
      const filtered = prev.filter((t) => t.ticker !== ticker);
      const next: RecentTicker = { ticker, viewedAt: new Date().toISOString() };
      return [next, ...filtered].slice(0, MAX_TICKERS);
    });
  }, []);

  const clearRecentTickers = React.useCallback(() => {
    setRecentTickers([]);
  }, []);

  return { recentTickers, pushRecentTicker, clearRecentTickers };
}
