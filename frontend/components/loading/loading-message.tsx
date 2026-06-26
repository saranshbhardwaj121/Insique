"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

const MESSAGES = [
  "Analyzing today's market...",
  "Fetching portfolio...",
  "Scanning watchlists...",
  "Computing RSI...",
  "Calculating momentum...",
  "Generating trading signals...",
  "Finding today's movers...",
  "Preparing dashboard...",
  "Almost ready...",
];

interface LoadingMessageProps {
  isActive: boolean;
}

export function LoadingMessage({ isActive }: LoadingMessageProps) {
  const [index, setIndex] = React.useState(0);
  const [visible, setVisible] = React.useState(true);
  const intervalRef = React.useRef<ReturnType<typeof setInterval> | null>(null);

  React.useEffect(() => {
    if (!isActive) {
      if (intervalRef.current) clearInterval(intervalRef.current);
      return;
    }

    const interval = setInterval(() => {
      setVisible(false);
      setTimeout(() => {
        setIndex((prev) => (prev + 1) % MESSAGES.length);
        setVisible(true);
      }, 200);
    }, 900);

    intervalRef.current = interval;
    return () => clearInterval(interval);
  }, [isActive]);

  return (
    <div className="h-5 flex items-center justify-center">
      <p
        className={cn(
          "text-sm text-muted-foreground transition-opacity duration-300",
          visible ? "opacity-100" : "opacity-0"
        )}
        aria-live="polite"
      >
        {MESSAGES[index]}
      </p>
    </div>
  );
}
