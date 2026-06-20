import { Nav } from "@/components/landing/nav";
import { Hero } from "@/components/landing/hero";
import { SocialProof } from "@/components/landing/social-proof";
import { LiveTicker } from "@/components/landing/live-ticker";
import { InteractiveShowcase } from "@/components/landing/interactive-showcase";
import { HowItWorks } from "@/components/landing/how-it-works";
import { CapabilitiesGrid } from "@/components/landing/capabilities-grid";
import { EvidenceSection } from "@/components/landing/evidence-section";
import { FutureVision } from "@/components/landing/future-vision";
import { FAQ } from "@/components/landing/faq";
import { FinalCTA } from "@/components/landing/final-cta";
import { Footer } from "@/components/landing/footer";

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Nav />
      <main>
        <Hero />
        <SocialProof />
        <LiveTicker />
        <InteractiveShowcase />
        <HowItWorks />
        <CapabilitiesGrid />
        <EvidenceSection />
        <FutureVision />
        <FAQ />
        <FinalCTA />
      </main>
      <Footer />
    </div>
  );
}
