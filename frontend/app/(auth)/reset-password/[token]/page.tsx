import { Metadata } from "next";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ResetPasswordForm } from "@/components/auth/reset-password-form";
import { Signal } from "lucide-react";

export const metadata: Metadata = {
  title: "Reset password - Insique",
};

export default async function ResetPasswordPage({
  params,
}: {
  params: Promise<{ token: string }>;
}) {
  const { token } = await params;

  return (
    <Card className="w-full max-w-sm">
      <CardHeader className="space-y-1 text-center">
        <div className="flex justify-center mb-2">
          <Signal className="h-8 w-8 text-primary" />
        </div>
        <CardTitle className="text-2xl">Reset password</CardTitle>
        <CardDescription>
          Enter your new password
        </CardDescription>
      </CardHeader>
      <CardContent>
        {token ? (
          <ResetPasswordForm token={token} />
        ) : (
          <p className="text-sm text-muted-foreground text-center">
            Invalid reset link.{" "}
            <a href="/forgot-password" className="font-medium text-primary hover:underline">
              Request a new one
            </a>
          </p>
        )}
      </CardContent>
    </Card>
  );
}
