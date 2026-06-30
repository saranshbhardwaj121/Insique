import { List, BarChart3, TrendingUp, Activity, Gauge, Settings } from "lucide-react";

const capabilities = [
  {
    icon: List,
    title: "Watchlists",
    description: "Organize tickers into named groups. Monitor sectors, strategies, or watch candidates.",
  },
  {
    icon: TrendingUp,
    title: "Market Data",
    description: "Live quotes and historical data. Price, volume, and day range give you full market context.",
  },
  {
    icon: BarChart3,
    title: "Analytics",
    description: "RSI, SMA, EMA, MACD. Every indicator visualized with clear interpretation.",
  },
  {
    icon: Activity,
    title: "Signals",
    description: "BUY, SELL, or NEUTRAL with confidence scoring. Four indicators, one unified verdict.",
  },
  {
    icon: Gauge,
    title: "Dashboard",
    description: "At-a-glance overview of your markets. Quick actions and real-time summaries.",
  },
  {
    icon: Settings,
    title: "Settings",
    description: "Profile management, dark mode, and preferences. Your workspace, your way.",
  },
];

export function CapabilitiesGrid() {
  return (
    <section className="py-24">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mb-12 text-center">
          <h2 className="text-balance text-2xl font-semibold tracking-tight sm:text-3xl">
            Everything you need to analyze markets
          </h2>
          <p className="mt-3 text-muted-foreground">
            No fluff. Every feature ships with a purpose.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {capabilities.map((cap) => (
            <div
              key={cap.title}
              className="group rounded-xl border border-border/50 bg-card p-5 transition-all duration-200 hover:-translate-y-0.5 hover:border-border/80 hover:shadow-sm"
            >
              <div className="mb-3 inline-flex h-10 w-10 items-center justify-center rounded-lg bg-secondary transition-all duration-300 group-hover:scale-110">
                <cap.icon className="h-4 w-4 text-primary" />
              </div>
              <h3 className="mb-1.5 text-sm font-semibold">{cap.title}</h3>
              <p className="text-sm leading-relaxed text-muted-foreground">
                {cap.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
