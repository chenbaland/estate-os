import { api, clearTokens, getRefreshToken, setTokens } from "@/lib/api";
import type { LoginCredentials, RegisterPayload, RoleCode, User, UserRole } from "@/types";

export const PUBLIC_ROUTES = ["/", "/login", "/register"] as const;
export const PENDING_AUTH_ROUTES = ["/pending-approval"] as const;

export const PROTECTED_ROUTE_PREFIXES = [
  "/dashboard",
  "/residents",
  "/visitors",
  "/security",
  "/billing",
  "/utilities",
  "/marketplace",
  "/pharmacy",
  "/healthcare",
  "/facilities",
  "/maintenance",
  "/packages",
  "/parking",
  "/community",
  "/transportation",
  "/analytics",
  "/ai-concierge",
  "/settings",
  "/platform",
] as const;

export function isPublicRoute(pathname: string): boolean {
  return PUBLIC_ROUTES.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`),
  );
}

export function isProtectedRoute(pathname: string): boolean {
  return PROTECTED_ROUTE_PREFIXES.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`),
  );
}

export function isSafeRedirectPath(path: string | null | undefined): path is string {
  if (!path || !path.startsWith("/") || path.startsWith("//")) {
    return false;
  }
  return isProtectedRoute(path);
}

export async function login(credentials: LoginCredentials) {
  const tokens = await api.login(credentials.email, credentials.password);
  setTokens(tokens);
  return tokens;
}

export async function register(payload: RegisterPayload) {
  return api.register(payload);
}

export async function logout(): Promise<void> {
  const refresh = getRefreshToken();
  // Best-effort: blacklist the refresh token on the backend before clearing local state
  if (refresh) {
    try {
      await api.logout(refresh);
    } catch {
      // Ignore errors — local logout proceeds regardless
    }
  }
  clearTokens();
  if (typeof window !== "undefined") {
    window.location.href = "/login";
  }
}

export function getUserDisplayName(user: User | null): string {
  if (!user) return "Guest";
  const name = [user.first_name, user.last_name].filter(Boolean).join(" ");
  return name || user.email;
}

export function hasRole(roles: UserRole[], codes: RoleCode[]): boolean {
  return roles.some((r) => codes.includes(r.code));
}

export function isSuperAdmin(roles: UserRole[], user: User | null): boolean {
  return Boolean(user?.is_superuser) || roles.some((r) => r.code === "super_admin");
}

export function isPlatformSuperUser(user: User | null, roles: UserRole[]): boolean {
  return isSuperAdmin(roles, user);
}

export const ROLE_LABELS: Record<RoleCode, string> = {
  super_admin: "Super Admin",
  estate_admin: "Estate Admin",
  finance_admin: "Finance Admin",
  security_admin: "Security Admin",
  facility_admin: "Facility Admin",
  resident: "Resident",
  vendor: "Vendor",
  technician: "Technician",
  security_personnel: "Security Personnel",
};

export function resolveLoginDestination(
  session: { user: User | null; roles: UserRole[]; has_active_membership: boolean },
  redirectTo?: string | null,
): string {
  return getPostAuthDestination(session.has_active_membership, session.roles, session.user, redirectTo);
}

export function getPostAuthDestination(
  hasActiveMembership: boolean,
  roles: UserRole[],
  user: User | null,
  redirectTo?: string | null,
): string {
  if (isSuperAdmin(roles, user)) return "/platform";
  if (hasActiveMembership) {
    if (redirectTo && isSafeRedirectPath(redirectTo)) return redirectTo;
    return "/dashboard";
  }
  return "/pending-approval";
}
