import { Metadata } from "next";
import { PortfolioPageContent } from "@/components/portfolio/portfolio-page-content";

export const metadata: Metadata = {
  title: "Portfolio - Insique",
};

export default function PortfolioPage() {
  return <PortfolioPageContent />;
}
