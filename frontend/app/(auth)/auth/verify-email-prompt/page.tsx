import { Metadata } from "next";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Mail } from "lucide-react";

export const metadata: Metadata = {
  title: "Check your email - Insique",
};

export default function VerifyEmailPromptPage() {
  return (
    <Card className="w-full max-w-sm">
      <CardHeader className="space-y-1 text-center">
        <div className="flex justify-center mb-2">
          <Mail className="h-12 w-12 text-primary" />
        </div>
        <CardTitle className="text-2xl">Check your email</CardTitle>
        <CardDescription>
          We&apos;ve sent a verification link to your email address.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4 text-center">
        <p className="text-sm text-muted-foreground">
          Click the link in the email to verify your account. The link expires in 24 hours.
        </p>
        <div className="space-y-2">
          <Button variant="outline" className="w-full" asChild>
            <a href="https://gmail.com" target="_blank" rel="noopener noreferrer">
              Open Gmail
            </a>
          </Button>
          <Button variant="outline" className="w-full" asChild>
            <Link href="/login">Back to login</Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
