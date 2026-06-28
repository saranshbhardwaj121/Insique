import { Brain, GitMerge, Shield, BarChart3 } from "lucide-react";

const points = [
  {
    icon: GitMerge,
    title: "RSI + MACD + SMA + EMA",
    description: "Four indicators, one unified signal. No single metric is trusted alone.",
  },
  {
    icon: BarChart3,
    title: "Combined confidence scoring",
    description: "Single 0-100% score. Clear conviction level for every ticker. No guesswork.",
  },
  {
    icon: Brain,
    title: "Real-time or historical",
    description: "Analyze any timeframe the data supports. Today's move or last month's trend.",
  },
  {
    icon: Shield,
    title: "Your data, your control",
    description: "Private, secure, yours. JWT-authenticated access with no third-party sharing.",
  },
];

export function EvidenceSection() {
  return (
    <section className="border-y border-border/10 py-24">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mb-12 text-center">
          <h2 className="text-balance text-2xl font-semibold tracking-tight sm:text-3xl">
            Why evidence beats intuition
          </h2>
        </div>

        <div className="grid gap-6 sm:grid-cols-2">
          {points.map((point) => (
            <div key={point.title} className="flex gap-4 rounded-xl border border-border/50 bg-card p-5">
              <div className="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-secondary">
                <point.icon className="h-4 w-4 text-primary" />
              </div>
              <div>
                <h3 className="mb-1 text-sm font-semibold">{point.title}</h3>
                <p className="text-sm leading-relaxed text-muted-foreground">
                  {point.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        <div className="mx-auto mt-12 max-w-2xl text-center">
          <p className="text-lg leading-relaxed text-muted-foreground">
            Insique doesn&apos;t predict the future. It structures the present so you can decide.
          </p>
        </div>
      </div>
    </section>
  );
}
