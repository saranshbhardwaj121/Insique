import { TrendingUp, BarChart3, Activity, LineChart } from "lucide-react";

const indicatorCard = (
  label: string,
  value: string,
  sub: string,
  color: string
) => (
  <div className="rounded-lg border border-border/50 bg-secondary/20 p-3">
    <div className="text-[10px] text-muted-foreground">{label}</div>
    <div className={cn("mt-0.5 text-sm font-semibold", color)}>{value}</div>
    <div className={cn("text-[10px]", color.replace("text-", "text-").replace("font-semibold", "") || "text-muted-foreground")}>
      {sub}
    </div>
  </div>
);

function cn(...classes: (string | boolean | undefined | null)[]) {
  return classes.filter(Boolean).join(" ");
}

export function SignalsMockup() {
  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <div className="text-xs text-muted-foreground">Current Signal</div>
          <div className="text-lg font-semibold">RELIANCE.NS</div>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-lg font-semibold tabular-nums">₹3,245.60</div>
            <div className="text-xs font-medium text-emerald-500">▲ +1.24%</div>
          </div>
        </div>
      </div>

      <div className="mb-4 grid grid-cols-4 gap-3">
        <div className="rounded-lg border border-border/50 bg-secondary/20 p-3">
          <div className="text-[10px] text-muted-foreground">RSI</div>
          <div className="mt-0.5 text-sm font-semibold">42.3</div>
          <div className="text-[10px] text-muted-foreground">Neutral</div>
        </div>
        <div className="rounded-lg border border-border/50 bg-secondary/20 p-3">
          <div className="text-[10px] text-muted-foreground">MACD</div>
          <div className="mt-0.5 text-sm font-semibold text-emerald-500">Bullish</div>
          <div className="text-[10px] text-emerald-500">Crossover ↑</div>
        </div>
        <div className="rounded-lg border border-border/50 bg-secondary/20 p-3">
          <div className="text-[10px] text-muted-foreground">SMA (20)</div>
          <div className="mt-0.5 text-sm font-semibold text-emerald-500">↑ Uptrend</div>
          <div className="text-[10px] text-emerald-500">Price above</div>
        </div>
        <div className="rounded-lg border border-border/50 bg-secondary/20 p-3">
          <div className="text-[10px] text-muted-foreground">EMA (50)</div>
          <div className="mt-0.5 text-sm font-semibold text-emerald-500">↑ Uptrend</div>
          <div className="text-[10px] text-emerald-500">Price above</div>
        </div>
      </div>

      <div className="flex items-center justify-between rounded-lg border border-border/50 bg-secondary/20 p-4">
        <div>
          <div className="text-xs text-muted-foreground">Combined Signal</div>
          <div className="flex items-center gap-2">
            <span className="text-xl font-bold text-emerald-500">BUY</span>
            <span className="rounded-md bg-emerald-500/10 px-2 py-0.5 text-xs font-medium text-emerald-500">
              78% confidence
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>Confidence</span>
          <div className="h-1.5 w-24 rounded-full bg-border">
            <div className="h-full w-[78%] rounded-full bg-emerald-500 transition-all" />
          </div>
        </div>
      </div>
    </div>
  );
}

export function AnalyticsMockup() {
  return (
    <div>
      <div className="mb-4">
        <div className="text-xs text-muted-foreground">Technical Analysis</div>
        <div className="text-lg font-semibold">RELIANCE.NS</div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-lg border border-border/50 p-4">
          <div className="mb-3 flex items-center gap-2">
            <TrendingUp className="h-3.5 w-3.5 text-primary" />
            <span className="text-xs font-medium">RSI (14)</span>
          </div>
          <div className="mb-2 flex items-baseline gap-2">
            <span className="text-2xl font-semibold tabular-nums">42.3</span>
            <span className="text-xs text-muted-foreground">/ 100</span>
          </div>
          <div className="h-2 rounded-full bg-border">
            <div
              className="h-full rounded-full bg-primary"
              style={{ width: "42.3%" }}
            />
          </div>
          <div className="mt-2 text-xs text-muted-foreground">
            Neutral zone — no extreme conditions detected
          </div>
        </div>

        <div className="rounded-lg border border-border/50 p-4">
          <div className="mb-3 flex items-center gap-2">
            <BarChart3 className="h-3.5 w-3.5 text-emerald-500" />
            <span className="text-xs font-medium">MACD</span>
          </div>
          <div className="mb-2 flex items-baseline gap-2">
            <span className="text-2xl font-semibold text-emerald-500">Bullish</span>
          </div>
          <div className="flex gap-3 text-xs text-muted-foreground">
            <span>MACD: 12.45</span>
            <span>Signal: 8.32</span>
          </div>
          <div className="mt-2 text-xs text-muted-foreground">
            MACD line crossed above signal line — momentum shifting up
          </div>
        </div>

        <div className="rounded-lg border border-border/50 p-4">
          <div className="mb-3 flex items-center gap-2">
            <LineChart className="h-3.5 w-3.5 text-emerald-500" />
            <span className="text-xs font-medium">SMA (20)</span>
          </div>
          <div className="mb-1 text-xs text-muted-foreground">Price: ₹3,245</div>
          <div className="mb-2 text-xs text-muted-foreground">SMA: ₹3,198</div>
          <div className="text-xs text-emerald-500">Price above SMA — uptrend confirmed</div>
        </div>

        <div className="rounded-lg border border-border/50 p-4">
          <div className="mb-3 flex items-center gap-2">
            <Activity className="h-3.5 w-3.5 text-emerald-500" />
            <span className="text-xs font-medium">EMA (50)</span>
          </div>
          <div className="mb-1 text-xs text-muted-foreground">Price: ₹3,245</div>
          <div className="mb-2 text-xs text-muted-foreground">EMA: ₹3,167</div>
          <div className="text-xs text-emerald-500">Price above EMA — trend intact</div>
        </div>
      </div>
    </div>
  );
}

