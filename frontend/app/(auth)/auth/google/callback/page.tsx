import { GoogleCallbackHandler } from "./callback-handler";

export default function Page({
  searchParams,
}: {
  searchParams: { code?: string; error?: string };
}) {
  return <GoogleCallbackHandler code={searchParams.code} />;
}
