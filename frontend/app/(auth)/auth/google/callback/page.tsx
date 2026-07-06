"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2 } from "lucide-react";
import { API_ROUTES } from "@/lib/api/routes";
import { clientFetch, ApiError } from "@/lib/api/client";

export default function GoogleCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const code = searchParams.get("code");

    if (!code) {
      setError("Missing authentication code.");
      return;
    }

    async function exchangeCode() {
      try {
        await clientFetch<{ success: boolean }>(API_ROUTES.AUTH.GOOGLE_CALLBACK, {
          method: "POST",
          body: JSON.stringify({ code }),
        });
        router.push("/dashboard");
      } catch (err) {
        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError("Authentication failed. Please try again.");
        }
        setTimeout(() => router.push("/login"), 3000);
      }
    }

    exchangeCode();
  }, [searchParams, router]);

  if (error) {
    return (
      <div className="flex flex-col items-center gap-4 text-center">
        <p className="text-sm text-destructive">{error}</p>
        <p className="text-xs text-muted-foreground">Redirecting to login...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center gap-4 text-center">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
      <p className="text-sm text-muted-foreground">Completing sign in...</p>
    </div>
  );
}
