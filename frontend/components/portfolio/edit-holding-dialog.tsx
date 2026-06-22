"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2 } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  updateHoldingSchema,
  type UpdateHoldingFormData,
} from "@/features/portfolio/schemas";
import { useUpdateHoldingMutation } from "@/features/portfolio/hooks";
import type { Holding } from "@/features/portfolio/types";

interface EditHoldingDialogProps {
  holding: Holding;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function EditHoldingDialog({
  holding,
  open,
  onOpenChange,
}: EditHoldingDialogProps) {
  const updateMutation = useUpdateHoldingMutation();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<UpdateHoldingFormData>({
    resolver: zodResolver(updateHoldingSchema),
    defaultValues: {
      quantity: holding.quantity,
      average_cost_basis: holding.average_cost_basis,
    },
  });

  React.useEffect(() => {
    if (open) {
      reset({
        quantity: holding.quantity,
        average_cost_basis: holding.average_cost_basis,
      });
    }
  }, [open, holding, reset]);

  const onSubmit = async (data: UpdateHoldingFormData) => {
    try {
      await updateMutation.mutateAsync({
        id: holding.id,
        payload: data,
      });
      onOpenChange(false);
    } catch {
      // Error toast handled by hook
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit {holding.ticker}</DialogTitle>
          <DialogDescription>
            Update your position details
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label>Ticker</Label>
            <p className="text-sm font-mono font-medium">{holding.ticker}</p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="edit-quantity">Quantity</Label>
            <Input
              id="edit-quantity"
              type="number"
              step="0.01"
              min="0.01"
              {...register("quantity", { valueAsNumber: true })}
            />
            {errors.quantity && (
              <p className="text-sm font-medium text-destructive">
                {errors.quantity.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="edit-avg-cost">Average Cost Basis ($)</Label>
            <Input
              id="edit-avg-cost"
              type="number"
              step="0.01"
              min="0.01"
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
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                "Save Changes"
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
