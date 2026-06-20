export interface RecentTicker {
  ticker: string;
  viewedAt: string;
}

export interface TickerContextValue {
  activeTicker: string | null;
  setActiveTicker: (ticker: string | null) => void;
  recentTickers: RecentTicker[];
  clearRecentTickers: () => void;
}
