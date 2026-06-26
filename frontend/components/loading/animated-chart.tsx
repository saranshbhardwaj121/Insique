"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

const CHART_POINTS = [
  { x: 0, y: 65 },
  { x: 12, y: 58 },
  { x: 24, y: 62 },
  { x: 36, y: 48 },
  { x: 48, y: 52 },
  { x: 60, y: 40 },
  { x: 72, y: 45 },
  { x: 84, y: 32 },
  { x: 96, y: 36 },
  { x: 108, y: 25 },
  { x: 120, y: 18 },
  { x: 132, y: 22 },
  { x: 144, y: 10 },
  { x: 156, y: 8 },
];

const linePath = CHART_POINTS.map((p, i) => {
  const cmd = i === 0 ? "M" : "L";
  return `${cmd}${p.x} ${p.y}`;
}).join(" ");

const lastPoint = CHART_POINTS[CHART_POINTS.length - 1];

interface AnimatedChartProps {
  className?: string;
}

export function AnimatedChart({ className }: AnimatedChartProps) {
  return (
    <div className={cn("relative w-full max-w-[200px] h-20", className)}>
      <svg
        viewBox="0 0 160 72"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full"
        aria-hidden="true"
      >
        <defs>
          <linearGradient id="chart-glow" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity="0.3" />
            <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity="0" />
          </linearGradient>
          <filter id="glow-dot">
            <feGaussianBlur stdDeviation="2.5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <rect x="0" y="0" width="160" height="72" fill="url(#chart-glow)" rx="4" />

        <path
          d={linePath}
          stroke="hsl(var(--primary))"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
          className="animate-chart-line"
          style={{
            strokeDasharray: "400",
            strokeDashoffset: "400",
          }}
        />

        <path
          d={linePath}
          stroke="hsl(var(--primary) / 0.15)"
          strokeWidth="6"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
          className="animate-chart-line"
          style={{
            strokeDasharray: "400",
            strokeDashoffset: "400",
          }}
        />

        <circle
          cx={lastPoint.x}
          cy={lastPoint.y}
          r="3"
          fill="hsl(var(--primary))"
          className="animate-chart-dot"
          filter="url(#glow-dot)"
          style={{ opacity: 0 }}
        />

        <line x1="0" y1="72" x2="160" y2="72" stroke="hsl(var(--border))" strokeWidth="1" strokeDasharray="2 2" />
        <line x1="0" y1="36" x2="160" y2="36" stroke="hsl(var(--border) / 0.5)" strokeWidth="0.5" strokeDasharray="2 4" />
        <line x1="80" y1="0" x2="80" y2="72" stroke="hsl(var(--border) / 0.3)" strokeWidth="0.5" strokeDasharray="2 4" />
      </svg>
    </div>
  );
}
