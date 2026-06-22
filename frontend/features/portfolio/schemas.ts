import { z } from "zod";

export const createHoldingSchema = z.object({
  ticker: z
    .string()
    .min(1, "Ticker is required")
    .max(20, "Ticker must be 20 characters or less"),
  quantity: z.coerce
    .number()
    .positive("Quantity must be positive"),
  average_cost_basis: z.coerce
    .number()
    .positive("Average cost basis must be positive"),
});

export const updateHoldingSchema = z.object({
  quantity: z.coerce.number().positive("Quantity must be positive").optional(),
  average_cost_basis: z.coerce.number().positive("Average cost basis must be positive").optional(),
});

export type CreateHoldingFormData = z.infer<typeof createHoldingSchema>;
export type UpdateHoldingFormData = z.infer<typeof updateHoldingSchema>;
