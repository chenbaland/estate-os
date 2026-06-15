import { Suspense } from "react";

import PlatformEstatesContent from "./estates-content";

export default function PlatformEstatesPage() {
  return (
    <Suspense fallback={<p className="text-sm text-muted-foreground">Loading estates…</p>}>
      <PlatformEstatesContent />
    </Suspense>
  );
}
