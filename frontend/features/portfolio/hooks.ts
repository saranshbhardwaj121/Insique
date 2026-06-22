"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { queryKeys } from "@/lib/api/query-keys";
import {
  listHoldings,
  createHolding,
  updateHolding,
  deleteHolding,
  getPortfolioSummary,
} from "./api";
import type { CreateHoldingPayload, UpdateHoldingPayload } from "./types";

export function useHoldingsQuery() {
  return useQuery({
    queryKey: queryKeys.portfolio.holdings.all,
    queryFn: listHoldings,
    staleTime: 120_000,
  });
}

export function usePortfolioSummaryQuery() {
  return useQuery({
    queryKey: queryKeys.portfolio.summary,
    queryFn: getPortfolioSummary,
    staleTime: 60_000,
  });
}

export function useCreateHoldingMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateHoldingPayload) => createHolding(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.portfolio.holdings.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.portfolio.summary });
      toast.success("Holding added");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to add holding");
    },
  });
}

export function useUpdateHoldingMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: UpdateHoldingPayload }) =>
      updateHolding(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.portfolio.holdings.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.portfolio.summary });
      toast.success("Holding updated");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to update holding");
    },
  });
}

export function useDeleteHoldingMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => deleteHolding(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.portfolio.holdings.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.portfolio.summary });
      toast.success("Holding removed");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to remove holding");
    },
  });
}
