export function SocialProof() {
  return (
    <section className="border-y border-border/10 py-12">
      <div className="mx-auto max-w-6xl px-6">
        <p className="mb-8 text-center text-xs font-medium uppercase tracking-widest text-muted-foreground">
          Used by analysts at
        </p>
        <div className="flex flex-wrap items-center justify-center gap-x-12 gap-y-6 opacity-50 grayscale">
          {["Analysis", "Markets", "Trade", "Data", "Capital"].map((name) => (
            <div
              key={name}
              className="flex items-center gap-2 text-sm font-medium text-muted-foreground"
            >
              <div className="flex h-6 w-6 items-center justify-center rounded border border-border">
                <span className="text-[10px] font-bold">{name[0]}</span>
              </div>
              <span>{name}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
