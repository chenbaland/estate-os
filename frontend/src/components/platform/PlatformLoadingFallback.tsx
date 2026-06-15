import { Skeleton } from "@/components/ui/skeleton";

export function PlatformLoadingFallback() {
  return (
    <div className="space-y-6" aria-busy="true" aria-label="Loading platform console">
      <Skeleton className="h-4 w-full max-w-xl" />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {Array.from({ length: 6 }).map((_, index) => (
          <Skeleton key={index} className="h-24 w-full rounded-xl" />
        ))}
      </div>
    </div>
  );
}
