"use client";

import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { HoldingWithMetrics } from "@/features/portfolio/types";

const COLORS = [
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
  "hsl(210, 70%, 60%)",
  "hsl(160, 60%, 55%)",
  "hsl(30, 80%, 60%)",
];

interface AllocationChartProps {
  holdings: HoldingWithMetrics[];
}

export function AllocationChart({ holdings }: AllocationChartProps) {
  const data = holdings
    .filter((h) => h.market_value != null && h.market_value > 0)
    .map((h) => ({
      name: h.ticker,
      value: Math.round(h.market_value! * 100) / 100,
    }));

  if (data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Allocation</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-64 text-sm text-muted-foreground">
          No holdings to visualize
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium">Allocation</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={2}
                dataKey="value"
              >
                {data.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip
                formatter={(value) => [`$${Number(value).toLocaleString()}`, "Value"]}
              />
              <Legend
                formatter={(value: string) => (
                  <span className="text-sm">{value}</span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
