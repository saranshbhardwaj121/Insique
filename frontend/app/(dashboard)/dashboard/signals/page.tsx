import type { Metadata } from "next";
import { SignalsPageContent } from "@/components/signals/signals-page-content";

export const metadata: Metadata = {
  title: "Signals - Insique",
};

export default function SignalsPage() {
  return <SignalsPageContent />;
}
