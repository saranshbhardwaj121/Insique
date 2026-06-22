import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertCircle, RefreshCw } from "lucide-react";

interface PortfolioErrorStateProps {
  onRetry: () => void;
}

export function PortfolioErrorState({ onRetry }: PortfolioErrorStateProps) {
  return (
    <Card className="border-destructive/30">
      <CardContent className="flex flex-col items-center justify-center py-16 text-center">
        <AlertCircle className="h-12 w-12 text-destructive mb-4" />
        <h3 className="text-lg font-semibold mb-1">Failed to load portfolio</h3>
        <p className="text-sm text-muted-foreground mb-6 max-w-sm">
          We could not load your portfolio data. Please try again.
        </p>
        <Button onClick={onRetry} variant="outline" className="gap-1.5">
          <RefreshCw className="h-4 w-4" />
          Try Again
        </Button>
      </CardContent>
    </Card>
  );
}
