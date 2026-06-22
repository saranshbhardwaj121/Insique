import { NextRequest } from "next/server";
import { forwardAuthenticatedRequest } from "@/lib/auth/authenticated-request";

export async function GET(request: NextRequest) {
  return forwardAuthenticatedRequest(request, "/portfolio/summary");
}
