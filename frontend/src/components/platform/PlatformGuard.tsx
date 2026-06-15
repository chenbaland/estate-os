"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { PlatformLoadingFallback } from "@/components/platform/PlatformLoadingFallback";
import { useAuth } from "@/hooks/useAuth";
import { isSuperAdmin } from "@/lib/auth";
import { useAuthStore } from "@/stores/auth-store";

export function PlatformGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const hasRehydrated = useAuthStore((state) => state.hasRehydrated);
  const { user, roles, isAuthenticated, isSessionLoading } = useAuth();
  const superAdmin = isSuperAdmin(roles, user);

  useEffect(() => {
    if (!hasRehydrated || isSessionLoading) return;

    if (!isAuthenticated) {
      router.replace("/login?redirect=/platform");
      return;
    }

    if (!superAdmin) {
      router.replace("/dashboard");
    }
  }, [hasRehydrated, isAuthenticated, isSessionLoading, router, superAdmin]);

  if (superAdmin) {
    return <>{children}</>;
  }

  if (!hasRehydrated || isSessionLoading) {
    return <PlatformLoadingFallback />;
  }

  return null;
}
