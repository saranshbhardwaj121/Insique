import { Suspense } from "react";
import { GoogleCallbackHandler } from "./callback-handler";

export default function Page() {
  return (
    <Suspense
      fallback={
        <div className="flex flex-col items-center gap-4 text-center">
          <p className="text-sm text-muted-foreground">Completing sign in...</p>
        </div>
      }
    >
      <GoogleCallbackHandler />
    </Suspense>
  );
}
