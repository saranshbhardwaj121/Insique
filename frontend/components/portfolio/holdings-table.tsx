"use client";

import * as React from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Pencil, Trash2, Plus } from "lucide-react";
import type { HoldingWithMetrics } from "@/features/portfolio/types";

interface HoldingsTableProps {
  holdings: HoldingWithMetrics[];
  isLoading: boolean;
  onAdd: () => void;
  onEdit: (holding: HoldingWithMetrics) => void;
  onDelete: (holding: HoldingWithMetrics) => void;
}

function formatCurrency(value: number | null): string {
  if (value === null || value === undefined) return "--";
  const abs = Math.abs(value);
  const formatted = abs.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  return `${value < 0 ? "-" : ""}$${formatted}`;
}

function formatPct(value: number | null): string {
  if (value === null || value === undefined) return "--";
  return `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;
}

function pnlColor(value: number | null | undefined): string {
  if (value === null || value === undefined) return "";
  return value > 0 ? "text-emerald-500" : value < 0 ? "text-red-500" : "";
}

export function HoldingsTable({
  holdings,
  isLoading,
  onAdd,
  onEdit,
  onDelete,
}: HoldingsTableProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-12 w-full rounded-lg" />
        ))}
      </div>
    );
  }

  if (holdings.length === 0) {
    return null;
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold">
          Holdings ({holdings.length})
        </h2>
        <Button onClick={onAdd} size="sm" className="gap-1.5">
          <Plus className="h-3.5 w-3.5" />
          Add Holding
        </Button>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-24 font-mono">Ticker</TableHead>
              <TableHead className="text-right">Qty</TableHead>
              <TableHead className="text-right">Avg Cost</TableHead>
              <TableHead className="text-right">Last Price</TableHead>
              <TableHead className="text-right">Market Value</TableHead>
              <TableHead className="text-right">P&L</TableHead>
              <TableHead className="text-right">P&L %</TableHead>
              <TableHead className="text-right">Alloc %</TableHead>
              <TableHead className="w-20">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {holdings.map((h) => (
              <TableRow key={h.id}>
                <TableCell className="font-mono font-medium">
                  {h.ticker}
                </TableCell>
                <TableCell className="text-right font-mono text-sm">
                  {h.quantity}
                </TableCell>
                <TableCell className="text-right font-mono text-sm">
                  {formatCurrency(h.average_cost_basis)}
                </TableCell>
                <TableCell className="text-right font-mono text-sm">
                  {formatCurrency(h.current_price)}
                </TableCell>
                <TableCell className="text-right font-mono text-sm">
                  {formatCurrency(h.market_value)}
                </TableCell>
                <TableCell className={`text-right font-mono text-sm ${pnlColor(h.profit_loss)}`}>
                  {formatCurrency(h.profit_loss)}
                </TableCell>
                <TableCell className={`text-right font-mono text-sm ${pnlColor(h.profit_loss_percent)}`}>
                  {formatPct(h.profit_loss_percent)}
                </TableCell>
                <TableCell className="text-right font-mono text-sm">
                  {h.allocation_percent != null ? `${h.allocation_percent.toFixed(1)}%` : "--"}
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => onEdit(h)}
                      title="Edit holding"
                    >
                      <Pencil className="h-3.5 w-3.5" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-muted-foreground hover:text-destructive"
                      onClick={() => onDelete(h)}
                      title="Remove holding"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
