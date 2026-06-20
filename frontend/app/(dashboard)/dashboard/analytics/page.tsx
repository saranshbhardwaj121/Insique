import type { Metadata } from "next";
import { AnalyticsPageContent } from "@/components/analytics/analytics-page-content";

export const metadata: Metadata = {
  title: "Analytics - Insique",
};

export default function AnalyticsPage({
  searchParams,
}: {
  searchParams: { ticker?: string };
}) {
  return <AnalyticsPageContent initialTicker={searchParams.ticker ?? null} />;
}
