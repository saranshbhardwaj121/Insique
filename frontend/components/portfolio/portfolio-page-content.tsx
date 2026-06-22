"use client";

import * as React from "react";
import { usePortfolioSummaryQuery } from "@/features/portfolio/hooks";
import { PortfolioSummaryCards } from "./portfolio-summary-cards";
import { AllocationChart } from "./allocation-chart";
import { HoldingsTable } from "./holdings-table";
import { AddHoldingDialog } from "./add-holding-dialog";
import { EditHoldingDialog } from "./edit-holding-dialog";
import { DeleteHoldingDialog } from "./delete-holding-dialog";
import { PortfolioSkeleton } from "./portfolio-skeleton";
import { PortfolioEmptyState } from "./portfolio-empty-state";
import { PortfolioErrorState } from "./portfolio-error-state";
import type { HoldingWithMetrics } from "@/features/portfolio/types";

export function PortfolioPageContent() {
  const { data: summary, isLoading, isError, refetch } = usePortfolioSummaryQuery();

  const [addDialogOpen, setAddDialogOpen] = React.useState(false);
  const [editTarget, setEditTarget] = React.useState<HoldingWithMetrics | null>(null);
  const [deleteTarget, setDeleteTarget] = React.useState<HoldingWithMetrics | null>(null);

  if (isLoading) return <PortfolioSkeleton />;
  if (isError) return <PortfolioErrorState onRetry={() => refetch()} />;

  const holdings = summary?.holdings ?? [];
  const isEmpty = holdings.length === 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Portfolio</h1>
          <p className="text-muted-foreground">
            Track your holdings and portfolio performance
          </p>
        </div>
      </div>

      <PortfolioSummaryCards summary={summary} isLoading={false} />

      {isEmpty ? (
        <PortfolioEmptyState onAddHolding={() => setAddDialogOpen(true)} />
      ) : (
        <>
          <AllocationChart holdings={holdings} />
          <HoldingsTable
            holdings={holdings}
            isLoading={false}
            onAdd={() => setAddDialogOpen(true)}
            onEdit={(h) => setEditTarget(h)}
            onDelete={(h) => setDeleteTarget(h)}
          />
        </>
      )}

      <AddHoldingDialog open={addDialogOpen} onOpenChange={setAddDialogOpen}>
        <span />
      </AddHoldingDialog>

      {editTarget && (
        <EditHoldingDialog
          holding={editTarget}
          open={!!editTarget}
          onOpenChange={(open) => { if (!open) setEditTarget(null); }}
        />
      )}

      {deleteTarget && (
        <DeleteHoldingDialog
          holding={deleteTarget}
          open={!!deleteTarget}
          onOpenChange={(open) => { if (!open) setDeleteTarget(null); }}
        />
      )}
    </div>
  );
}
