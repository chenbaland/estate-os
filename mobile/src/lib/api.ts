import * as SecureStore from "expo-secure-store";

import type { AuthTokens, RegisterPayload, User } from "@/types";

const API_URL =
  process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

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

export async function getAccessToken(): Promise<string | null> {
  return SecureStore.getItemAsync(ACCESS_TOKEN_KEY);
}

export async function getRefreshToken(): Promise<string | null> {
  return SecureStore.getItemAsync(REFRESH_TOKEN_KEY);
}

export async function getEstateId(): Promise<string | null> {
  return SecureStore.getItemAsync(ESTATE_ID_KEY);
}

export async function setTokens(tokens: AuthTokens): Promise<void> {
  await SecureStore.setItemAsync(ACCESS_TOKEN_KEY, tokens.access);
  await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, tokens.refresh);
}

export async function clearTokens(): Promise<void> {
  await SecureStore.deleteItemAsync(ACCESS_TOKEN_KEY);
  await SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
}

export async function setEstateId(estateId: string | null): Promise<void> {
  if (estateId) {
    await SecureStore.setItemAsync(ESTATE_ID_KEY, estateId);
  } else {
    await SecureStore.deleteItemAsync(ESTATE_ID_KEY);
  }
}

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refresh = await getRefreshToken();
  if (!refresh) return null;

  const response = await fetch(`${API_URL}/accounts/auth/token/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });

  if (!response.ok) {
    await clearTokens();
    return null;
  }

  const data = (await response.json()) as { access: string };
  await SecureStore.setItemAsync(ACCESS_TOKEN_KEY, data.access);
  return data.access;
}

async function getValidAccessToken(): Promise<string | null> {
  const token = await getAccessToken();
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
    const estateId = await getEstateId();
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
    await clearTokens();
    throw new ApiClientError("Session expired", 401);
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

  const message =
    (data as { detail?: string })?.detail ??
    (data as { message?: string })?.message ??
    (data as { title?: string })?.title ??
    `Request failed with status ${response.status}`;

  return new ApiClientError(message, response.status, data);
}

export const api = {
  login: (email: string, password: string) =>
    apiRequest<AuthTokens>("/accounts/auth/token/", {
      method: "POST",
      body: { email, password },
      auth: false,
      estateScoped: false,
    }),

  register: (payload: RegisterPayload) =>
    apiRequest<User>("/accounts/register/", {
      method: "POST",
      body: payload,
      auth: false,
      estateScoped: false,
    }),

  getCurrentUser: () =>
    apiRequest<User>("/accounts/me/", { method: "GET", estateScoped: false }),

  getEstates: () =>
    apiRequest<{ results: import("@/types").Estate[] }>("/estates/", {
      method: "GET",
    }),

  getVisitors: () =>
    apiRequest<{ results: import("@/types").VisitorPass[] }>("/visitors/", {
      method: "GET",
    }),

  createVisitorPass: (payload: {
    visitor_name: string;
    visitor_phone: string;
    purpose: string;
    valid_until: string;
  }) =>
    apiRequest<import("@/types").VisitorPass>("/visitors/", {
      method: "POST",
      body: payload,
    }),

  scanVisitorPass: (qrCode: string) =>
    apiRequest<import("@/types").VisitorPass>("/visitors/scan/", {
      method: "POST",
      body: { qr_code: qrCode },
    }),

  getBillingInvoices: () =>
    apiRequest<{ results: import("@/types").BillingInvoice[] }>("/billing/invoices/", {
      method: "GET",
    }),

  getFacilities: () =>
    apiRequest<{ results: import("@/types").Facility[] }>("/facilities/", {
      method: "GET",
    }),

  bookFacility: (payload: {
    facility_id: string;
    start_time: string;
    end_time: string;
  }) =>
    apiRequest<{ id: string }>("/facilities/bookings/", {
      method: "POST",
      body: payload,
    }),

  createMaintenanceRequest: (payload: {
    title: string;
    description: string;
    category: string;
    priority: string;
  }) =>
    apiRequest<import("@/types").MaintenanceRequest>("/maintenance/requests/", {
      method: "POST",
      body: payload,
    }),

  sendChatMessage: (message: string) =>
    apiRequest<{ reply: string }>("/ai/chat/", {
      method: "POST",
      body: { message },
    }),

  triggerSOS: (payload: { location?: string; message?: string }) =>
    apiRequest<{ id: string }>("/security/sos/", {
      method: "POST",
      body: payload,
    }),

  registerPushToken: (token: string, platform: string) =>
    apiRequest<void>("/notifications/devices/", {
      method: "POST",
      body: { token, platform },
    }),
};

export { API_URL };
