import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ShowcaseMockup } from "@/components/landing/showcase-mockup";

export function Hero() {
  return (
    <section className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden px-6 pb-16 pt-24">
      <div className="pointer-events-none absolute inset-0 bg-grid opacity-40 [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)]" />
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-background via-background/50 to-background" />

      <div className="relative z-10 mx-auto flex max-w-6xl flex-col items-center text-center">
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-border/50 bg-secondary/50 px-4 py-1.5 text-xs text-muted-foreground">
          <span className="relative flex h-1.5 w-1.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75" />
            <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-primary" />
          </span>
          Free during beta. No credit card needed.
        </div>

        <h1 className="animate-fade-in text-balance text-4xl font-semibold tracking-tight sm:text-5xl md:text-6xl lg:text-7xl">
          Analyze markets.{" "}
          <span className="text-primary">Build confidence</span>.
        </h1>

        <p className="animate-fade-in-up mt-6 max-w-2xl text-balance text-lg text-muted-foreground sm:text-xl">
          Real-time analytics and technical signals for smarter trading decisions.
          RSI, MACD, SMA, and EMA help you see what the data says before you act.
        </p>

        <div className="animate-fade-in-up mt-8 flex flex-col items-center gap-4 sm:flex-row">
          <Button size="lg" asChild className="h-12 px-8 text-base">
            <Link href="/register">Get Started &rarr;</Link>
          </Button>
          <Button size="lg" variant="outline" asChild className="h-12 px-8 text-base">
            <Link href="#features">Explore Features</Link>
          </Button>
        </div>

        <p className="mt-4 text-xs text-muted-foreground">No credit card required.</p>
      </div>

      <div className="relative z-10 mx-auto mt-16 w-full max-w-5xl">
        <div className="animate-fade-in-up animate-in-stagger-3">
          <ShowcaseMockup />
        </div>
      </div>
    </section>
  );
}
