"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, CheckCircle2, AlertCircle, Clock, Mail } from "lucide-react";
import { verifyEmail, resendVerification } from "@/features/auth/api";
import { ApiError } from "@/lib/api/errors";

type State = "loading" | "success" | "expired" | "invalid" | "already-verified" | "error";

export function VerifyEmailHandler({ token }: { token?: string }) {
  const router = useRouter();
  const [state, setState] = useState<State>("loading");
  const [message, setMessage] = useState<string>("");
  const [resending, setResending] = useState(false);
  const [resendSent, setResendSent] = useState(false);

  useEffect(() => {
    if (!token) {
      setState("invalid");
      setMessage("No verification token provided.");
      return;
    }

    const tokenValue = token;

    async function verify() {
      try {
        const result = await verifyEmail(tokenValue);
        setState("success");
        setMessage(result.message);
      } catch (err) {
        if (err instanceof ApiError) {
          const detail = err.message.toLowerCase();
          if (detail.includes("expired") || detail.includes("24 hours")) {
            setState("expired");
            setMessage(err.message);
          } else if (detail.includes("already verified")) {
            setState("already-verified");
            setMessage(err.message);
          } else {
            setState("invalid");
            setMessage(err.message);
          }
        } else {
          setState("error");
          setMessage("An unexpected error occurred.");
        }
      }
    }

    verify();
  }, [token]);

  const handleResend = async () => {
    setResending(true);
    try {
      await resendVerification();
      setResendSent(true);
    } catch (err) {
      if (err instanceof ApiError) {
        setMessage(err.message);
      }
    } finally {
      setResending(false);
    }
  };

  if (state === "loading") {
    return (
      <Card className="w-full max-w-sm">
        <CardContent className="pt-6 text-center">
          <Loader2 className="mx-auto h-8 w-8 animate-spin text-primary" />
          <p className="mt-4 text-sm text-muted-foreground">Verifying your email...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-sm">
      <CardHeader className="space-y-1 text-center">
        <div className="flex justify-center mb-2">
          {state === "success" && <CheckCircle2 className="h-12 w-12 text-green-500" />}
          {state === "expired" && <Clock className="h-12 w-12 text-amber-500" />}
          {state === "invalid" && <AlertCircle className="h-12 w-12 text-red-500" />}
          {state === "already-verified" && <CheckCircle2 className="h-12 w-12 text-blue-500" />}
          {state === "error" && <AlertCircle className="h-12 w-12 text-red-500" />}
        </div>
        <CardTitle className="text-2xl">
          {state === "success" && "Email verified!"}
          {state === "expired" && "Link expired"}
          {state === "invalid" && "Invalid link"}
          {state === "already-verified" && "Already verified"}
          {state === "error" && "Something went wrong"}
        </CardTitle>
        <CardDescription>{message}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {state === "success" && (
          <Button className="w-full" onClick={() => router.push("/login")}>
            Continue to login
          </Button>
        )}
        {state === "expired" && (
          <>
            {resendSent ? (
              <div className="text-center space-y-3">
                <Mail className="mx-auto h-8 w-8 text-primary" />
                <p className="text-sm text-muted-foreground">
                  A new verification link has been sent to your email.
                </p>
                <Button variant="outline" className="w-full" asChild>
                  <Link href="/login">Back to login</Link>
                </Button>
              </div>
            ) : (
              <Button className="w-full" onClick={handleResend} disabled={resending}>
                {resending ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Sending...</>
                ) : (
                  "Resend verification email"
                )}
              </Button>
            )}
          </>
        )}
        {state === "invalid" && (
          <Button variant="outline" className="w-full" asChild>
            <Link href="/login">Back to login</Link>
          </Button>
        )}
        {state === "already-verified" && (
          <Button className="w-full" onClick={() => router.push("/login")}>
            Continue to login
          </Button>
        )}
        {state === "error" && (
          <Button variant="outline" className="w-full" asChild>
            <Link href="/login">Back to login</Link>
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
