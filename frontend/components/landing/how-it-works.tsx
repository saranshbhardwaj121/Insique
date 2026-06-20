import { Search, BarChart3, Target } from "lucide-react";

const steps = [
  {
    number: "01",
    icon: Search,
    title: "Add tickers",
    description: "Build your watchlist with the stocks you care about. Search by symbol or name.",
  },
  {
    number: "02",
    icon: BarChart3,
    title: "Get signals",
    description: "Insique analyzes RSI, MACD, SMA, and EMA on every ticker. A combined confidence score tells you the story.",
  },
  {
    number: "03",
    icon: Target,
    title: "Decide with confidence",
    description: "Every trade backed by data, not emotion. Clear signals. Transparent methodology. No black boxes.",
  },
];

export function HowItWorks() {
  return (
    <section className="border-t border-border/40 py-24" id="how-it-works">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mb-16 text-center">
          <h2 className="text-balance text-2xl font-semibold tracking-tight sm:text-3xl">
            How it works
          </h2>
          <p className="mt-3 text-muted-foreground">
            Three steps from curiosity to clarity.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-3">
          {steps.map((step, index) => (
            <div key={step.number} className="relative text-center">
              {index < steps.length - 1 && (
                <div className="absolute left-[60%] top-12 hidden h-px w-[80%] bg-gradient-to-r from-border to-transparent md:block" />
              )}
              <div className="mb-4 text-6xl font-bold tracking-tighter text-border/40">
                {step.number}
              </div>
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-secondary">
                <step.icon className="h-5 w-5 text-primary" />
              </div>
              <h3 className="mb-2 text-lg font-semibold">{step.title}</h3>
              <p className="text-sm leading-relaxed text-muted-foreground">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
