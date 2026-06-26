"use client";

import * as React from "react";
import { useAlertTriggersQuery } from "@/features/alerts/hooks";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

interface AlertTriggerHistoryProps {
  alertId: string;
}

export function AlertTriggerHistory({ alertId }: AlertTriggerHistoryProps) {
  const { data: triggers, isLoading, isError } = useAlertTriggersQuery(alertId);

  if (isLoading) {
    return (
      <p className="text-sm text-muted-foreground py-2">Loading triggers...</p>
    );
  }

  if (isError) {
    return (
      <p className="text-sm text-destructive py-2">Failed to load triggers</p>
    );
  }

  if (!triggers || triggers.length === 0) {
    return (
      <p className="text-sm text-muted-foreground py-2">No triggers recorded yet</p>
    );
  }

  return (
    <div>
      <div className="hidden sm:block rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Date</TableHead>
              <TableHead>Value</TableHead>
              <TableHead>Threshold</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {triggers.map((t) => (
              <TableRow key={t.id}>
                <TableCell className="text-xs">
                  {new Date(t.triggered_at).toLocaleString()}
                </TableCell>
                <TableCell>{t.triggered_value}</TableCell>
                <TableCell>{t.threshold}</TableCell>
                <TableCell>
                  <Badge variant="outline" className="text-xs">
                    Triggered
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <div className="sm:hidden space-y-2">
        {triggers.map((t) => (
          <div key={t.id} className="rounded-lg border p-3">
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">
                {new Date(t.triggered_at).toLocaleString()}
              </span>
              <Badge variant="outline" className="text-xs">Triggered</Badge>
            </div>
            <div className="flex gap-4 mt-2 text-sm">
              <div>
                <span className="text-xs text-muted-foreground">Value</span>
                <p className="font-mono">{t.triggered_value}</p>
              </div>
              <div>
                <span className="text-xs text-muted-foreground">Threshold</span>
                <p className="font-mono">{t.threshold}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
