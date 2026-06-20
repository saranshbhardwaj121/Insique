"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { ChevronDown } from "lucide-react";

const faqs = [
  {
    q: "How are signals calculated?",
    a: "Four technical indicators: RSI for momentum, MACD for trend direction, SMA and EMA for moving averages. Each indicator votes, and the combined confidence score reflects how many agree and how strongly.",
  },
  {
    q: "Is my data private?",
    a: "Yes. Your watchlists, preferences, and account data are protected with JWT-based authentication. We never share or sell your data. No third-party access.",
  },
  {
    q: "What markets do you support?",
    a: "Currently NSE India via Yahoo Finance integration. US market support is on the roadmap.",
  },
  {
    q: "Can I paper trade?",
    a: "Not yet. Paper trading is our top-priority feature and is currently in active development. Join the waitlist to be notified when it ships.",
  },
  {
    q: "Do I need trading experience?",
    a: "No. If you understand that decisions should be based on data, Insique gives you the tools. Every signal includes an explanation of why.",
  },
  {
    q: "What does 'confidence' mean?",
    a: "Confidence is the percentage of indicator agreement weighted by signal strength. 4/4 indicators agreeing on a strong trend = higher confidence. 2/4 with mixed signals = lower confidence.",
  },
];

export function FAQ() {
  const [openIndex, setOpenIndex] = React.useState<number | null>(null);

  return (
    <section className="border-t border-border/40 py-24">
      <div className="mx-auto max-w-3xl px-6">
        <div className="mb-12 text-center">
          <h2 className="text-balance text-2xl font-semibold tracking-tight sm:text-3xl">
            Questions? We have answers.
          </h2>
        </div>

        <div className="space-y-2">
          {faqs.map((faq, index) => (
            <div
              key={index}
              className="rounded-xl border border-border/50 bg-card"
            >
              <button
                onClick={() => setOpenIndex(openIndex === index ? null : index)}
                className="flex w-full items-center justify-between px-5 py-4 text-left text-sm font-medium"
              >
                <span>{faq.q}</span>
                <ChevronDown
                  className={cn(
                    "h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200",
                    openIndex === index && "rotate-180"
                  )}
                />
              </button>
              <div
                className={cn(
                  "overflow-hidden transition-all duration-300",
                  openIndex === index ? "max-h-48" : "max-h-0"
                )}
              >
                <p className="border-t border-border/50 px-5 py-4 text-sm leading-relaxed text-muted-foreground">
                  {faq.a}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
