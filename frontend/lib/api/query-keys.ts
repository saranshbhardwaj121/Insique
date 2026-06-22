export const queryKeys = {
  auth: {
    me: ["auth", "me"] as const,
  },
  watchlists: {
    all: ["watchlists"] as const,
    detail: (id: string) => ["watchlists", id] as const,
    quotes: (id: string) => ["watchlists", id, "quotes"] as const,
    signals: (id: string) => ["watchlists", id, "signals"] as const,
  },
  marketData: {
    quote: (ticker: string) => ["market-data", "quote", ticker] as const,
    history: (ticker: string) => ["market-data", "history", ticker] as const,
    search: (query: string) => ["market-data", "search", query] as const,
  },
  analytics: {
    sma: (ticker: string) => ["analytics", ticker, "sma"] as const,
    ema: (ticker: string) => ["analytics", ticker, "ema"] as const,
    rsi: (ticker: string) => ["analytics", ticker, "rsi"] as const,
    macd: (ticker: string) => ["analytics", ticker, "macd"] as const,
  },
  signals: {
    ticker: (ticker: string) => ["signals", ticker] as const,
  },
  alerts: {
    all: ["alerts"] as const,
    detail: (id: string) => ["alerts", id] as const,
    triggers: (id: string) => ["alerts", id, "triggers"] as const,
  },
  notifications: {
    list: (limit: number) => ["notifications", "list", limit] as const,
    count: ["notifications", "count"] as const,
  },
  portfolio: {
    holdings: {
      all: ["portfolio", "holdings"] as const,
      detail: (id: string) => ["portfolio", "holdings", id] as const,
    },
    summary: ["portfolio", "summary"] as const,
  },
} as const;
