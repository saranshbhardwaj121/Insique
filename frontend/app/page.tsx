import Link from "next/link";
import { Signal } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex h-14 items-center justify-between border-b px-6">
        <div className="flex items-center gap-2 font-semibold">
          <Signal className="h-5 w-5 text-primary" />
          <span>Insique</span>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" asChild>
            <Link href="/login">Sign in</Link>
          </Button>
          <Button asChild>
            <Link href="/register">Get started</Link>
          </Button>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center p-8 text-center">
        <Signal className="h-16 w-16 text-primary mb-6" />
        <h1 className="text-4xl font-bold tracking-tight mb-3">
          Market Intelligence Platform
        </h1>
        <p className="text-lg text-muted-foreground max-w-md mb-8">
          Analyze stocks, maintain watchlists, track trades, and receive structured technical insights.
        </p>
        <div className="flex gap-4">
          <Button size="lg" asChild>
            <Link href="/register">Get started</Link>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <Link href="/login">Sign in</Link>
          </Button>
        </div>
      </main>
    </div>
  );
}
