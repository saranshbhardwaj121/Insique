import { Metadata } from "next";
import { WatchlistsPageContent } from "@/components/watchlists/watchlists-page-content";

export const metadata: Metadata = {
  title: "Watchlists - Insique",
};

export default function WatchlistsPage() {
  return <WatchlistsPageContent />;
}