export function MarketDataMockup() {
  return (
    <div>
      <div className="mb-4">
        <div className="text-xs text-muted-foreground">Market Data</div>
        <div className="text-lg font-semibold">RELIANCE.NS</div>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="rounded-lg border border-border/50 p-4">
          <div className="text-[10px] text-muted-foreground">Current Price</div>
          <div className="mt-1 text-xl font-semibold tabular-nums">₹3,245.60</div>
          <div className="mt-0.5 text-xs font-medium text-emerald-500">▲ +1.24%</div>
        </div>
        <div className="rounded-lg border border-border/50 p-4">
          <div className="text-[10px] text-muted-foreground">Day Range</div>
          <div className="mt-1 text-sm font-semibold tabular-nums">
            ₹3,198.00 — ₹3,262.00
          </div>
        </div>
        <div className="rounded-lg border border-border/50 p-4">
          <div className="text-[10px] text-muted-foreground">Volume</div>
          <div className="mt-1 text-sm font-semibold tabular-nums">2.4M</div>
          <div className="mt-0.5 text-xs text-muted-foreground">Avg: 3.1M</div>
        </div>
        <div className="rounded-lg border border-border/50 p-4">
          <div className="text-[10px] text-muted-foreground">52 Week Range</div>
          <div className="mt-1 text-sm font-semibold tabular-nums">
            ₹2,210.00 — ₹3,420.00
          </div>
        </div>
      </div>

      <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">
        <span className="relative flex h-1.5 w-1.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-500 opacity-75" />
          <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-emerald-500" />
        </span>
        Live data — updates every 15 seconds
      </div>
    </div>
  );
}

export function WatchlistsMockup() {
  return (
    <div>
      <div className="mb-4">
        <div className="text-xs text-muted-foreground">Watchlist</div>
        <div className="text-lg font-semibold">Tech Stocks</div>
      </div>

      <div className="overflow-hidden rounded-lg border border-border/50">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-border/50 bg-secondary/20">
              <th className="px-4 py-2.5 text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                Ticker
              </th>
              <th className="px-4 py-2.5 text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                Price
              </th>
              <th className="px-4 py-2.5 text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                Change
              </th>
              <th className="px-4 py-2.5 text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                Signal
              </th>
            </tr>
          </thead>
          <tbody>
            {[
              { ticker: "RELIANCE.NS", price: "₹3,245.60", change: "+1.24%", signal: "BUY", signalColor: "text-emerald-500" },
              { ticker: "TCS.NS", price: "₹4,102.00", change: "-0.40%", signal: "NEUTRAL", signalColor: "text-muted-foreground" },
              { ticker: "INFY.NS", price: "₹1,892.30", change: "+2.10%", signal: "SELL", signalColor: "text-red-500" },
              { ticker: "HDFCBANK.NS", price: "₹1,678.50", change: "+0.80%", signal: "NEUTRAL", signalColor: "text-muted-foreground" },
            ].map((row) => (
              <tr key={row.ticker} className="border-b border-border/30 last:border-0">
                <td className="px-4 py-2.5 font-mono text-xs">{row.ticker}</td>
                <td className="px-4 py-2.5 font-mono text-xs tabular-nums">{row.price}</td>
                <td className={cn("px-4 py-2.5 font-mono text-xs tabular-nums", row.change.startsWith("+") ? "text-emerald-500" : "text-red-500")}>
                  {row.change}
                </td>
                <td className={cn("px-4 py-2.5 text-xs font-medium", row.signalColor)}>
                  {row.signal}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
