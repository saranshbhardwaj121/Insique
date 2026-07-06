import { NextRequest, NextResponse } from "next/server";
import { serverFetch, ApiError } from "@/lib/api/client";
import { API_ROUTES } from "@/lib/api/routes";
import { setAuthCookies } from "@/lib/auth/session";
import type { AuthTokens } from "@/features/auth/types";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const code = body?.code;

    if (!code || typeof code !== "string") {
      return NextResponse.json({ detail: "Missing session code" }, { status: 400 });
    }

    const tokens = await serverFetch<AuthTokens>(API_ROUTES.AUTH.GOOGLE_CALLBACK, {
      method: "POST",
      body: JSON.stringify({ code }),
    });

    const response = NextResponse.json({ success: true });
    setAuthCookies(response, tokens.access_token, tokens.refresh_token);
    return response;
  } catch (error) {
    if (error instanceof ApiError) {
      return NextResponse.json(
        { detail: error.message },
        { status: error.statusCode }
      );
    }
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
