import { NextRequest } from "next/server";
import { forwardAuthenticatedRequest } from "@/lib/auth/authenticated-request";

export async function GET(request: NextRequest) {
  return forwardAuthenticatedRequest(request, "/portfolio/holdings");
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  return forwardAuthenticatedRequest(request, "/portfolio/holdings", {
    method: "POST",
    body: JSON.stringify(body),
  });
}
