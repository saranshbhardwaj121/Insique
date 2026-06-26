"use client";

import * as React from "react";
import { Loader2, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { TickerSearchForm } from "@/components/shared/ticker-search-form";
import { useCreateAlert } from "@/features/alerts/hooks";
import type { AlertType, AlertOperator } from "@/features/alerts/types";

const ALERT_TYPES: { value: AlertType; label: string }[] = [
  { value: "price", label: "Price" },
  { value: "signal", label: "Signal" },
  { value: "confidence", label: "Confidence" },
  { value: "rsi", label: "RSI" },
];

const OPERATORS: { value: AlertOperator; label: string }[] = [
  { value: "gt", label: ">" },
  { value: "lt", label: "<" },
  { value: "gte", label: ">=" },
  { value: "lte", label: "<=" },
  { value: "eq", label: "=" },
];

const OPERATOR_LABELS: Record<AlertOperator, string> = {
  gt: "greater than",
  lt: "less than",
  gte: "greater than or equal to",
  lte: "less than or equal to",
  eq: "equal to",
};

export function AlertCreateForm({ onSuccess }: { onSuccess?: () => void }) {
  const [ticker, setTicker] = React.useState("");
  const [alertType, setAlertType] = React.useState<AlertType>("price");
  const [operator, setOperator] = React.useState<AlertOperator>("gt");
  const [threshold, setThreshold] = React.useState("");
  const [rsiWindow, setRsiWindow] = React.useState("14");

  const createAlert = useCreateAlert();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticker || !threshold) return;

    const parameters = alertType === "rsi" ? { rsi_window: parseInt(rsiWindow, 10) } : undefined;

    try {
      await createAlert.mutateAsync({
        ticker: ticker.toUpperCase(),
        alert_type: alertType,
        operator,
        threshold: parseFloat(threshold),
        parameters,
      });
      setThreshold("");
      setAlertType("price");
      setOperator("gt");
      setTicker("");
      onSuccess?.();
    } catch {
      // handled by hook
    }
  };

  const isValid = ticker && threshold && !isNaN(parseFloat(threshold));

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border p-4">
      <div className="space-y-2">
        <Label htmlFor="alert-ticker">Ticker</Label>
        <TickerSearchForm
          compact
          placeholder="Search ticker..."
          onSubmit={setTicker}
          buttonLabel="Select"
        />
        {ticker && (
          <p className="text-sm text-muted-foreground">Selected: {ticker}</p>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="alert-type">Type</Label>
          <Select
            value={alertType}
            onValueChange={(v) => setAlertType(v as AlertType)}
          >
            <SelectTrigger id="alert-type">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {ALERT_TYPES.map((t) => (
                <SelectItem key={t.value} value={t.value}>
                  {t.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="alert-operator">Condition</Label>
          <Select
            value={operator}
            onValueChange={(v) => setOperator(v as AlertOperator)}
          >
            <SelectTrigger id="alert-operator">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {OPERATORS.map((o) => (
                <SelectItem key={o.value} value={o.value}>
                  {o.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="alert-threshold">
          Threshold ({alertType === "price" ? "price" : alertType === "confidence" ? "0.0 - 1.0" : alertType === "rsi" ? "0 - 100" : "-6 to 6"})
        </Label>
        <Input
          id="alert-threshold"
          type="number"
          step="any"
          placeholder={
            alertType === "confidence"
              ? "e.g. 0.8"
              : alertType === "rsi"
              ? "e.g. 30"
              : alertType === "signal"
              ? "e.g. 2"
              : "e.g. 3500"
          }
          value={threshold}
          onChange={(e) => setThreshold(e.target.value)}
        />
      </div>

      {alertType === "rsi" && (
        <div className="space-y-2">
          <Label htmlFor="rsi-window">RSI Window</Label>
          <Input
            id="rsi-window"
            type="number"
            min={2}
            max={250}
            value={rsiWindow}
            onChange={(e) => setRsiWindow(e.target.value)}
          />
        </div>
      )}

      <p className="text-sm text-muted-foreground">
        Trigger when {ticker || "ticker"} {alertType} {OPERATOR_LABELS[operator]}{" "}
        {threshold || "..."}
      </p>

      <Button type="submit" disabled={!isValid || createAlert.isPending} className="w-full">
        {createAlert.isPending ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Creating...
          </>
        ) : (
          <>
            <Plus className="mr-2 h-4 w-4" />
            Create Alert
          </>
        )}
      </Button>
    </form>
  );
}
