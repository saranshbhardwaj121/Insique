import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-border/40 py-12">
      <div className="mx-auto max-w-6xl px-6">
        <div className="flex flex-col items-center justify-between gap-8 sm:flex-row">
          <div>
            <div className="flex items-center gap-2">
              <div className="flex h-6 w-6 items-center justify-center rounded bg-primary">
                <span className="text-[10px] font-bold text-primary-foreground">I</span>
              </div>
              <span className="text-sm font-semibold">Insique</span>
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              Insight + Intelligence + Unique
            </p>
          </div>

          <div className="flex gap-8 text-xs text-muted-foreground">
            <div>
              <p className="mb-2 text-[10px] font-medium uppercase tracking-widest">Product</p>
              <div className="space-y-1.5">
                <Link href="#features" className="block hover:text-foreground">
                  Features
                </Link>
                <Link href="#how-it-works" className="block hover:text-foreground">
                  How it works
                </Link>
              </div>
            </div>
            <div>
              <p className="mb-2 text-[10px] font-medium uppercase tracking-widest">Company</p>
              <div className="space-y-1.5">
                <span className="block text-muted-foreground/60">About</span>
                <span className="block text-muted-foreground/60">Contact</span>
              </div>
            </div>
            <div>
              <p className="mb-2 text-[10px] font-medium uppercase tracking-widest">Legal</p>
              <div className="space-y-1.5">
                <span className="block text-muted-foreground/60">Privacy</span>
                <span className="block text-muted-foreground/60">Terms</span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 flex flex-col items-center justify-between gap-2 border-t border-border/30 pt-6 text-[10px] text-muted-foreground/60 sm:flex-row">
          <p>&copy; {new Date().getFullYear()} Insique. All rights reserved.</p>
          <p>Built with FastAPI + Next.js + PostgreSQL</p>
        </div>
      </div>
    </footer>
  );
}
