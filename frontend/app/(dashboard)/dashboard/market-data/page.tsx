import { MarketDataPageContent } from "@/components/market-data/market-data-page-content";

export default function MarketDataPage({
  searchParams,
}: {
  searchParams: { ticker?: string };
}) {
  return <MarketDataPageContent initialTicker={searchParams.ticker ?? null} />;
}
