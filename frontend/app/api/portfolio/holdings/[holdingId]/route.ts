import { NextRequest } from "next/server";
import { forwardAuthenticatedRequest } from "@/lib/auth/authenticated-request";

export async function PATCH(
  request: NextRequest,
  { params }: { params: { holdingId: string } }
) {
  const body = await request.json();
  return forwardAuthenticatedRequest(request, `/portfolio/holdings/${params.holdingId}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { holdingId: string } }
) {
  return forwardAuthenticatedRequest(request, `/portfolio/holdings/${params.holdingId}`, {
    method: "DELETE",
  });
}
