import AsyncStorage from "@react-native-async-storage/async-storage";
import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

import { api, clearTokens, setTokens as persistTokens } from "@/lib/api";
import type { AuthTokens, LoginCredentials, User, UserRole } from "@/types";

interface AuthState {
  user: User | null;
  roles: UserRole[];
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  biometricEnabled: boolean;
  setUser: (user: User | null) => void;
  setRoles: (roles: UserRole[]) => void;
  setTokens: (tokens: AuthTokens) => Promise<void>;
  setBiometricEnabled: (enabled: boolean) => void;
  login: (credentials: LoginCredentials) => Promise<void>;
  fetchUser: () => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      roles: [],
      isAuthenticated: false,
      isLoading: false,
      error: null,
      biometricEnabled: false,

      setUser: (user) =>
        set({ user, isAuthenticated: !!user, error: null }),

      setRoles: (roles) => set({ roles }),

      setTokens: async (tokens) => {
        await persistTokens(tokens);
        set({ isAuthenticated: true, error: null });
      },

      setBiometricEnabled: (enabled) => set({ biometricEnabled: enabled }),

      login: async (credentials) => {
        set({ isLoading: true, error: null });
        try {
          const tokens = await api.login(credentials.email, credentials.password);
          await persistTokens(tokens);
          const user = await api.getCurrentUser();
          set({ user, isAuthenticated: true, isLoading: false });
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
          const user = await api.getCurrentUser();
          set({ user, isAuthenticated: true, isLoading: false, error: null });
        } catch {
          await clearTokens();
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },

      logout: async () => {
        await clearTokens();
        set({
          user: null,
          roles: [],
          isAuthenticated: false,
          error: null,
        });
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: "estateos-auth",
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        user: state.user,
        roles: state.roles,
        isAuthenticated: state.isAuthenticated,
        biometricEnabled: state.biometricEnabled,
      }),
    },
  ),
);
