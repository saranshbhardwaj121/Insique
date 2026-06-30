import Link from "next/link";
import { Button } from "@/components/ui/button";

export function FinalCTA() {
  return (
    <section className="border-t border-border/10 py-24">
      <div className="mx-auto max-w-3xl px-6 text-center">
        <h2 className="text-balance text-2xl font-semibold tracking-tight sm:text-3xl">
          Ready to trade with confidence?
        </h2>
        <p className="mt-4 text-lg text-muted-foreground">
          Try Insique free during beta. No credit card required.
        </p>
        <div className="mt-8 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <Button size="lg" asChild className="h-12 px-8 text-base">
            <Link href="/register">Get Started &rarr;</Link>
          </Button>
          <Button size="lg" variant="outline" asChild className="h-12 px-8 text-base">
            <Link href="/login">Sign in</Link>
          </Button>
        </div>
        <p className="mt-4 text-xs text-muted-foreground">
          Join 1,200+ traders already using Insique.
        </p>
      </div>
    </section>
  );
}
