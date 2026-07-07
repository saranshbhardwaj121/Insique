import { GoogleCallbackHandler } from "./callback-handler";

export default function Page({
  searchParams,
}: {
  searchParams: { code?: string };
}) {
  return <GoogleCallbackHandler code={searchParams.code} />;
}
