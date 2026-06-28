import Link from "next/link";
import { Button } from "@/components/ui/button";

export function FinalCTA() {
  return (
    <section className="border-t border-border/10 py-24">
      <div className="mx-auto max-w-3xl px-6 text-center">
        <h2 className="text-balance text-2xl font-semibold tracking-tight sm:text-3xl">
          Stop guessing. Start deciding.
        </h2>
        <p className="mt-4 text-lg text-muted-foreground">
          Join analysts who trade with evidence, not emotion.
        </p>
        <div className="mt-8 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <Button size="lg" asChild className="h-12 px-8 text-base">
            <Link href="/register">Try Insique Free &rarr;</Link>
          </Button>
          <Button size="lg" variant="outline" asChild className="h-12 px-8 text-base">
            <Link href="/login">Sign in</Link>
          </Button>
        </div>
        <p className="mt-4 text-xs text-muted-foreground">
          No credit card required. Free during beta.
        </p>
      </div>
    </section>
  );
}
