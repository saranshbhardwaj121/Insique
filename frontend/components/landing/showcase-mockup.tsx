import { Signal, TrendingUp, BarChart3, Activity } from "lucide-react";

export function ShowcaseMockup() {
  return (
    <div className="relative overflow-hidden rounded-xl border border-border/50 bg-card shadow-2xl">
      <div className="flex items-center gap-2 border-b border-border/50 px-4 py-2.5">
        <div className="flex gap-1.5">
          <div className="h-2.5 w-2.5 rounded-full bg-red-500/70" />
          <div className="h-2.5 w-2.5 rounded-full bg-yellow-500/70" />
          <div className="h-2.5 w-2.5 rounded-full bg-green-500/70" />
        </div>
        <div className="ml-3 flex items-center gap-1.5 text-xs text-muted-foreground">
          <Signal className="h-3 w-3" />
          <span>Insique — Dashboard</span>
        </div>
      </div>

      <div className="grid grid-cols-[240px_1fr]">
        <div className="border-r border-border/50 p-4">
          <div className="mb-4 space-y-1">
            <div className="text-xs font-medium text-muted-foreground">Navigation</div>
            <div className="flex items-center gap-2 rounded-md bg-secondary/50 px-3 py-2 text-xs font-medium text-foreground">
              <BarChart3 className="h-3.5 w-3.5 text-primary" />
              <span>Signals</span>
            </div>
            <div className="flex items-center gap-2 rounded-md px-3 py-2 text-xs text-muted-foreground">
              <TrendingUp className="h-3.5 w-3.5" />
              <span>Analytics</span>
            </div>
            <div className="flex items-center gap-2 rounded-md px-3 py-2 text-xs text-muted-foreground">
              <Activity className="h-3.5 w-3.5" />
              <span>Market Data</span>
            </div>
          </div>
        </div>

        <div className="p-4">
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
              <div className="mt-0.5 text-sm font-semibold">Bullish</div>
              <div className="text-[10px] text-emerald-500">Crossover ↑</div>
            </div>
            <div className="rounded-lg border border-border/50 bg-secondary/20 p-3">
              <div className="text-[10px] text-muted-foreground">SMA (20)</div>
              <div className="mt-0.5 text-sm font-semibold">↑ Uptrend</div>
              <div className="text-[10px] text-emerald-500">Price above</div>
            </div>
            <div className="rounded-lg border border-border/50 bg-secondary/20 p-3">
              <div className="text-[10px] text-muted-foreground">EMA (50)</div>
              <div className="mt-0.5 text-sm font-semibold">↑ Uptrend</div>
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
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <div className="h-1.5 w-24 rounded-full bg-border">
                <div className="h-full w-[78%] rounded-full bg-emerald-500 transition-all" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
