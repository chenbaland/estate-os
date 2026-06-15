import type {
  AuthSessionResponse,
  AuthTokens,
  BlacklistEntry,
  CreateVisitorPassPayload,
  CurrentUserResponse,
  DebtRecord,
  Invoice,
  PaginatedResponse,
  Payment,
  PublicEstate,
  PublicUnit,
  RegisterPayload,
  ResidentProfile,
  Unit,
  User,
  VisitorLog,
  VisitorPass,
} from "@/types";

import { parseSessionPayload } from "@/lib/auth-session";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

const ACCESS_TOKEN_KEY = "estateos_access_token";
const REFRESH_TOKEN_KEY = "estateos_refresh_token";
const ESTATE_ID_KEY = "estateos_estate_id";

export class ApiClientError extends Error {
  status: number;
  data: unknown;

  constructor(message: string, status: number, data?: unknown) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.data = data;
  }
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function getEstateId(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ESTATE_ID_KEY);
}

export function setTokens(tokens: AuthTokens): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh);
  document.cookie = `estateos-access=${tokens.access}; path=/; max-age=3600; SameSite=Lax`;
}

export function clearTokens(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  document.cookie =
    "estateos-access=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
}

export function setEstateId(estateId: string | null): void {
  if (typeof window === "undefined") return;
  if (estateId) {
    localStorage.setItem(ESTATE_ID_KEY, estateId);
  } else {
    localStorage.removeItem(ESTATE_ID_KEY);
  }
}

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refresh = getRefreshToken();
  if (!refresh) return null;

  const response = await fetch(`${API_URL}/accounts/auth/token/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });

  if (!response.ok) {
    clearTokens();
    return null;
  }

  const data = (await response.json()) as { access: string };
  localStorage.setItem(ACCESS_TOKEN_KEY, data.access);
  document.cookie = `estateos-access=${data.access}; path=/; max-age=3600; SameSite=Lax`;
  return data.access;
}

async function getValidAccessToken(): Promise<string | null> {
  const token = getAccessToken();
  if (token) return token;

  if (!refreshPromise) {
    refreshPromise = refreshAccessToken().finally(() => {
      refreshPromise = null;
    });
  }

  return refreshPromise;
}

interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  auth?: boolean;
  estateScoped?: boolean;
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { body, auth = true, estateScoped = true, headers, ...rest } = options;

  const requestHeaders = new Headers(headers);
  requestHeaders.set("Content-Type", "application/json");

  if (auth) {
    const token = await getValidAccessToken();
    if (token) {
      requestHeaders.set("Authorization", `Bearer ${token}`);
    }
  }

  if (estateScoped) {
    const estateId = getEstateId();
    if (estateId) {
      requestHeaders.set("X-Estate-Id", estateId);
    }
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...rest,
    headers: requestHeaders,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (response.status === 401 && auth) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      requestHeaders.set("Authorization", `Bearer ${newToken}`);
      const retry = await fetch(`${API_URL}${path}`, {
        ...rest,
        headers: requestHeaders,
        body: body !== undefined ? JSON.stringify(body) : undefined,
      });
      if (!retry.ok) {
        throw await buildError(retry);
      }
      if (retry.status === 204) return undefined as T;
      return retry.json() as Promise<T>;
    }
    clearTokens();
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
    throw await buildError(response);
  }

  if (!response.ok) {
    throw await buildError(response);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

async function buildError(response: Response): Promise<ApiClientError> {
  let data: unknown;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (data && typeof data === "object" && !Array.isArray(data)) {
    const record = data as Record<string, unknown>;
    if (typeof record.detail === "string") {
      return new ApiClientError(record.detail, response.status, data);
    }
    const fieldMessages = Object.entries(record)
      .map(([field, value]) => {
        if (Array.isArray(value)) {
          return `${field}: ${value.join(", ")}`;
        }
        if (typeof value === "string") {
          return `${field}: ${value}`;
        }
        return null;
      })
      .filter(Boolean);
    if (fieldMessages.length > 0) {
      return new ApiClientError(fieldMessages.join(" · "), response.status, data);
    }
  }

  const message =
    (data as { detail?: string })?.detail ??
    (data as { message?: string })?.message ??
    `Request failed with status ${response.status}`;

  return new ApiClientError(message, response.status, data);
}

function buildQuery(params?: Record<string, string | undefined>): string {
  if (!params) return "";
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value) search.set(key, value);
  }
  const query = search.toString();
  return query ? `?${query}` : "";
}

export const api = {
  login: (email: string, password: string) =>
    apiRequest<AuthSessionResponse>("/accounts/auth/token/", {
      method: "POST",
      body: { email, password },
      auth: false,
      estateScoped: false,
    }),

  register: (payload: RegisterPayload) =>
    apiRequest<AuthSessionResponse & { user: User }>("/accounts/auth/register/", {
      method: "POST",
      body: payload,
      auth: false,
      estateScoped: false,
    }),

  getOAuthAuthorizeUrl: (provider: "google" | "apple") =>
    apiRequest<{ authorization_url: string }>(
      `/accounts/auth/oauth/${provider}/authorize/`,
      { method: "GET", auth: false, estateScoped: false },
    ),

  oauthCallback: (provider: "google" | "apple", payload: { code?: string; id_token?: string; identity_token?: string }) =>
    apiRequest<AuthSessionResponse>(
      `/accounts/auth/oauth/${provider}/callback/`,
      { method: "POST", body: payload, auth: false, estateScoped: false },
    ),

  getCurrentUser: async () =>
    parseSessionPayload(
      await apiRequest<CurrentUserResponse>("/accounts/me/", {
        method: "GET",
        estateScoped: false,
      }),
    ),

  getPublicEstates: () =>
    apiRequest<{ results: PublicEstate[] }>("/estates/public/", {
      method: "GET",
      auth: false,
      estateScoped: false,
    }),

  getPublicUnits: (estateId: string) =>
    apiRequest<{ results: PublicUnit[] }>(`/estates/public/${estateId}/units/`, {
      method: "GET",
      auth: false,
      estateScoped: false,
    }),

  getResidentProfiles: (params?: { status?: string }) => {
    const query = params?.status ? `?status=${encodeURIComponent(params.status)}` : "";
    return apiRequest<{ results: ResidentProfile[] }>(`/residents/profiles${query}`, {
      method: "GET",
    });
  },

  activateResidentProfile: (
    profileId: string,
    unitId: string,
    residentType: "owner" | "tenant",
  ) =>
    apiRequest<ResidentProfile>(`/residents/profiles/${profileId}/activate/`, {
      method: "POST",
      body: { unit_id: unitId, resident_type: residentType },
    }),

  rejectResidentProfile: (profileId: string, reason?: string) =>
    apiRequest<ResidentProfile>(`/residents/profiles/${profileId}/reject/`, {
      method: "POST",
      body: reason ? { reason } : {},
    }),

  getEstates: () =>
    apiRequest<{ results: import("@/types").Estate[] }>("/estates/", {
      method: "GET",
    }),

  getUnits: () =>
    apiRequest<{ results: Unit[] }>("/estates/units/", {
      method: "GET",
    }),

  getPlatformOverview: () =>
    apiRequest<import("@/types").PlatformOverview>("/platform/overview/", {
      method: "GET",
      estateScoped: false,
    }),

  getPlatformEstates: () =>
    apiRequest<{ results: import("@/types").PlatformEstate[] }>("/platform/estates/", {
      method: "GET",
      estateScoped: false,
    }),

  createPlatformEstate: (payload: import("@/types").CreatePlatformEstatePayload) =>
    apiRequest<import("@/types").PlatformEstate>("/platform/estates/", {
      method: "POST",
      body: payload,
      estateScoped: false,
    }),

  updatePlatformEstate: (
    estateId: string,
    payload: import("@/types").UpdatePlatformEstatePayload,
  ) =>
    apiRequest<import("@/types").PlatformEstate>(`/platform/estates/${estateId}/`, {
      method: "PATCH",
      body: payload,
      estateScoped: false,
    }),

  deactivatePlatformEstate: (estateId: string) =>
    apiRequest<import("@/types").PlatformEstate>(
      `/platform/estates/${estateId}/deactivate/`,
      { method: "POST", estateScoped: false },
    ),

  activatePlatformEstate: (estateId: string) =>
    apiRequest<import("@/types").PlatformEstate>(
      `/platform/estates/${estateId}/activate/`,
      { method: "POST", estateScoped: false },
    ),

  getPlatformAuditLogs: () =>
    apiRequest<{ results: import("@/types").PlatformAuditLog[] }>(
      "/platform/audit-logs/",
      { method: "GET", estateScoped: false },
    ),

  getPlatformAdmins: () =>
    apiRequest<{ results: import("@/types").PlatformAdminAssignment[] }>(
      "/platform/admins/",
      { method: "GET", estateScoped: false },
    ),

  assignPlatformAdmin: (payload: import("@/types").AssignPlatformAdminPayload) =>
    apiRequest<import("@/types").PlatformAdminAssignment>("/platform/admins/", {
      method: "POST",
      body: payload,
      estateScoped: false,
    }),

  revokePlatformAdmin: (assignmentId: string) =>
    apiRequest<void>(`/platform/admins/${assignmentId}/`, {
      method: "DELETE",
      estateScoped: false,
    }),

  getInvoices: (params?: { status?: string; resident?: string }) =>
    apiRequest<PaginatedResponse<Invoice>>(`/billing/invoices/${buildQuery(params)}`, {
      method: "GET",
    }),

  payInvoice: (invoiceId: string, payload?: { amount?: string; method?: string }) =>
    apiRequest<Payment>(`/billing/invoices/${invoiceId}/pay/`, {
      method: "POST",
      body: payload ?? {},
    }),

  getPayments: (params?: { status?: string; invoice?: string }) =>
    apiRequest<PaginatedResponse<Payment>>(`/billing/payments/${buildQuery(params)}`, {
      method: "GET",
    }),

  getDebtRecords: (params?: { status?: string }) =>
    apiRequest<PaginatedResponse<DebtRecord>>(`/billing/debts/${buildQuery(params)}`, {
      method: "GET",
    }),

  getVisitorPasses: (params?: { host?: string; status?: string }) =>
    apiRequest<PaginatedResponse<VisitorPass>>(`/visitors/passes/${buildQuery(params)}`, {
      method: "GET",
    }),

  createVisitorPass: (payload: CreateVisitorPassPayload) =>
    apiRequest<VisitorPass>("/visitors/passes/", {
      method: "POST",
      body: payload,
    }),

  revokeVisitorPass: (passId: string) =>
    apiRequest<VisitorPass>(`/visitors/passes/${passId}/`, {
      method: "PATCH",
      body: { status: "revoked" },
    }),

  getVisitorLogs: (params?: { direction?: string }) =>
    apiRequest<PaginatedResponse<VisitorLog>>(`/visitors/logs/${buildQuery(params)}`, {
      method: "GET",
    }),

  logout: (refresh: string) =>
    apiRequest<void>("/accounts/auth/logout/", {
      method: "POST",
      body: { refresh },
    }),

  updateCurrentUser: (payload: { first_name?: string; last_name?: string; phone?: string; preferred_language?: string }) =>
    apiRequest<import("@/types").User>("/accounts/me/", {
      method: "PATCH",
      body: payload,
      estateScoped: false,
    }),

  getNotifications: (params?: { status?: string }) =>
    apiRequest<PaginatedResponse<import("@/types").Notification>>(
      `/notifications/notifications/${buildQuery(params)}`,
      { method: "GET" },
    ),

  markNotificationRead: (notifId: string) =>
    apiRequest<import("@/types").Notification>(`/notifications/notifications/${notifId}/mark_read/`, {
      method: "POST",
      body: {},
    }),

  markAllNotificationsRead: () =>
    apiRequest<{ marked_read: number }>("/notifications/notifications/mark_all_read/", {
      method: "POST",
      body: {},
    }),

  getBlacklist: (params?: { is_active?: string }) =>
    apiRequest<PaginatedResponse<BlacklistEntry>>(`/visitors/blacklist/${buildQuery(params)}`, {
      method: "GET",
    }),
};

export { API_URL };
