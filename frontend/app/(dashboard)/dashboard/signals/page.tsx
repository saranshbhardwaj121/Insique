import type { Metadata } from "next";
import { SignalsPageContent } from "@/components/signals/signals-page-content";

export const metadata: Metadata = {
  title: "Signals - Insique",
};

export default function SignalsPage({
  searchParams,
}: {
  searchParams: { ticker?: string };
}) {
  return <SignalsPageContent initialTicker={searchParams.ticker ?? null} />;
}
