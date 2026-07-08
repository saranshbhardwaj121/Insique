import { Metadata } from "next";
import { VerifyEmailHandler } from "./verify-email-handler";

export const metadata: Metadata = {
  title: "Verify email - Insique",
};

export default function Page({
  searchParams,
}: {
  searchParams: { token?: string };
}) {
  return <VerifyEmailHandler token={searchParams.token} />;
}
