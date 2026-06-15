"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";

import { useAuth } from "@/hooks/useAuth";
import { isSuperAdmin } from "@/lib/auth";

/** Routes super admins can use outside /platform (also linked from platform sidebar). */
const SUPER_ADMIN_ESTATE_ROUTES = ["/settings", "/analytics"] as const;

function isSuperAdminAllowedPath(pathname: string): boolean {
  if (pathname.startsWith("/platform")) return true;
  return SUPER_ADMIN_ESTATE_ROUTES.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`),
  );
}

export function SuperAdminRedirect() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, roles, isLoading, isAuthenticated } = useAuth();

  useEffect(() => {
    if (isLoading || !isAuthenticated || !user) return;
    if (isSuperAdminAllowedPath(pathname)) return;
    if (isSuperAdmin(roles, user)) {
      router.replace("/platform");
    }
  }, [isAuthenticated, isLoading, pathname, roles, router, user]);

  return null;
}
