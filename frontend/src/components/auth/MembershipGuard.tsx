"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { isPlatformSuperUser } from "@/lib/auth-session";
import { useAuthStore } from "@/stores/auth-store";

export function MembershipGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, hasActiveMembership, isLoading, pendingMembership, roles, user, hasRehydrated } =
    useAuthStore();
  const superAdmin = isPlatformSuperUser(user, roles);

  useEffect(() => {
    if (!hasRehydrated || isLoading || !isAuthenticated || superAdmin) return;
    if (hasActiveMembership) return;

    if (pendingMembership) {
      router.replace("/pending-approval");
      return;
    }

    router.replace("/login?reason=no-membership");
  }, [
    hasActiveMembership,
    pendingMembership,
    isAuthenticated,
    isLoading,
    hasRehydrated,
    router,
    superAdmin,
  ]);

  if (
    isAuthenticated &&
    !superAdmin &&
    !hasActiveMembership &&
    (pendingMembership || hasRehydrated)
  ) {
    return null;
  }

  return <>{children}</>;
}
