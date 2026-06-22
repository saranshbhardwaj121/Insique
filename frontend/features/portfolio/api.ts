import { clientFetch } from "@/lib/api/client";
import { API_ROUTES } from "@/lib/api/routes";
import type { Holding, PortfolioSummary, CreateHoldingPayload, UpdateHoldingPayload } from "./types";

export async function listHoldings(): Promise<Holding[]> {
  return clientFetch<Holding[]>(API_ROUTES.PORTFOLIO.HOLDINGS);
}

export async function createHolding(payload: CreateHoldingPayload): Promise<Holding> {
  return clientFetch<Holding>(API_ROUTES.PORTFOLIO.HOLDINGS, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateHolding(id: string, payload: UpdateHoldingPayload): Promise<Holding> {
  return clientFetch<Holding>(API_ROUTES.PORTFOLIO.HOLDING(id), {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteHolding(id: string): Promise<void> {
  await clientFetch<void>(API_ROUTES.PORTFOLIO.HOLDING(id), {
    method: "DELETE",
  });
}

export async function getPortfolioSummary(): Promise<PortfolioSummary> {
  return clientFetch<PortfolioSummary>(API_ROUTES.PORTFOLIO.SUMMARY);
}
