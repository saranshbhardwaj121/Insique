import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PieChart, Plus } from "lucide-react";

interface PortfolioEmptyStateProps {
  onAddHolding: () => void;
}

export function PortfolioEmptyState({ onAddHolding }: PortfolioEmptyStateProps) {
  return (
    <Card className="border-dashed">
      <CardContent className="flex flex-col items-center justify-center py-16 text-center">
        <PieChart className="h-12 w-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-semibold mb-1">No holdings tracked yet</h3>
        <p className="text-sm text-muted-foreground mb-6 max-w-sm">
          Add your first holding to see portfolio performance, allocation, and profit/loss tracking.
        </p>
        <Button onClick={onAddHolding} className="gap-1.5">
          <Plus className="h-4 w-4" />
          Add Holding
        </Button>
      </CardContent>
    </Card>
  );
}
