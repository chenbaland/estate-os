import { create } from "zustand";
import { persist } from "zustand/middleware";

import { api, clearTokens, getAccessToken, getRefreshToken, setTokens } from "@/lib/api";
import {
  getPostAuthDestination,
  logout as authLogout,
  resolveLoginDestination,
} from "@/lib/auth";
import { normalizeSession, parseSessionPayload } from "@/lib/auth-session";
import type {
  AuthSessionResponse,
  AuthTokens,
  CurrentUserResponse,
  LoginCredentials,
  ResidentMembership,
  User,
  UserRole,
} from "@/types";

interface AuthState {
  user: User | null;
  roles: UserRole[];
  memberships: ResidentMembership[];
  hasActiveMembership: boolean;
  pendingMembership: boolean;
  isAuthenticated: boolean;
  isLoading: boolean;
  hasRehydrated: boolean;
  error: string | null;
  setUser: (user: User | null) => void;
  setRoles: (roles: UserRole[]) => void;
  setMembershipState: (payload: Pick<
    CurrentUserResponse,
    "memberships" | "roles" | "has_active_membership" | "pending_membership"
  >) => void;
  setTokens: (tokens: AuthTokens) => void;
  applySession: (payload: CurrentUserResponse) => void;
  login: (credentials: LoginCredentials, redirectPath?: string | null) => Promise<string>;
  fetchUser: () => Promise<string>;
  logout: () => void;
  clearError: () => void;
}

function sessionFromAuthResponse(data: AuthSessionResponse): CurrentUserResponse | null {
  if (!data.user) return null;
  return parseSessionPayload(data);
}

function destinationFromState(
  state: Pick<AuthState, "hasActiveMembership" | "roles" | "user">,
): string {
  return getPostAuthDestination(state.hasActiveMembership, state.roles, state.user);
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      roles: [],
      memberships: [],
      hasActiveMembership: false,
      pendingMembership: false,
      isAuthenticated: false,
      isLoading: false,
      hasRehydrated: false,
      error: null,

      setUser: (user) =>
        set({ user, isAuthenticated: !!user, error: null }),

      setRoles: (roles) => set({ roles }),

      setMembershipState: (payload) =>
        set({
          memberships: payload.memberships,
          roles: payload.roles,
          hasActiveMembership: payload.has_active_membership,
          pendingMembership: payload.pending_membership,
        }),

      setTokens: (tokens) => {
        setTokens(tokens);
        set({ isAuthenticated: true, error: null });
      },

      applySession: (payload) => {
        const session = parseSessionPayload(payload);
        set({
          user: session.user ?? null,
          memberships: session.memberships ?? [],
          roles: session.roles ?? [],
          hasActiveMembership: session.has_active_membership,
          pendingMembership: session.pending_membership,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        });
      },

      login: async (credentials, redirectPath) => {
        set({ isLoading: true, error: null });
        try {
          const authData = await api.login(credentials.email, credentials.password);
          setTokens({ access: authData.access, refresh: authData.refresh });

          const session =
            sessionFromAuthResponse(authData) ?? (await api.getCurrentUser());
          get().applySession(session);
          return resolveLoginDestination(session, redirectPath);
        } catch (err) {
          const message =
            err instanceof Error ? err.message : "Login failed. Please try again.";
          set({ error: message, isLoading: false, isAuthenticated: false });
          throw err;
        }
      },

      fetchUser: async () => {
        set({ isLoading: true });
        try {
          const session = await api.getCurrentUser();
          get().applySession(session);
          return destinationFromState({
            hasActiveMembership: session.has_active_membership,
            roles: session.roles,
            user: session.user,
          });
        } catch {
          clearTokens();
          set({
            user: null,
            roles: [],
            memberships: [],
            hasActiveMembership: false,
            pendingMembership: false,
            isAuthenticated: false,
            isLoading: false,
          });
          return "/login";
        }
      },

      logout: () => {
        clearTokens();
        set({
          user: null,
          roles: [],
          memberships: [],
          hasActiveMembership: false,
          pendingMembership: false,
          isAuthenticated: false,
          error: null,
        });
        authLogout();
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: "estateos-auth",
      skipHydration: true,
      partialize: (state) => ({
        user: state.user,
        roles: state.roles,
        memberships: state.memberships,
        hasActiveMembership: state.hasActiveMembership,
        pendingMembership: state.pendingMembership,
        isAuthenticated: state.isAuthenticated,
      }),
      merge: (persistedState, currentState) => {
        const persisted = persistedState as Partial<AuthState> | undefined;
        return {
          ...currentState,
          ...persisted,
          roles: persisted?.roles ?? [],
          memberships: persisted?.memberships ?? [],
        };
      },
      onRehydrateStorage: () => (_state, error) => {
        if (error) {
          useAuthStore.setState({
            hasRehydrated: true,
            isLoading: false,
            isAuthenticated: false,
            user: null,
            roles: [],
            memberships: [],
            hasActiveMembership: false,
            pendingMembership: false,
          });
          return;
        }

        const state = useAuthStore.getState();
        const access = getAccessToken();
        const refresh = getRefreshToken();

        if (access && refresh) {
          setTokens({ access, refresh });
        } else if (state.isAuthenticated) {
          clearTokens();
          useAuthStore.setState({
            user: null,
            roles: [],
            memberships: [],
            hasActiveMembership: false,
            pendingMembership: false,
            isAuthenticated: false,
            hasRehydrated: true,
            isLoading: false,
          });
          return;
        }

        const persistedUser = state.user;
        const persistedRoles = state.roles ?? [];
        const superUser = Boolean(persistedUser?.is_superuser);

        useAuthStore.setState({
          hasRehydrated: true,
          isLoading: Boolean(state.isAuthenticated && access && refresh),
          ...(superUser
            ? {
                hasActiveMembership: true,
                pendingMembership: false,
                roles: persistedRoles.some((role) => role.code === "super_admin")
                  ? persistedRoles
                  : [
                      {
                        id: "platform-super-admin",
                        code: "super_admin" as const,
                        name: "Super Admin",
                        estate_id: "",
                        estate_name: "Platform",
                      },
                      ...persistedRoles,
                    ],
              }
            : {}),
        });
      },
    },
  ),
);
