export interface Holding {
  id: string;
  ticker: string;
  quantity: number;
  average_cost_basis: number;
  created_at: string;
  updated_at: string;
}

export interface HoldingWithMetrics {
  id: string;
  ticker: string;
  quantity: number;
  average_cost_basis: number;
  current_price: number | null;
  market_value: number | null;
  profit_loss: number | null;
  profit_loss_percent: number | null;
  allocation_percent: number | null;
  created_at: string;
  updated_at: string;
}

export interface PortfolioSummary {
  total_market_value: number;
  total_cost_basis: number;
  total_profit_loss: number;
  total_profit_loss_percent: number;
  total_holdings: number;
  profitable_holdings: number;
  losing_holdings: number;
  holdings: HoldingWithMetrics[];
}

export interface CreateHoldingPayload {
  ticker: string;
  quantity: number;
  average_cost_basis: number;
}

export interface UpdateHoldingPayload {
  quantity?: number;
  average_cost_basis?: number;
}
