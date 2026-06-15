import { Suspense } from "react";

import OAuthCallbackContent from "./callback-content";

export default function OAuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center text-muted-foreground">
          Completing sign in…
        </div>
      }
    >
      <OAuthCallbackContent />
    </Suspense>
  );
}
