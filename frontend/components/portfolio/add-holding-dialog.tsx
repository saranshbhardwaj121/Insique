"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Search } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  createHoldingSchema,
  type CreateHoldingFormData,
} from "@/features/portfolio/schemas";
import { useCreateHoldingMutation } from "@/features/portfolio/hooks";
import { useTickerSearchQuery } from "@/features/search/hooks";

interface AddHoldingDialogProps {
  children?: React.ReactNode;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

export function AddHoldingDialog({
  children,
  open,
  onOpenChange,
}: AddHoldingDialogProps) {
  const [internalOpen, setInternalOpen] = React.useState(false);
  const isControlled = open !== undefined;
  const isOpen = isControlled ? open : internalOpen;
  const setIsOpen = isControlled ? (onOpenChange ?? setInternalOpen) : setInternalOpen;

  const [searchQuery, setSearchQuery] = React.useState("");
  const [showSuggestions, setShowSuggestions] = React.useState(false);
  const [highlightedIndex, setHighlightedIndex] = React.useState(-1);

  const { suggestions, isSearching } = useTickerSearchQuery(searchQuery);

  const createMutation = useCreateHoldingMutation();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
    setValue,
    watch,
  } = useForm<CreateHoldingFormData>({
    resolver: zodResolver(createHoldingSchema),
  });

  const selectedTicker = watch("ticker");

  const onSubmit = async (data: CreateHoldingFormData) => {
    try {
      await createMutation.mutateAsync({
        ticker: data.ticker.toUpperCase(),
        quantity: data.quantity,
        average_cost_basis: data.average_cost_basis,
      });
      reset();
      setSearchQuery("");
      setIsOpen(false);
    } catch {
      // Error toast handled by hook
    }
  };

  const commitTicker = (ticker: string) => {
    setValue("ticker", ticker.toUpperCase());
    setSearchQuery(ticker.toUpperCase());
    setShowSuggestions(false);
    setHighlightedIndex(-1);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestions || suggestions.length === 0) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlightedIndex((prev) =>
        prev < suggestions.length - 1 ? prev + 1 : 0
      );
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlightedIndex((prev) =>
        prev > 0 ? prev - 1 : suggestions.length - 1
      );
    } else if (e.key === "Enter" && highlightedIndex >= 0) {
      e.preventDefault();
      commitTicker(suggestions[highlightedIndex].ticker);
    } else if (e.key === "Escape") {
      setShowSuggestions(false);
      setHighlightedIndex(-1);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add holding</DialogTitle>
          <DialogDescription>
            Enter the ticker, quantity, and average cost basis
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2 relative">
            <Label htmlFor="ticker">Ticker</Label>
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                id="ticker"
                placeholder="e.g. AAPL"
                className="pl-8"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setValue("ticker", e.target.value.toUpperCase());
                  setShowSuggestions(true);
                  setHighlightedIndex(-1);
                }}
                onFocus={() => setShowSuggestions(true)}
                onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                onKeyDown={handleKeyDown}
                autoComplete="off"
              />
              {isSearching && (
                <Loader2 className="absolute right-2.5 top-2.5 h-4 w-4 animate-spin text-muted-foreground" />
              )}
            </div>
            {errors.ticker && (
              <p className="text-sm font-medium text-destructive">
                {errors.ticker.message}
              </p>
            )}
            {showSuggestions && suggestions.length > 0 && searchQuery.trim().length >= 1 && (
              <div className="absolute z-50 w-full mt-1 rounded-md border bg-popover shadow-md">
                {suggestions.map((item, index) => (
                  <button
                    key={item.ticker}
                    type="button"
                    className={`w-full text-left px-3 py-2 text-sm hover:bg-accent transition-colors ${
                      index === highlightedIndex ? "bg-accent" : ""
                    }`}
                    onMouseDown={() => commitTicker(item.ticker)}
                  >
                    <span className="font-mono font-medium">{item.ticker}</span>
                    {item.name && (
                      <span className="text-muted-foreground ml-2 text-xs">
                        {item.name}
                      </span>
                    )}
                    {item.exchange && (
                      <span className="text-muted-foreground ml-2 text-xs">
                        ({item.exchange})
                      </span>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="quantity">Quantity</Label>
            <Input
              id="quantity"
              type="number"
              step="0.01"
              min="0.01"
              placeholder="e.g. 10"
              {...register("quantity", { valueAsNumber: true })}
            />
            {errors.quantity && (
              <p className="text-sm font-medium text-destructive">
                {errors.quantity.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="average_cost_basis">Average Cost Basis ($)</Label>
            <Input
              id="average_cost_basis"
              type="number"
              step="0.01"
              min="0.01"
              placeholder="e.g. 150.00"
              {...register("average_cost_basis", { valueAsNumber: true })}
            />
            {errors.average_cost_basis && (
              <p className="text-sm font-medium text-destructive">
                {errors.average_cost_basis.message}
              </p>
            )}
          </div>

          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Adding...
                </>
              ) : (
                "Add Holding"
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
