import type { CurrentUserResponse, ResidentMembership, User, UserRole } from "@/types";

const PLATFORM_SUPER_ADMIN_ROLE: UserRole = {
  id: "platform-super-admin",
  code: "super_admin",
  name: "Super Admin",
  estate_id: "",
  estate_name: "Platform",
};

/** Normalize login and /me payloads into a consistent session shape. */
export function parseSessionPayload(data: unknown): CurrentUserResponse {
  if (!data || typeof data !== "object") {
    throw new Error("Invalid session response from server.");
  }

  const record = data as Record<string, unknown>;

  if (record.user && typeof record.user === "object") {
    return normalizeSession({
      user: record.user as User,
      roles: (record.roles as UserRole[] | undefined) ?? [],
      memberships: (record.memberships as ResidentMembership[] | undefined) ?? [],
      has_active_membership: Boolean(record.has_active_membership),
      pending_membership: Boolean(record.pending_membership),
    });
  }

  if (typeof record.id === "string" && typeof record.email === "string") {
    return normalizeSession({
      user: record as unknown as User,
      roles: [],
      memberships: [],
      has_active_membership: false,
      pending_membership: false,
    });
  }

  throw new Error("Unrecognized session response from server.");
}

/** Ensure platform superusers never inherit resident pending-approval state. */
export function normalizeSession(session: CurrentUserResponse): CurrentUserResponse {
  if (!session.user?.is_superuser) {
    return session;
  }

  const roles = (session.roles ?? []).some((role) => role.code === "super_admin")
    ? session.roles
    : [PLATFORM_SUPER_ADMIN_ROLE, ...(session.roles ?? [])];

  return {
    ...session,
    roles,
    has_active_membership: true,
    pending_membership: false,
  };
}

export function isPlatformSuperUser(
  user: { is_superuser?: boolean } | null | undefined,
  roles: UserRole[] | null | undefined,
): boolean {
  return Boolean(user?.is_superuser) || (roles ?? []).some((role) => role.code === "super_admin");
}
