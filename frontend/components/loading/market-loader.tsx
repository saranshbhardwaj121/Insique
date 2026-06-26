"use client";

import * as React from "react";
import { Signal } from "lucide-react";
import { cn } from "@/lib/utils";
import { AnimatedChart } from "@/components/loading/animated-chart";
import { LoadingMessage } from "@/components/loading/loading-message";

interface MarketLoaderProps {
  isLoading: boolean;
  children: React.ReactNode;
}

export function MarketLoader({ isLoading, children }: MarketLoaderProps) {
  const [showLoader, setShowLoader] = React.useState(true);
  const [phase, setPhase] = React.useState<"logo" | "chart" | "messages">("logo");
  const [fadeOut, setFadeOut] = React.useState(false);
  const [contentVisible, setContentVisible] = React.useState(false);
  const minTimerRef = React.useRef<ReturnType<typeof setTimeout> | null>(null);
  const contentReady = isLoading === false;

  React.useEffect(() => {
    const logo = setTimeout(() => setPhase("chart"), 500);
    const chart = setTimeout(() => setPhase("messages"), 1800);
    minTimerRef.current = setTimeout(() => {}, 2000);

    return () => {
      clearTimeout(logo);
      clearTimeout(chart);
    };
  }, []);

  const startTransition = React.useCallback(() => {
    setFadeOut(true);
    setTimeout(() => {
      setShowLoader(false);
      setContentVisible(true);
    }, 400);
  }, []);

  React.useEffect(() => {
    if (!contentReady || phase === "logo") return;
    if (phase === "chart") {
      const timer = setTimeout(startTransition, 500);
      return () => clearTimeout(timer);
    }
    startTransition();
  }, [contentReady, phase, startTransition]);

  return (
    <>
      {showLoader && (
        <div
          className={cn(
            "fixed inset-0 z-50 flex flex-col items-center justify-center bg-background transition-opacity duration-300",
            fadeOut ? "opacity-0" : "opacity-100"
          )}
        >
          <div className="flex flex-col items-center gap-6">
            <div
              className={cn(
                "flex items-center gap-3 transition-all duration-500",
                phase === "logo" ? "opacity-0 scale-95" : "opacity-100 scale-100"
              )}
            >
              <Signal className="h-6 w-6 text-primary" />
              <span className="text-lg font-semibold">Insique</span>
            </div>

            <AnimatedChart
              className={cn(
                "transition-all duration-500",
                phase === "logo" || phase === "chart"
                  ? "opacity-0 translate-y-2"
                  : "opacity-100 translate-y-0",
                phase === "logo" && "hidden"
              )}
            />

            <div
              className={cn(
                "transition-all duration-500",
                phase === "messages" ? "opacity-100 translate-y-0" : "opacity-0 translate-y-1",
                phase === "messages" ? "" : "hidden"
              )}
            >
              <LoadingMessage isActive={phase === "messages" && !fadeOut} />
            </div>
          </div>
        </div>
      )}

      <div
        className={cn(
          "transition-opacity duration-500",
          contentVisible ? "opacity-100" : "opacity-0"
        )}
      >
        {children}
      </div>
    </>
  );
}
