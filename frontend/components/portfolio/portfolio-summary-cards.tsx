import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { PortfolioSummary } from "@/features/portfolio/types";

interface PortfolioSummaryCardsProps {
  summary: PortfolioSummary | undefined;
  isLoading: boolean;
}

function formatCurrency(value: number): string {
  const abs = Math.abs(value);
  const formatted = abs >= 1000
    ? `$${(abs / 1000).toFixed(1)}k`
    : `$${abs.toFixed(2)}`;
  return value < 0 ? `-${formatted}` : formatted;
}

export function PortfolioSummaryCards({ summary, isLoading }: PortfolioSummaryCardsProps) {
  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}>
            <CardHeader className="pb-2">
              <Skeleton className="h-4 w-20" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-24" />
              <Skeleton className="h-3 w-16 mt-1" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const s = summary;
  const isPositive = (s?.total_profit_loss ?? 0) >= 0;
  const pnlColor = s && s.total_holdings > 0
    ? isPositive ? "text-emerald-500" : "text-red-500"
    : "text-muted-foreground";

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Total Value</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {s ? formatCurrency(s.total_market_value) : "--"}
          </div>
          <p className="text-xs text-muted-foreground mt-1">Current market value</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Total Cost</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {s ? formatCurrency(s.total_cost_basis) : "--"}
          </div>
          <p className="text-xs text-muted-foreground mt-1">Total invested</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Profit / Loss</CardTitle>
        </CardHeader>
        <CardContent>
          <div className={`text-2xl font-bold ${pnlColor}`}>
            {s ? formatCurrency(s.total_profit_loss) : "--"}
          </div>
          <p className={`text-xs mt-1 ${pnlColor}`}>
            {s && s.total_holdings > 0
              ? `${s.total_profit_loss_percent >= 0 ? "+" : ""}${s.total_profit_loss_percent.toFixed(2)}%`
              : "Total return"}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Holdings</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {s ? s.total_holdings : "--"}
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            {s && s.total_holdings > 0
              ? `${s.profitable_holdings} gaining, ${s.losing_holdings} losing`
              : "Positions tracked"}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
