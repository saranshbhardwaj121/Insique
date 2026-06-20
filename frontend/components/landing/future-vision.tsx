import { Wallet, History, BrainCircuit } from "lucide-react";

const features = [
  {
    icon: Wallet,
    title: "Paper Trading",
    status: "In development",
    description:
      "Validate signals without risking capital. Test strategies in real-time with virtual portfolios. Track win rate, drawdown, and total return.",
    statusClass: "text-amber-500 bg-amber-500/10 border-amber-500/20",
  },
  {
    icon: History,
    title: "Backtesting",
    status: "On the roadmap",
    description:
      "Run your strategy against years of historical data. See win rate, drawdown, Sharpe ratio — before you commit real capital.",
    statusClass: "text-primary bg-primary/10 border-primary/20",
  },
  {
    icon: BrainCircuit,
    title: "ML Forecasting",
    status: "Research phase",
    description:
      "Pattern recognition meets technical analysis. Bullish and bearish probability scores powered by machine learning.",
    statusClass: "text-muted-foreground bg-secondary border-border/50",
  },
];

export function FutureVision() {
  return (
    <section className="py-24">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mb-12 text-center">
          <h2 className="text-balance text-2xl font-semibold tracking-tight sm:text-3xl">
            Built for what&apos;s next
          </h2>
          <p className="mt-3 text-muted-foreground">
            The foundation is ready. The vision extends further.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="rounded-xl border border-border/50 bg-card p-6"
            >
              <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-lg bg-secondary">
                <feature.icon className="h-4 w-4 text-primary" />
              </div>
              <h3 className="mb-2 text-base font-semibold">{feature.title}</h3>
              <span
                className={`mb-3 inline-block rounded-md border px-2 py-0.5 text-[11px] font-medium ${feature.statusClass}`}
              >
                {feature.status}
              </span>
              <p className="text-sm leading-relaxed text-muted-foreground">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
